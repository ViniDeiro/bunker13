#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameSession.h"
#include "Components/CapsuleComponent.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Hash/Blake3.h"
#include "Misc/SecureHash.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

namespace
{
bool HexTicket(const FString& Ticket)
{
    if (Ticket.Len()!=64) return false;
    for (TCHAR C:Ticket) if (!FChar::IsHexDigit(C)) return false;
    return true;
}
FString HashTicket(const FString& Ticket)
{
    FTCHARToUTF8 Bytes(*Ticket);
    return LexToString(FBlake3::HashBuffer(Bytes.Get(),Bytes.Length()));
}
FString ProfileSlot()
{
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest")))
    {
        int32 Index=0;FParse::Value(FCommandLine::Get(),TEXT("C13ReconnectProfile="),Index);
        return FString::Printf(TEXT("C13_TestReconnectProfile_%d"),FMath::Clamp(Index,0,8));
    }
#endif
    return TEXT("C13_ReconnectProfile");
}
bool ValidProfile(UBunkerReconnectProfile* P)
{
    if (!P || P->Version!=1 || P->Generation<1 || P->Generation>=MAX_int64-1 || P->Tickets.Num()>32) return false;
    for (const auto& Pair:P->Tickets) {FGuid Id;if (!FGuid::Parse(Pair.Key,Id) || !Id.IsValid() || !HexTicket(Pair.Value)) return false;}
    return true;
}
UBunkerReconnectProfile* ReadProfileSlot(const FString& Slot)
{
    TArray<uint8> Bytes;
    if (!UGameplayStatics::LoadDataFromSlot(Bytes,Slot,0) || Bytes.Num()<21 || Bytes.Num()>256*1024) return nullptr;
    uint8 Hash[20];FSHA1::HashBuffer(Bytes.GetData(),Bytes.Num()-20,Hash);
    if (FMemory::Memcmp(Hash,Bytes.GetData()+Bytes.Num()-20,20)!=0) return nullptr;
    Bytes.SetNum(Bytes.Num()-20);
    return Cast<UBunkerReconnectProfile>(UGameplayStatics::LoadGameFromMemory(Bytes));
}
bool WriteProfileSlot(UBunkerReconnectProfile* P,const FString& Slot)
{
    TArray<uint8> Bytes;if (!UGameplayStatics::SaveGameToMemory(P,Bytes) || Bytes.Num()>256*1024-20) return false;
    uint8 Hash[20];FSHA1::HashBuffer(Bytes.GetData(),Bytes.Num(),Hash);Bytes.Append(Hash,20);
    return UGameplayStatics::SaveDataToSlot(Bytes,Slot,0);
}
UBunkerReconnectProfile* ReadProfile(bool& bDamaged)
{
    const auto Slot=ProfileSlot();
    auto* A=ReadProfileSlot(Slot+TEXT("_A"));
    auto* B=ReadProfileSlot(Slot+TEXT("_B"));
    bool VA=ValidProfile(A),VB=ValidProfile(B);
    auto* P=VA && (!VB || A->Generation>B->Generation)?A:VB?B:nullptr;
    bDamaged=!P && (UGameplayStatics::DoesSaveGameExist(Slot+TEXT("_A"),0)||UGameplayStatics::DoesSaveGameExist(Slot+TEXT("_B"),0));
    return P;
}
void Capture(ABunkerPlayerController* PC,FBunkerSavedPlayer& R)
{
    auto* PS=PC->GetPlayerState<ABunkerPlayerState>();
    R.Inventory=PS->Inventory;R.Health=PS->Health;R.Food=PS->Food;R.Water=PS->Water;R.Energy=PS->Energy;
    R.Location=PC->CheckpointLocation();R.Rotation=PC->GetControlRotation();
}
void Reject(ABunkerGameMode* GM,ABunkerPlayerController* PC,const TCHAR* Reason)
{
    UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_REJECT %s"),Reason);
    GM->GameSession->KickPlayer(PC,FText::FromString(TEXT("Não foi possível retomar este participante. Credencial inválida, personagem conectado ou campanha sem vaga.")));
}
}

