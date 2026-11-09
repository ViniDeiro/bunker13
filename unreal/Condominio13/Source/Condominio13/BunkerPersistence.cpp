#include "BunkerSaveGame.h"
#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BunkerContainer.h"
#include "BunkerReferenceCabinet.h"
#include "BunkerDoor.h"
#include "BunkerRound.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/SecureHash.h"
#include "TimerManager.h"
#include "InputKeyEventArgs.h"

namespace
{
constexpr int32 MaxSaveBytes=4*1024*1024;
bool Probe()
{
#if !UE_BUILD_SHIPPING
    return FParse::Param(FCommandLine::Get(),TEXT("C13SaveProbe"));
#else
    return false;
#endif
}
FString Layout(UWorld* W)
{
    TArray<FString> Keys;
    for (TActorIterator<ABunkerInteractable> It(W);It;++It)
        if (!It->WorldKey.IsEmpty() && !Cast<ABunkerReferenceCabinet>(*It) && !ABunkerInfrastructure::Extension(*It) && !ABunkerInfrastructure::SupplyExtension(*It))
        {
            auto* D=Cast<ABunkerDoor>(*It);
            Keys.Add(It->WorldKey+It->GetClass()->GetPathName()+It->GetActorLocation().ToString()+
                FString::FromInt(int32(It->Interaction))+(D?FString::SanitizeFloat(D->ClosedYaw):TEXT("")));
        }
    Keys.Sort();
    return W->GetPackage()->GetName()+TEXT(":v1:")+FMD5::HashAnsiString(*FString::Join(Keys,TEXT("|")));
}
FBunkerInventoryEntry Entry(ABunkerInteractable* A)
{
    FBunkerInventoryEntry E; E.Id=A->ItemId;E.Name=A->DisplayName.ToString();E.ItemType=A->ItemType;
    E.WorldMesh=A->Mesh->GetStaticMesh();E.WorldScale=A->GetActorScale3D();
    for (int32 I=0;I<A->Mesh->GetNumMaterials();++I) E.Materials.Add(A->Mesh->GetMaterial(I));
    return E;
}
UBunkerSaveGame* Read(const FString& Slot)
{
    TArray<uint8> Bytes;
    if (!UGameplayStatics::LoadDataFromSlot(Bytes,Slot,0) || Bytes.Num()<21 || Bytes.Num()>MaxSaveBytes) return nullptr;
    uint8 Digest[20];FSHA1::HashBuffer(Bytes.GetData(),Bytes.Num()-20,Digest);
    if (FMemory::Memcmp(Digest,Bytes.GetData()+Bytes.Num()-20,20)!=0) return nullptr;
    Bytes.SetNum(Bytes.Num()-20);
    return Cast<UBunkerSaveGame>(UGameplayStatics::LoadGameFromMemory(Bytes));
}
bool Write(UBunkerSaveGame* S,const FString& Slot)
{
    TArray<uint8> Bytes;
    if (!UGameplayStatics::SaveGameToMemory(S,Bytes) || Bytes.Num()>MaxSaveBytes-20) return false;
    uint8 Digest[20];FSHA1::HashBuffer(Bytes.GetData(),Bytes.Num(),Digest);Bytes.Append(Digest,20);
    return UGameplayStatics::SaveDataToSlot(Bytes,Slot,0);
}
bool Point(FVector V) {return !V.ContainsNaN() && V.GetAbsMax()<100000;}
bool Valid(UBunkerSaveGame* S,UWorld* W,ABunkerPlayerState* PS)
{
    if (!S || S->Version!=(W->GetNetMode()==NM_ListenServer?2:1) || (S->Sequence<1 || S->Sequence>=MAX_int64-1) || S->Layout!=Layout(W) || !PS || !PS->Rules || S->Actors.Num()>1024 ||
        !Point(S->PlayerLocation) || S->PlayerRotation.ContainsNaN()) return false;
    if(S->bRoundMode!=(ABunkerRound::Find(W)!=nullptr) || (S->bRoundMode && (S->RoundPhase>3 || !FMath::IsFinite(S->RoundRemaining) || S->RoundRemaining<0 || S->RoundRemaining>120 || (S->RoundPhase!=1 && S->RoundRemaining!=0))))return false;
    if(!FMath::IsFinite(S->ShelterSeconds)||S->ShelterSeconds<0||S->ShelterSeconds>1.e9||!FMath::IsFinite(S->ShelterDaySeconds)||S->ShelterDaySeconds<1||S->ShelterDaySeconds>3600||(S->RoundPhase!=3&&S->ShelterSeconds!=0))return false;
    if(S->bInfrastructure && (!ABunkerInfrastructure::Find(W)||!ABunkerInfrastructure::Valid(S->Infrastructure)||S->Infrastructure.Fuel>PS->Rules->FuelCapacityLiters+.001f||S->Infrastructure.RawWater>PS->Rules->RawWaterCapacityLiters+.001f||S->Infrastructure.CleanWater>PS->Rules->CleanWaterCapacityLiters+.001f))return false;
    for (float Value:{S->Health,S->Food,S->Water,S->Energy})
        if (!FMath::IsFinite(Value) || Value<0 || Value>100) return false;
    TSet<FGuid> Owned;
    auto Item=[&](const FBunkerInventoryEntry& E,bool bOwned=true)
    {
        auto* Def=PS->Rules->Find(E.ItemType);
        if (!E.Id.IsValid() || (bOwned && Owned.Contains(E.Id)) || !Def || !E.WorldMesh ||
            !E.WorldMesh->GetPathName().StartsWith(TEXT("/Game/Bunker/")) || E.Name.Len()>128 ||
            E.Materials.Num()>16 || E.WorldScale.ContainsNaN() || E.WorldScale.GetMin()<=0 || E.WorldScale.GetMax()>10 ||
            !FMath::IsFinite(E.WeightKg) || !FMath::IsNearlyEqual(E.WeightKg,Def->WeightKg)) return false;
        for (const auto& M:E.Materials) if (!M || !M->GetPathName().StartsWith(TEXT("/Game/"))) return false;
        if (bOwned) Owned.Add(E.Id); return true;
    };
    auto Items=[&](const TArray<FBunkerInventoryEntry>& Entries,int32 Slots,float MaxWeight)
    {
        if (Entries.Num()>Slots) return false;
        float Weight=0;for (const auto& E:Entries) {if (!Item(E)) return false;Weight+=E.WeightKg;}
        return Weight<=MaxWeight+.001f;
    };
    if (!Items(S->Inventory,PS->Rules->MaxSlots,PS->Rules->MaxWeightKg)) return false;
    const bool Coop=W->GetNetMode()==NM_ListenServer;
    if ((!Coop && (!S->RemotePlayers.IsEmpty() || S->CampaignId.IsValid())) || S->RemotePlayers.Num()>3 || (Coop && !S->CampaignId.IsValid())) return false;
    TSet<FGuid> PlayerKeys;TSet<FString> TicketHashes;
    for (const auto& R:S->RemotePlayers)
    {
        if (!R.Key.IsValid() || PlayerKeys.Contains(R.Key) || R.TicketHash.Len()!=64 || TicketHashes.Contains(R.TicketHash) ||
            !Point(R.Location) || R.Rotation.ContainsNaN()) return false;
        for (TCHAR C:R.TicketHash) if (!FChar::IsHexDigit(C)) return false;
        for (float V:{R.Health,R.Food,R.Water,R.Energy}) if (!FMath::IsFinite(V) || V<0 || V>100) return false;
        if (!Items(R.Inventory,PS->Rules->MaxSlots,PS->Rules->MaxWeightKg)) return false;
        PlayerKeys.Add(R.Key);TicketHashes.Add(R.TicketHash);
    }
    TMap<FString,ABunkerInteractable*> Authored;
    for (TActorIterator<ABunkerInteractable> It(W);It;++It) if (!It->WorldKey.IsEmpty()) Authored.Add(It->WorldKey,*It);
    int32 SupplyCount=0;for(const auto& Pair:Authored)if(ABunkerInfrastructure::SupplyExtension(Pair.Value))SupplyCount++;
    if(ABunkerInfrastructure::Find(W)&&SupplyCount!=6)return false;
    if(S->bExternalSupplies&&(!S->bInfrastructure||SupplyCount!=6))return false;
    TSet<FString> Seen;
    TSet<FGuid> Tombstones;
    for (const auto& R:S->Actors)
    {
        ABunkerInteractable* A=nullptr;
        if (!R.Key.IsEmpty())
        {
            if (Seen.Contains(R.Key) || !Authored.Contains(R.Key)) return false;
            Seen.Add(R.Key); A=Authored[R.Key];
            if(ABunkerInfrastructure::Extension(A)&&!S->bInfrastructure)return false;
            if(ABunkerInfrastructure::SupplyExtension(A)&&!S->bExternalSupplies)return false;
            if (R.Kind!=uint8(A->Interaction)) return false;
        }
        else if (R.Kind!=uint8(EBunkerInteraction::Pickup) || !R.Active) return false;
        if (R.Transform.ContainsNaN() || !Point(R.Transform.GetLocation())) return false;
        if (auto* D=Cast<ABunkerDoor>(A))
            if (!FMath::IsFinite(R.DoorAngle) || R.DoorAngle<FMath::Min(0.f,D->OpenAngle)-.01f || R.DoorAngle>FMath::Max(0.f,D->OpenAngle)+.01f) return false;
        if (auto* C=Cast<ABunkerContainer>(A))
        {if (!Items(R.Contents,C->MaxSlots,C->MaxWeightKg)) return false;
            if (auto* Physical=Cast<ABunkerReferenceCabinet>(C))
                if (!Physical->ValidSlots(R.Contents) || !FMath::IsFinite(R.DoorAngle) || R.DoorAngle<0 || R.DoorAngle>110) return false;}
        else if (!R.Contents.IsEmpty()) return false;
        if (R.Kind==uint8(EBunkerInteraction::Pickup))
        {
            // Inactive map pickups are tombstones; their GUID may now belong to a bag or locker.
            if (!Item(R.Item,R.Active)) return false;
            if (!R.Active) {if (Tombstones.Contains(R.Item.Id)) return false;Tombstones.Add(R.Item.Id);}
        }
    }
    // Only the new, initially empty fixture is an allowed additive layout extension.
    // All legacy actor keys and the exact legacy fingerprint remain mandatory.
    for (const auto& Pair:Authored) if (!Seen.Contains(Pair.Key) && !Cast<ABunkerReferenceCabinet>(Pair.Value) && !(ABunkerInfrastructure::Extension(Pair.Value)&&!S->bInfrastructure) && !(ABunkerInfrastructure::SupplyExtension(Pair.Value)&&!S->bExternalSupplies)) return false;
    return true;
}
ABunkerPlayerController* Local(UWorld* W) {for(TActorIterator<ABunkerPlayerController> It(W);It;++It) if(It->IsLocalController()) return *It;return nullptr;}
}

