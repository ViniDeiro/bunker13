#include "BunkerSaveGame.h"
#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BunkerContainer.h"
#include "BunkerDoor.h"
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
        if (!It->WorldKey.IsEmpty())
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
    if (!S || S->Version!=1 || (S->Sequence<1 || S->Sequence>=MAX_int64-1) || S->Layout!=Layout(W) || !PS || !PS->Rules || S->Actors.Num()>1024 ||
        !Point(S->PlayerLocation) || S->PlayerRotation.ContainsNaN()) return false;
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
    TMap<FString,ABunkerInteractable*> Authored;
    for (TActorIterator<ABunkerInteractable> It(W);It;++It) if (!It->WorldKey.IsEmpty()) Authored.Add(It->WorldKey,*It);
    TSet<FString> Seen;
    TSet<FGuid> Tombstones;
    for (const auto& R:S->Actors)
    {
        ABunkerInteractable* A=nullptr;
        if (!R.Key.IsEmpty())
        {
            if (Seen.Contains(R.Key) || !Authored.Contains(R.Key)) return false;
            Seen.Add(R.Key); A=Authored[R.Key];
            if (R.Kind!=uint8(A->Interaction)) return false;
        }
        else if (R.Kind!=uint8(EBunkerInteraction::Pickup) || !R.Active) return false;
        if (R.Transform.ContainsNaN() || !Point(R.Transform.GetLocation())) return false;
        if (auto* D=Cast<ABunkerDoor>(A))
            if (!FMath::IsFinite(R.DoorAngle) || R.DoorAngle<FMath::Min(0.f,D->OpenAngle)-.01f || R.DoorAngle>FMath::Max(0.f,D->OpenAngle)+.01f) return false;
        if (auto* C=Cast<ABunkerContainer>(A))
        {if (!Items(R.Contents,C->MaxSlots,C->MaxWeightKg)) return false;}
        else if (!R.Contents.IsEmpty()) return false;
        if (R.Kind==uint8(EBunkerInteraction::Pickup))
        {
            // Inactive map pickups are tombstones; their GUID may now belong to a bag or locker.
            if (!Item(R.Item,R.Active)) return false;
            if (!R.Active) {if (Tombstones.Contains(R.Item.Id)) return false;Tombstones.Add(R.Item.Id);}
        }
    }
    return Seen.Num()==Authored.Num();
}
ABunkerPlayerController* Local(UWorld* W) {return Cast<ABunkerPlayerController>(W->GetFirstPlayerController());}
}

FVector ABunkerPlayerController::CheckpointLocation() const
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    return PS && PS->RestingBed?RestExit:GetPawn()?GetPawn()->GetActorLocation():FVector::ZeroVector;
}

void ABunkerPlayerController::C13Save()
{
    auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();
    ClientNotice(GM && GM->SaveCheckpoint()?TEXT("Partida solo salva."):TEXT("Não foi possível salvar. Salvamento disponível nesta etapa apenas no modo solo; veja os avisos de integridade."));
}
void ABunkerGameMode::StartPersistence()
{
    SavePrefix=Probe()?TEXT("C13_AutomatedCheckpoint"):TEXT("C13_SoloCheckpoint");
    // All older test fixtures must remain independent of a real player's campaign.
    const TCHAR* Flags[]={TEXT("C13NetTest"),TEXT("C13SurvivalTest"),TEXT("C13StorageTest"),TEXT("C13StorageVisual"),
        TEXT("C13HandsVisual"),TEXT("C13DoorAudit"),TEXT("C13DoorVisual"),TEXT("C13ItemVisual"),TEXT("C13SurvivalVisual")};
    for (const TCHAR* Flag:Flags) if (FParse::Param(FCommandLine::Get(),Flag)) return;
    if (GetNetMode()!=NM_Standalone) return;
    if (!Probe() || FParse::Param(FCommandLine::Get(),TEXT("C13SaveExit")))
        FWorldDelegates::OnWorldBeginTearDown.AddWeakLambda(this,[this](UWorld* World)
        {if (World==GetWorld()) SaveCheckpoint();});
    FTimerHandle Start;
    GetWorldTimerManager().SetTimer(Start,FTimerDelegate::CreateWeakLambda(this,[this]()
    {
#if !UE_BUILD_SHIPPING
        if (Probe()) {PersistenceProbe();return;}
#endif
        LoadCheckpoint();bPersistenceReady=true;
        GetWorldTimerManager().SetTimer(PersistenceTimer,this,&ABunkerGameMode::C13AutoSave,60,true);
    }),2,false);
}
void ABunkerGameMode::C13AutoSave() {SaveCheckpoint();}

bool ABunkerGameMode::SaveCheckpoint()
{
    auto* PC=Local(GetWorld());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;APawn* Pawn=PC?PC->GetPawn().Get():nullptr;
    if (!bPersistenceReady || bPersistenceBlocked || GetNetMode()!=NM_Standalone || !Pawn || !PS) return false;
    auto* S=NewObject<UBunkerSaveGame>(this);S->Sequence=SaveSequence+1;S->Layout=Layout(GetWorld());
    S->Inventory=PS->Inventory;S->Health=PS->Health;S->Food=PS->Food;S->Water=PS->Water;S->Energy=PS->Energy;
    S->PlayerLocation=PC->CheckpointLocation();S->PlayerRotation=PC->GetControlRotation();
    for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
    {
        if (It->WorldKey.IsEmpty() && (It->Interaction!=EBunkerInteraction::Pickup || !It->bActive)) continue;
        FBunkerSavedActor R;R.Key=It->WorldKey;R.Kind=uint8(It->Interaction);R.Active=It->bActive;R.Transform=It->GetActorTransform();
        if (auto* C=Cast<ABunkerContainer>(*It)) R.Contents=C->Contents;
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
    if (GetNetMode()!=NM_Standalone) return false;
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
    PC->ReleaseBed();PC->CloseContainerView();
    PS->Inventory=S->Inventory;PS->Health=S->Health;PS->Food=S->Food;PS->Water=S->Water;PS->Energy=S->Energy;PS->ForceNetUpdate();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(CheckpointPosition),false,Pawn);
    const auto Shape=FCollisionShape::MakeCapsule(Pawn->GetCapsuleComponent()->GetScaledCapsuleRadius(),Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-2);
    FHitResult Floor;
    const bool Safe=!GetWorld()->OverlapBlockingTestByChannel(S->PlayerLocation,FQuat::Identity,ECC_Pawn,Shape,Query) &&
        GetWorld()->LineTraceSingleByChannel(Floor,S->PlayerLocation,S->PlayerLocation-FVector(0,0,200),ECC_Visibility,Query);
    if (Safe) {Pawn->SetActorLocation(S->PlayerLocation,false,nullptr,ETeleportType::TeleportPhysics);PC->SetControlRotation(S->PlayerRotation);}
    SaveSequence=S->Sequence;bPersistenceBlocked=false;
    PC->ClientNotice(TEXT("Partida solo restaurada. F5 salva; salvamento automático a cada minuto."));
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