bool ABunkerGameMode::UsesCoopPersistence() const
{
    if (GetNetMode()!=NM_ListenServer) return false;
    const TCHAR* Fixtures[]={TEXT("C13NetTest"),TEXT("C13SurvivalTest"),TEXT("C13StorageTest"),TEXT("C13StorageVisual"),
        TEXT("C13HandsVisual"),TEXT("C13DoorAudit"),TEXT("C13DoorVisual"),TEXT("C13ItemVisual"),TEXT("C13SurvivalVisual"),TEXT("C13SaveProbe")};
    for (const auto* Flag:Fixtures) if (FParse::Param(FCommandLine::Get(),Flag)) return false;
    return true;
}
void ABunkerGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);
    if (!UsesCoopPersistence()) return;
    auto* PC=Cast<ABunkerPlayerController>(NewPlayer);if (!PC) return;
    if (auto* PS=PC->GetPlayerState<ABunkerPlayerState>()) {PS->bSessionReady=false;PS->ForceNetUpdate();}
    FTimerHandle Request;
    GetWorldTimerManager().SetTimer(Request,FTimerDelegate::CreateWeakLambda(PC,[this,PC]()
    {if (bPersistenceReady && !bPersistenceBlocked) RequestReconnect(PC);}),.5f,false);
}
void ABunkerPlayerState::OnRep_SessionReady()
{
    if (auto* PC=Cast<ABunkerPlayerController>(GetOwner()))
        if (PC->IsLocalController())
        {
            PC->CloseContainerView();
            if (auto* C=Cast<ACharacter>(PC->GetPawn()))
                C->GetCharacterMovement()->SetMovementMode(bSessionReady && Health>0 && !RestingBed?MOVE_Walking:MOVE_None);
        }
}
void ABunkerGameMode::RequestReconnect(ABunkerPlayerController* PC)
{
    if (!UsesCoopPersistence() || !bPersistenceReady || bPersistenceBlocked || PC->IsLocalController()) return;
    PC->ClientRequestReconnect(CampaignId);
    FTimerHandle Timeout;
    GetWorldTimerManager().SetTimer(Timeout,FTimerDelegate::CreateWeakLambda(PC,[this,PC]()
    {auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if (PS && !PS->bSessionReady) Reject(this,PC,TEXT("timeout"));}),12,false);
}
void ABunkerPlayerController::ClientRequestReconnect_Implementation(FGuid Campaign)
{
    CloseContainerView();
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest")) && FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectReset")))
    {UGameplayStatics::DeleteGameInSlot(ProfileSlot()+TEXT("_A"),0);UGameplayStatics::DeleteGameInSlot(ProfileSlot()+TEXT("_B"),0);}
#endif
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest")) && FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectDamageProfile")))
    {
        auto* A=ReadProfileSlot(ProfileSlot()+TEXT("_A"));auto* B=ReadProfileSlot(ProfileSlot()+TEXT("_B"));
        const bool UseA=ValidProfile(A) && (!ValidProfile(B) || A->Generation>B->Generation);
        TArray<uint8> Bad={1,2,3};UGameplayStatics::SaveDataToSlot(Bad,ProfileSlot()+(UseA?TEXT("_A"):TEXT("_B")),0);
        bool Failed=false;auto* Remaining=ReadProfile(Failed);
        UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_PROFILE_BACKUP remaining=%d"),Remaining!=nullptr && !Failed);
    }