FVector ABunkerPlayerController::CheckpointLocation() const
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    return PS && PS->RestingBed?RestExit:GetPawn()?GetPawn()->GetActorLocation():FVector::ZeroVector;
}

void ABunkerPlayerController::C13Save()
{
    auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();
    ClientNotice(GM && GM->SaveCheckpoint()?TEXT("Partida salva."):TEXT("Não foi possível salvar. Apenas o host pode gravar; confira os avisos de integridade."));
}
void ABunkerGameMode::StartPersistence()
{
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest")) && GetNetMode()!=NM_ListenServer) return;
#endif
    SavePrefix=Probe()?TEXT("C13_AutomatedCheckpoint"):TEXT("C13_SoloCheckpoint");
    // All older test fixtures must remain independent of a real player's campaign.
    const TCHAR* Flags[]={TEXT("C13NetTest"),TEXT("C13SurvivalTest"),TEXT("C13StorageTest"),TEXT("C13StorageVisual"),
        TEXT("C13Reference"),TEXT("C13HandsVisual"),TEXT("C13DoorAudit"),TEXT("C13DoorVisual"),TEXT("C13ItemVisual"),TEXT("C13SurvivalVisual")};
    for (const TCHAR* Flag:Flags) if (FParse::Param(FCommandLine::Get(),Flag)) return;
    if (GetNetMode()!=NM_Standalone && !UsesCoopPersistence()) return;
    if (UsesCoopPersistence())
    {
        SavePrefix=TEXT("C13_CoopCheckpoint");CampaignId=FGuid::NewGuid();
#if !UE_BUILD_SHIPPING
        if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest")))
        {
            SavePrefix=TEXT("C13_TestCoopCheckpoint");
            if (FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectReset")))
            {UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_A"),0);UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_B"),0);}
        }
#endif
        for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) {It->bSessionReady=false;It->ForceNetUpdate();}
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("C13Round")))SavePrefix=GetNetMode()==NM_ListenServer?TEXT("C13_MvpRoundCoop"):TEXT("C13_MvpRoundSolo");
#if !UE_BUILD_SHIPPING
    if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest")))SavePrefix=TEXT("C13_TestRound");
    if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest")) && FParse::Param(FCommandLine::Get(),TEXT("C13RoundReset"))){UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_A"),0);UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_B"),0);}
#endif
    if (!Probe() || FParse::Param(FCommandLine::Get(),TEXT("C13SaveExit")))
        FWorldDelegates::OnWorldBeginTearDown.AddWeakLambda(this,[this](UWorld* World)
        {if (World==GetWorld()) {SaveCheckpoint();bCheckpointEnding=true;}});
    FTimerHandle Start;
    GetWorldTimerManager().SetTimer(Start,FTimerDelegate::CreateWeakLambda(this,[this]()
    {
#if !UE_BUILD_SHIPPING
        if (Probe()) {PersistenceProbe();return;}
#endif
        LoadCheckpoint();bPersistenceReady=true;
        if(!UsesCoopPersistence()&&ABunkerInfrastructure::Find(GetWorld())&&!bPersistenceBlocked&&!SaveCheckpoint())
        {bPersistenceBlocked=true;if(auto* PC=Local(GetWorld()))if(auto* PS=PC->GetPlayerState<ABunkerPlayerState>())PS->bSessionReady=false;return;}
        if (UsesCoopPersistence())
        {
            auto* Host=Local(GetWorld());auto* PS=Host?Host->GetPlayerState<ABunkerPlayerState>():nullptr;
            if (!PS || bPersistenceBlocked) return;
            PS->bSessionReady=true;PS->OnRep_SessionReady();PS->ForceNetUpdate();
            if (!SaveCheckpoint()) {PS->bSessionReady=false;bPersistenceBlocked=true;return;}
            for(TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It) RequestReconnect(*It);
            StartReconnectValidation();
        }
        GetWorldTimerManager().SetTimer(PersistenceTimer,this,&ABunkerGameMode::C13AutoSave,60,true);
    }),2,false);
}
void ABunkerGameMode::C13AutoSave() {SaveCheckpoint();}