#endif
    bool Damaged=false;auto* Profile=ReadProfile(Damaged);
    FString Ticket=Profile?Profile->Tickets.FindRef(Campaign.ToString()):TEXT("");
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectInvalid"))) Ticket=FString::ChrN(64,TEXT('f'));
#endif
    ServerResumeSession(Damaged?TEXT("DAMAGED_LOCAL_PROFILE"):Ticket);
}
void ABunkerPlayerController::ClientStoreReconnect_Implementation(FGuid Campaign,const FString& Ticket)
{
    bool Damaged=false;auto* Previous=ReadProfile(Damaged);
    bool Stored=false;
    if (!Damaged && Campaign.IsValid() && HexTicket(Ticket))
    {
        auto* P=NewObject<UBunkerReconnectProfile>();
        if (Previous) {P->Generation=Previous->Generation;P->Tickets=Previous->Tickets;}
        ++P->Generation;P->Tickets.Add(Campaign.ToString(),Ticket);
        const FString Slot=ProfileSlot()+(P->Generation%2?TEXT("_A"):TEXT("_B"));
        if (ValidProfile(P) && WriteProfileSlot(P,Slot))
        {
            auto* Check=ReadProfileSlot(Slot);
            Stored=ValidProfile(Check) && Check->Tickets.FindRef(Campaign.ToString())==Ticket;
            // Tickets are issued once per campaign: mirror the verified contents immediately,
            // so the first credential has a usable backup, not only a future campaign's backup.
            if (Stored)
            {
                ++P->Generation;
                const FString BackupSlot=ProfileSlot()+(P->Generation%2?TEXT("_A"):TEXT("_B"));
                const bool Backup=WriteProfileSlot(P,BackupSlot);
                UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_CREDENTIAL backup=%d"),Backup && ValidProfile(ReadProfileSlot(BackupSlot)));
            }
        }
    }
    UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_CREDENTIAL stored=%d"),Stored);
    ServerReconnectStored(Stored);
}
void ABunkerPlayerController::ServerResumeSession_Implementation(const FString& Ticket)
{
    if (auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>()) GM->ResumePlayer(this,Ticket);
}
void ABunkerPlayerController::ServerReconnectStored_Implementation(bool bStored)
{
    if (auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>()) GM->ConfirmReconnect(this,bStored);
}
void ABunkerGameMode::ResumePlayer(ABunkerPlayerController* PC,const FString& Ticket)
{
    if (!UsesCoopPersistence() || !bPersistenceReady || bPersistenceBlocked || PC->IsLocalController() || PC->bReconnectAttempted) return;
    PC->bReconnectAttempted=true;
    auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if (!PS || !PC->GetPawn()) {Reject(this,PC,TEXT("pawn"));return;}
    if (Ticket.IsEmpty())
    {
        if (RemotePlayers.Num()>=3) {Reject(this,PC,TEXT("roster"));return;}
        const FString NewTicket=FGuid::NewGuid().ToString(EGuidFormats::Digits)+FGuid::NewGuid().ToString(EGuidFormats::Digits);
        FBunkerSavedPlayer R;R.Key=FGuid::NewGuid();R.TicketHash=HashTicket(NewTicket);Capture(PC,R);
        RemotePlayers.Add(R);PC->SessionPlayerKey=R.Key;PC->bNewReconnectRecord=true;
        PC->ClientStoreReconnect(CampaignId,NewTicket);
        return;
    }
    if (!HexTicket(Ticket)) {Reject(this,PC,TEXT("invalid"));return;}
    const FString Hash=HashTicket(Ticket);
    auto* R=RemotePlayers.FindByPredicate([&](const auto& P){return P.TicketHash==Hash;});
    if (!R) {Reject(this,PC,TEXT("invalid"));return;}
    for (TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
        if (*It!=PC && It->SessionPlayerKey==R->Key) {Reject(this,PC,TEXT("active"));return;}
    PC->SessionPlayerKey=R->Key;ConfirmReconnect(PC,true);
}
void ABunkerGameMode::ConfirmReconnect(ABunkerPlayerController* PC,bool bStored)
{
    if (!UsesCoopPersistence() || !PC->bReconnectAttempted || !PC->SessionPlayerKey.IsValid()) return;
    auto* PS=PC->GetPlayerState<ABunkerPlayerState>();auto* C=Cast<ACharacter>(PC->GetPawn());
    if (!PS || !C || PS->bSessionReady) return;
    auto* R=RemotePlayers.FindByPredicate([&](const auto& P){return P.Key==PC->SessionPlayerKey;});
    if (!bStored || !R) {Reject(this,PC,TEXT("profile"));return;}
    PS->Inventory=R->Inventory;PS->Health=R->Health;PS->Food=R->Food;PS->Water=R->Water;PS->Energy=R->Energy;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(ReconnectPosition),false,C);FHitResult Floor;
    const auto Shape=FCollisionShape::MakeCapsule(C->GetCapsuleComponent()->GetScaledCapsuleRadius(),C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-2);
    const bool Safe=!GetWorld()->OverlapBlockingTestByChannel(R->Location,FQuat::Identity,ECC_Pawn,Shape,Query) &&
        GetWorld()->LineTraceSingleByChannel(Floor,R->Location,R->Location-FVector(0,0,200),ECC_Visibility,Query);
    if (Safe) {C->SetActorLocation(R->Location,false,nullptr,ETeleportType::TeleportPhysics);PC->SetControlRotation(R->Rotation);PC->ClientSetRotation(R->Rotation,true);}
    PS->bSessionReady=true;
    if (!SaveCheckpoint()) {PS->bSessionReady=false;PS->Inventory.Empty();Reject(this,PC,TEXT("checkpoint"));return;}
    PC->bNewReconnectRecord=false;
    C->GetCharacterMovement()->SetMovementMode(PS->Health>0?MOVE_Walking:MOVE_None);
    PS->ForceNetUpdate();
    PC->ClientNotice(TEXT("Participante restaurado. Seus recursos continuam na mochila."));
    UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_BOUND items=%d position=%d roster=%d"),PS->Inventory.Num(),Safe,RemotePlayers.Num());
}
void ABunkerGameMode::CaptureRoster()
{
    for (TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
    {
        auto* PS=It->GetPlayerState<ABunkerPlayerState>();
        if (!PS || !PS->bSessionReady || !It->SessionPlayerKey.IsValid()) continue;
        if (auto* R=RemotePlayers.FindByPredicate([&](const auto& P){return P.Key==It->SessionPlayerKey;})) Capture(*It,*R);
    }
}
void ABunkerGameMode::CaptureDisconnected(ABunkerPlayerController* PC)
{
    if (!UsesCoopPersistence() || PC->IsLocalController()) return;
    auto* PS=PC->GetPlayerState<ABunkerPlayerState>();
    if (!PS || !PC->SessionPlayerKey.IsValid()) return;
    if (!PS->bSessionReady)
    {
        if (PC->bNewReconnectRecord) RemotePlayers.RemoveAll([&](const auto& R){return R.Key==PC->SessionPlayerKey;});
        return;
    }
    if (auto* R=RemotePlayers.FindByPredicate([&](const auto& P){return P.Key==PC->SessionPlayerKey;}))
    {
        Capture(PC,*R);PS->bSessionReady=false;PS->Inventory.Empty();
        SaveCheckpoint();
        UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_OFFLINE items=%d"),R->Inventory.Num());
    }
}