bool ABunkerGameMode::SaveCheckpoint()
{
    auto* PC=Local(GetWorld());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;APawn* Pawn=PC?PC->GetPawn().Get():nullptr;
    if (!bPersistenceReady || bPersistenceBlocked || bCheckpointEnding || (GetNetMode()!=NM_Standalone && !UsesCoopPersistence()) || !Pawn || !PS) return false;
    auto* S=NewObject<UBunkerSaveGame>(this);S->Sequence=SaveSequence+1;S->Layout=Layout(GetWorld());
    if(auto* Round=ABunkerRound::Find(GetWorld()))Round->Store(S);
    if(auto* Infra=ABunkerInfrastructure::Find(GetWorld()))Infra->Store(S);
    if (UsesCoopPersistence())
    {
        CaptureRoster();S->Version=2;S->CampaignId=CampaignId;S->RemotePlayers=RemotePlayers;
        for (TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
            if (It->bNewReconnectRecord && (!It->GetPlayerState<ABunkerPlayerState>() || !It->GetPlayerState<ABunkerPlayerState>()->bSessionReady))
                S->RemotePlayers.RemoveAll([&](const auto& R){return R.Key==It->SessionPlayerKey;});
    }
    S->Inventory=PS->Inventory;S->Health=PS->Health;S->Food=PS->Food;S->Water=PS->Water;S->Energy=PS->Energy;
    S->PlayerLocation=PC->CheckpointLocation();S->PlayerRotation=PC->GetControlRotation();
    for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
    {
        if (It->WorldKey.IsEmpty() && (It->Interaction!=EBunkerInteraction::Pickup || !It->bActive)) continue;
        FBunkerSavedActor R;R.Key=It->WorldKey;R.Kind=uint8(It->Interaction);R.Active=It->bActive;R.Transform=It->GetActorTransform();
        if (auto* C=Cast<ABunkerContainer>(*It)) R.Contents=C->Contents;
        if (auto* C=Cast<ABunkerReferenceCabinet>(*It)) {R.Active=C->bDoorOpen;R.DoorAngle=C->DoorAngle;}
        if (auto* D=Cast<ABunkerDoor>(*It)) {R.Active=D->bOpen;R.DoorAngle=D->CurrentAngle;}
        if (It->Interaction==EBunkerInteraction::Pickup)
        {R.Item=Entry(*It);if (auto* Def=PS->Rules->Find(R.Item.ItemType)) R.Item.WeightKg=Def->WeightKg;}
        S->Actors.Add(R);
    }
    if (!Valid(S,GetWorld(),PS)) {UE_LOG(LogTemp,Warning,TEXT("C13_SAVE_REJECT validation"));return false;}
    const FString Slot=SavePrefix+(S->Sequence%2?TEXT("_A"):TEXT("_B"));
    if (!Write(S,Slot)) return false;
    auto* Verified=Read(Slot);
    if (!Verified || Verified->Sequence!=S->Sequence || !Valid(Verified,GetWorld(),PS)) return false;
    SaveSequence=S->Sequence;
    UE_LOG(LogTemp,Display,TEXT("C13_SAVE_COMMIT sequence=%lld actors=%d"),SaveSequence,S->Actors.Num());
    return true;
}

bool ABunkerGameMode::LoadCheckpoint()
{
    auto* PC=Local(GetWorld());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;auto* Pawn=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
    if (GetNetMode()!=NM_Standalone && !UsesCoopPersistence()) return false;
    if (!Pawn || !PS) {bPersistenceBlocked=true;return false;}
    auto* A=Read(SavePrefix+TEXT("_A"));auto* B=Read(SavePrefix+TEXT("_B"));
    bool VA=Valid(A,GetWorld(),PS),VB=Valid(B,GetWorld(),PS);
    auto* S=VA && (!VB || A->Sequence>B->Sequence)?A:VB?B:nullptr;
    if (!S)
    {
        bPersistenceBlocked=UGameplayStatics::DoesSaveGameExist(SavePrefix+TEXT("_A"),0)||UGameplayStatics::DoesSaveGameExist(SavePrefix+TEXT("_B"),0);
        if (bPersistenceBlocked) PC->ClientNotice(TEXT("Salvamento incompatível ou danificado. Arquivos preservados; gravação bloqueada."));
        UE_LOG(LogTemp,Display,TEXT("C13_SAVE_LOAD none blocked=%d"),bPersistenceBlocked);return false;
    }
    if(ABunkerInfrastructure::Find(GetWorld())&&!S->bInfrastructure)
    {
        for(const TCHAR* Suffix:{TEXT("_A"),TEXT("_B")})
        {TArray<uint8> Bytes;if(!UGameplayStatics::LoadDataFromSlot(Bytes,SavePrefix+Suffix,0))continue;
         const FString Backup=SavePrefix+TEXT("_PreInfrastructure_")+BytesToHex(Bytes.GetData()+FMath::Max(0,Bytes.Num()-20),FMath::Min(8,Bytes.Num()));
         if(!UGameplayStatics::DoesSaveGameExist(Backup,0)&&!UGameplayStatics::SaveDataToSlot(Bytes,Backup,0)){bPersistenceBlocked=true;return false;}}
        UE_LOG(LogTemp,Display,TEXT("C13_INFRA_LEGACY_BACKUP"));
    }
    if(ABunkerInfrastructure::Find(GetWorld())&&!S->bExternalSupplies)
    {
        for(const TCHAR* Suffix:{TEXT("_A"),TEXT("_B")})
        {TArray<uint8> Bytes;if(!UGameplayStatics::LoadDataFromSlot(Bytes,SavePrefix+Suffix,0))continue;
         const FString Backup=SavePrefix+TEXT("_PreSupplyV1_")+BytesToHex(Bytes.GetData()+FMath::Max(0,Bytes.Num()-20),FMath::Min(8,Bytes.Num()));
         TArray<uint8> Verified;
         if(!UGameplayStatics::DoesSaveGameExist(Backup,0)&&!UGameplayStatics::SaveDataToSlot(Bytes,Backup,0)){bPersistenceBlocked=true;return false;}
         if(!UGameplayStatics::LoadDataFromSlot(Verified,Backup,0)||Verified!=Bytes){bPersistenceBlocked=true;return false;}}
        UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_LEGACY_BACKUP"));
    }
    // Stage dynamic drops before changing existing state, so allocation failure leaves the world intact.
    TArray<ABunkerInteractable*> Staged;
    for (const auto& R:S->Actors) if (R.Key.IsEmpty())
    {
        FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* D=GetWorld()->SpawnActor<ABunkerInteractable>(ABunkerInteractable::StaticClass(),R.Transform,P);
        if (!D) {for(auto* Spawned:Staged) Spawned->Destroy();bPersistenceBlocked=true;return false;}
        D->bActive=false;D->OnRep_State();Staged.Add(D);
    }
    for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
        if (It->WorldKey.IsEmpty() && It->Interaction==EBunkerInteraction::Pickup && !Staged.Contains(*It)) It->Destroy();
    TMap<FString,ABunkerInteractable*> Map;
    for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It) if (!It->WorldKey.IsEmpty()) Map.Add(It->WorldKey,*It);
    int32 Dynamic=0;
    for (const auto& R:S->Actors)
    {
        auto* Actor=R.Key.IsEmpty()?Staged[Dynamic++]:Map[R.Key];
        if (auto* C=Cast<ABunkerContainer>(Actor)) {C->Contents=R.Contents;++C->Revision;C->RefreshViewers();}
        if (auto* C=Cast<ABunkerReferenceCabinet>(Actor)) {C->bDoorOpen=R.Active;C->DoorAngle=R.DoorAngle;C->NormalizeSlots();}
        if (auto* D=Cast<ABunkerDoor>(Actor)) {D->bOpen=R.Active;D->CurrentAngle=R.DoorAngle;D->SetActorRotation(FRotator(0,D->ClosedYaw+D->CurrentAngle,0));}
        else Actor->bActive=R.Active;
        if (R.Kind==uint8(EBunkerInteraction::Pickup))
        {
            Actor->ItemId=R.Item.Id;Actor->ItemType=R.Item.ItemType;Actor->DisplayName=FText::FromString(R.Item.Name);
            Actor->SetActorTransform(R.Transform);Actor->PickupMesh=R.Item.WorldMesh;Actor->PickupMaterials=R.Item.Materials;
            Actor->PickupScale=R.Item.WorldScale;Actor->OnRep_Visual();Actor->OnRep_State();
        }
        Actor->ForceNetUpdate();
    }
    if (UsesCoopPersistence()) {RemotePlayers=S->RemotePlayers;CampaignId=S->CampaignId;}
    PC->ReleaseBed();PC->CloseContainerView();
    PS->Inventory=S->Inventory;PS->Health=S->Health;PS->Food=S->Food;PS->Water=S->Water;PS->Energy=S->Energy;PS->ForceNetUpdate();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(CheckpointPosition),false,Pawn);
    const auto Shape=FCollisionShape::MakeCapsule(Pawn->GetCapsuleComponent()->GetScaledCapsuleRadius(),Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-2);
    FHitResult Floor;
    const bool Safe=!GetWorld()->OverlapBlockingTestByChannel(S->PlayerLocation,FQuat::Identity,ECC_Pawn,Shape,Query) &&
        GetWorld()->LineTraceSingleByChannel(Floor,S->PlayerLocation,S->PlayerLocation-FVector(0,0,200),ECC_Visibility,Query);
    if (Safe) {Pawn->SetActorLocation(S->PlayerLocation,false,nullptr,ETeleportType::TeleportPhysics);PC->SetControlRotation(S->PlayerRotation);}
    SaveSequence=S->Sequence;bPersistenceBlocked=false;
    if(auto* Round=ABunkerRound::Find(GetWorld()))Round->Restore(S);
    if(auto* Infra=ABunkerInfrastructure::Find(GetWorld()))Infra->Restore(S);
    PC->ClientNotice(TEXT("Partida restaurada. Host: F5 salva; gravação automática a cada minuto."));
    UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_RESTORED introduced=%d"),S->bExternalSupplies);
    UE_LOG(LogTemp,Display,TEXT("C13_SAVE_LOAD sequence=%lld position=%d inventory=%d"),SaveSequence,Safe,PS->Inventory.Num());
    return true;
}

void ABunkerGameMode::PersistenceProbe()
{
#if !UE_BUILD_SHIPPING
    FString Phase;FParse::Value(FCommandLine::Get(),TEXT("C13SavePhase="),Phase);
    auto* PC=Local(GetWorld());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
    bool Passed=PS && PC->GetPawn();
    const FGuid BagId(13,1,1,1),BoxId(13,2,2,2),DropId(13,3,3,3);
    auto Audit=[&](bool Value)
    {
        UE_LOG(LogTemp,Display,TEXT("C13_SAVE_PROBE %s phase=%s sequence=%lld"),Value?TEXT("PASS"):TEXT("FAIL"),*Phase,SaveSequence);
        FPlatformMisc::RequestExit(false);
    };
    if (!Passed) {Audit(false);return;}
    bPersistenceReady=true;
    if (Phase.StartsWith(TEXT("reference_")))
    {
        TActorIterator<ABunkerReferenceCabinet> It(GetWorld());auto* Box=It?*It:nullptr;
        const FGuid RefId(0xC1300022,0xF100,0,8);Passed=Box!=nullptr;
        if (Passed && Phase==TEXT("reference_seed"))
        {
            UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_A"),0);UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_B"),0);SaveSequence=0;
            ABunkerInteractable* Pickup=nullptr;
            for (TActorIterator<ABunkerInteractable> P(GetWorld());P;++P) if (P->Interaction==EBunkerInteraction::Pickup && P->ItemType==TEXT("Water") && !Pickup) Pickup=*P;
            Passed=Pickup!=nullptr;
            if(Pickup){Pickup->ItemId=RefId;auto E=Entry(Pickup);E.WeightKg=PS->Rules->Find(E.ItemType)->WeightKg;E.StorageSlot=8;Box->Contents.Add(E);Box->bDoorOpen=true;Box->DoorAngle=110;Pickup->bActive=false;Pickup->OnRep_State();Passed=SaveCheckpoint();}
        }
        else if(Passed && Phase==TEXT("reference_load"))
        {Passed=LoadCheckpoint() && Box->Contents.Num()==1 && Box->Contents[0].Id==RefId && Box->Contents[0].StorageSlot==8 && Box->bDoorOpen && FMath::IsNearlyEqual(Box->DoorAngle,110.f);}
        else if(Passed && Phase==TEXT("reference_badslot"))
        {
            auto* S=Read(SavePrefix+TEXT("_A"));Passed=S!=nullptr;
            if(S){for(auto& R:S->Actors)if(R.Key==Box->WorldKey && R.Contents.Num()){auto E=R.Contents[0];E.Id=FGuid::NewGuid();R.Contents.Add(E);}Passed=!Valid(S,GetWorld(),PS);}
        }
        else if(Passed && Phase==TEXT("reference_legacy"))
        {
            auto* S=Read(SavePrefix+TEXT("_A"));Passed=S!=nullptr;
            if(S){for(auto& R:S->Actors)if(R.Key==Box->WorldKey){for(auto E:R.Contents){E.StorageSlot=-1;S->Inventory.Add(E);}}S->Actors.RemoveAll([&](const auto& R){return R.Key==Box->WorldKey;});S->Sequence=2;Passed=Valid(S,GetWorld(),PS) && Write(S,SavePrefix+TEXT("_B"));}
        }
        else if(Passed && Phase==TEXT("reference_migrate"))
        {Passed=LoadCheckpoint() && PS->Inventory.Num()==1 && PS->Inventory[0].Id==RefId && Box->Contents.IsEmpty() && !Box->bDoorOpen && SaveCheckpoint();}
        else Passed=false;
        Audit(Passed);return;
    }
    if (Phase==TEXT("seed"))
    {
        UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_A"),0);UGameplayStatics::DeleteGameInSlot(SavePrefix+TEXT("_B"),0);
        TArray<ABunkerInteractable*> Pickups;ABunkerContainer* Box=nullptr;
        for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
        {
            if (It->Interaction==EBunkerInteraction::Pickup && It->bActive) Pickups.Add(*It);
            if (auto* C=Cast<ABunkerContainer>(*It)) if (!Box || C->WorldKey<Box->WorldKey) Box=C;
        }
        Pickups.Sort([](const ABunkerInteractable& A,const ABunkerInteractable& B){return A.WorldKey<B.WorldKey;});
        Passed=Pickups.Num()>=3 && Box;
        if (Passed)
        {
            for (int32 I=0;I<3;++I)
            {
                auto* P=Pickups[I];P->ItemId=I==0?BagId:I==1?BoxId:DropId;
                auto E=Entry(P);auto* Def=PS->Rules->Find(E.ItemType);if (!Def) {Passed=false;break;} E.WeightKg=Def->WeightKg;
                P->bActive=false;P->OnRep_State();
                if (I==0) PS->Inventory.Add(E);
                if (I==1) Box->Contents.Add(E);
                if (I==2)
                {
                    // Use the actual authoritative drop action to create the saved world resource.
                    PS->Inventory.Add(E);PC->ServerDropItem(E.Id);
                }
            }
            PS->Health=62;PS->Food=53;PS->Water=44;PS->Energy=35;
            for (TActorIterator<ABunkerDoor> It(GetWorld());It;++It) {It->bOpen=false;It->CurrentAngle=0;}
            Passed=Passed && SaveCheckpoint();
            if (Passed)
            {
                // Exercise the shipped F5 binding through the engine input queue.
                PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,EKeys::F5,IE_Pressed,1.f,false,FPlatformTime::Cycles64()));
                FTimerHandle KeyAudit;
                GetWorldTimerManager().SetTimer(KeyAudit,FTimerDelegate::CreateWeakLambda(this,[this]()
                {
                    auto* Controller=Local(GetWorld());
                    Controller->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,EKeys::F5,IE_Released,0.f,false,FPlatformTime::Cycles64()));
                    UE_LOG(LogTemp,Display,TEXT("C13_SAVE_PROBE %s phase=seed sequence=%lld input=F5"),SaveSequence==2?TEXT("PASS"):TEXT("FAIL"),SaveSequence);
                    FPlatformMisc::RequestExit(false);
                }),.2f,false);
                return;
            }
        }
        Audit(Passed);return;
    }
    if (Phase==TEXT("corrupt"))
    {
        TArray<uint8> Garbage={1,2,3,4};Passed=UGameplayStatics::SaveDataToSlot(Garbage,SavePrefix+TEXT("_B"),0);
        Audit(Passed);return;
    }
    if (Phase==TEXT("version") || Phase==TEXT("layout") || Phase==TEXT("duplicate") || Phase==TEXT("position"))
    {
        auto* S=Read(SavePrefix+TEXT("_A"));Passed=S!=nullptr;
        if (S)
        {
            S->Sequence=2;
            if (Phase==TEXT("version")) S->Version=999;
            if (Phase==TEXT("layout")) S->Layout=TEXT("different_map");
            if (Phase==TEXT("duplicate")) {const FBunkerInventoryEntry Copy=S->Inventory[0];S->Inventory.Add(Copy);}
            if (Phase==TEXT("position")) S->PlayerLocation=FVector::ZeroVector;
            Passed=Write(S,SavePrefix+TEXT("_B"));
        }
        Audit(Passed);return;
    }
    if (Phase==TEXT("blocked"))
    {
        TArray<uint8> Garbage={1,2,3};
        UGameplayStatics::SaveDataToSlot(Garbage,SavePrefix+TEXT("_A"),0);
        UGameplayStatics::SaveDataToSlot(Garbage,SavePrefix+TEXT("_B"),0);
        Passed=!LoadCheckpoint() && bPersistenceBlocked && !SaveCheckpoint() && PS->Inventory.IsEmpty();
        Audit(Passed);return;
    }
    if (Phase==TEXT("shutdown"))
    {
        Passed=LoadCheckpoint() && SaveSequence==3;PS->Health=61;Audit(Passed);return;
    }
    const bool Loaded=LoadCheckpoint();int32 BagCount=0,BoxCount=0,DropCount=0,Hidden=0;bool Doors=true;
    for (const auto& E:PS->Inventory) BagCount+=E.Id==BagId;
    for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
    {
        if (auto* C=Cast<ABunkerContainer>(*It)) for(const auto& E:C->Contents) BoxCount+=E.Id==BoxId;
        if (It->Interaction==EBunkerInteraction::Pickup)
        {
            DropCount+=It->bActive && It->ItemId==DropId;
            Hidden+=!It->bActive && (It->ItemId==BagId || It->ItemId==BoxId || It->ItemId==DropId);
        }
        if (auto* D=Cast<ABunkerDoor>(*It)) Doors&=!D->bOpen;
    }
    const int64 Expected=Phase==TEXT("load")?2:Phase==TEXT("roundtrip")?3:Phase==TEXT("shutdownload")?4:Phase==TEXT("safe_spawn")?2:1;
    Passed=Loaded && SaveSequence==Expected && BagCount==1 && BoxCount==1 && DropCount==1 && Hidden==3 && Doors &&
        FMath::IsNearlyEqual(PS->Health,Phase==TEXT("shutdownload")?61.f:62.f) && FMath::IsNearlyEqual(PS->Food,53) &&
        FMath::IsNearlyEqual(PS->Water,44) && FMath::IsNearlyEqual(PS->Energy,35);
    UE_LOG(LogTemp,Display,TEXT("C13_SAVE_CONTENT bag=%d box=%d drop=%d tombstones=%d doors=%d"),BagCount,BoxCount,DropCount,Hidden,Doors);
    if (Phase==TEXT("safe_spawn")) Passed=Passed && !PC->GetPawn()->GetActorLocation().IsNearlyZero();
    if (Phase==TEXT("load")) Passed=SaveCheckpoint() && Passed;
    Audit(Passed);
#endif
}

void ABunkerGameMode::SupplyPersistenceAudit()
{
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("C13SupplyTest")))return;
 auto* PC=Local(GetWorld());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
 if(!PS||!SaveCheckpoint())return;
 auto* A=Read(SavePrefix+TEXT("_A"));auto* B=Read(SavePrefix+TEXT("_B"));auto* S=A&&(!B||A->Sequence>B->Sequence)?A:B;
 if(!S||!Valid(S,GetWorld(),PS))return;
 auto* Missing=DuplicateObject<UBunkerSaveGame>(S,this);Missing->Actors.RemoveAll([](const auto& R){return R.Key==TEXT("SupplyV1_0");});
 auto* Mixed=DuplicateObject<UBunkerSaveGame>(S,this);Mixed->bExternalSupplies=false;
 auto* Migration=DuplicateObject<UBunkerSaveGame>(S,this);Migration->bExternalSupplies=false;Migration->Actors.RemoveAll([](const auto& R){return R.Key.StartsWith(TEXT("SupplyV1_"));});
 auto* Duplicate=DuplicateObject<UBunkerSaveGame>(S,this);for(const auto& R:S->Actors)if(R.Key==TEXT("SupplyV1_0")){Duplicate->Actors.Add(R);break;}
 UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_SCHEMA missing=%d mixed=%d migration=%d duplicate=%d"),!Valid(Missing,GetWorld(),PS),!Valid(Mixed,GetWorld(),PS),Valid(Migration,GetWorld(),PS),!Valid(Duplicate,GetWorld(),PS));
#endif
}
