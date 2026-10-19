#include "BunkerNetwork.h"
#include "BunkerContainer.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UnrealClient.h"
namespace {
ABunkerContainer* StorageTarget(UWorld* W)
{
    for (TActorIterator<ABunkerContainer> It(W);It;++It)
        if (FParse::Param(FCommandLine::Get(),TEXT("C13StorageTest"))?It->DisplayName.ToString()==TEXT("NET_Storage"):It->DisplayName.ToString()==TEXT("Despensa — suprimentos")) return *It;
    return nullptr;
}
FBunkerInventoryEntry StorageEntry(FName Type)
{
    FBunkerInventoryEntry E;E.Id=FGuid::NewGuid();E.ItemType=Type;E.Name=Type==TEXT("Water")?TEXT("garrafa de água"):Type==TEXT("Food")?TEXT("lata de alimento"):TEXT("kit médico");
    E.WeightKg=Type==TEXT("Water")?.6f:Type==TEXT("Food")?.4f:.8f;
    E.WorldMesh=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Bunker/Items/")+Type.ToString()+TEXT("/SM_Item_")+Type.ToString()+TEXT(".SM_Item_")+Type.ToString()));return E;
}
}
void ABunkerGameMode::StartStorageValidation()
{
#if !UE_BUILD_SHIPPING
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("C13StorageTest")),Visual=FParse::Param(FCommandLine::Get(),TEXT("C13StorageVisual"));
    if (!Test && !Visual) return;
    ABunkerContainer* Storage=nullptr;
    if (Test)
    {
        FActorSpawnParameters P;P.Name=TEXT("NET_Storage");P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        Storage=GetWorld()->SpawnActor<ABunkerContainer>(FVector(10000,10000,4900),FRotator::ZeroRotator,P);
        Storage->DisplayName=FText::FromString(TEXT("NET_Storage"));
        Storage->PickupMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/HeroKit/SM_Hero_Locker.SM_Hero_Locker"));Storage->OnRep_Visual();Storage->bAlwaysRelevant=true;Storage->ForceNetUpdate();
        P.Name=TEXT("NET_Storage_Floor");
        auto* Floor=GetWorld()->SpawnActor<ABunkerInteractable>(FVector(10000,10100,4850),FRotator::ZeroRotator,P);
        Floor->Interaction=EBunkerInteraction::Panel;Floor->SetActorScale3D(FVector(14,14,1));
    }
    else Storage=StorageTarget(GetWorld());
    if (!Storage) {UE_LOG(LogTemp,Error,TEXT("C13_STORAGE_FIXTURE_MISSING"));return;}
    Storage->Contents.Empty();Storage->Contents.Add(StorageEntry(TEXT("Water")));
    if (Visual) Storage->Contents.Add(StorageEntry(TEXT("Food")));
    const FGuid Original=Storage->Contents[0].Id;
    auto Audit=[this,Storage,Original](const TCHAR* Name,int32 ExpectedStored,int32 ExpectedHeld,bool Filled=false) {
        int32 Held=0,Total=0;bool Unique=true;TSet<FGuid> All;
        for (const auto& E:Storage->Contents) {Unique &= !All.Contains(E.Id);All.Add(E.Id);Total++;}
        for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)
            for (const auto& E:It->Inventory) {Held++;Unique &= !All.Contains(E.Id);All.Add(E.Id);Total++;}
        const bool Pass=Storage->Contents.Num()==ExpectedStored && Held==ExpectedHeld && Unique && All.Contains(Original);
        UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_AUDIT %s %s stored=%d held=%d unique=%d"),Name,Pass?TEXT("PASS"):TEXT("FAIL"),Storage->Contents.Num(),Held,Unique);
    };
    if (Test)
    {
        auto Timer=[this](float T,TFunction<void()> Fn){FTimerHandle H;GetWorldTimerManager().SetTimer(H,FTimerDelegate::CreateWeakLambda(this,[Fn](){Fn();}),T,false);};
        Timer(9,[Audit](){Audit(TEXT("race"),0,1);});
        Timer(18,[Audit](){Audit(TEXT("deposit"),1,0);});
        Timer(24,[Audit](){Audit(TEXT("remote_reject"),1,0);});
        Timer(26,[this](){for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) {It->Inventory.Empty();for (int32 I=0;I<12;I++) It->Inventory.Add(StorageEntry(TEXT("Food")));It->ForceNetUpdate();}});
        Timer(32,[Audit](){Audit(TEXT("capacity"),1,48,true);});
        Timer(33,[this](){for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It){It->Inventory.Empty();It->ForceNetUpdate();}});
        Timer(37,[this](){for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) if (It->Rules) It->Rules->MaxWeightKg=.1f;});
        Timer(43,[Audit](){Audit(TEXT("weight"),1,0);});
        Timer(44,[this](){for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) if (It->Rules) It->Rules->MaxWeightKg=20;});
        Timer(47,[Audit](){Audit(TEXT("final"),1,0);});
    }
    else
    {
        FTimerHandle Setup;GetWorldTimerManager().SetTimer(Setup,FTimerDelegate::CreateWeakLambda(this,[this]() {
            if (auto* PC=Cast<ABunkerPlayerController>(UGameplayStatics::GetPlayerController(this,0)))
                if (auto* PS=PC->GetPlayerState<ABunkerPlayerState>()) {PS->Inventory.Empty();PS->Inventory.Add(StorageEntry(TEXT("Medkit")));}
        }),2,false);
    }
#endif
}
void ABunkerPlayerController::ServerPrepareStorageProbe_Implementation(bool bFar)
{
#if !UE_BUILD_SHIPPING
    if (!FParse::Param(FCommandLine::Get(),TEXT("C13StorageTest")) && !FParse::Param(FCommandLine::Get(),TEXT("C13StorageVisual"))) return;
    auto* Storage=StorageTarget(GetWorld());auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();if (!Storage || !C || !PS) return;
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("C13StorageTest"));
    FVector Pos=Storage->GetActorLocation()+FVector(Test?(PS->GetPlayerId()%4)*80-120:0,Test?270:220,100);
    if (bFar) Pos.Y+=2000;
    C->SetActorLocation(Pos,false,nullptr,ETeleportType::TeleportPhysics);C->GetCharacterMovement()->SetMovementMode(MOVE_Flying);C->GetCharacterMovement()->StopMovementImmediately();
    FVector Eye;FRotator Rot;C->GetActorEyesViewPoint(Eye,Rot);Rot=(Storage->Mesh->Bounds.Origin-Eye).Rotation();SetControlRotation(Rot);ClientSetRotation(Rot,true);
#endif
}
void ABunkerPlayerController::StorageProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("C13StorageTest")),Visual=FParse::Param(FCommandLine::Get(),TEXT("C13StorageVisual"));
    if ((!Test && !Visual) || !IsLocalController() || !GetPawn()) return;
    const float T=GetWorld()->GetGameState()?GetWorld()->GetGameState()->GetServerWorldTimeSeconds():0;
    auto* Target=StorageTarget(GetWorld());if (!Target) return;
    if (Visual)
    {
        const float Times[]={3,4,5.5f,6,7,8,8.15f,8.35f,9.5f,10,11,12};
        if (StorageProbeStage>=UE_ARRAY_COUNT(Times) || T<Times[StorageProbeStage]) return;
        const int32 Step=StorageProbeStage++;
        if (Step==0) ServerPrepareStorageProbe(false);
        if (Step==1) ProbeKey(EKeys::E);
        if (Step==3 || Step==7) {if (Step==3 && !ContainerEntries.IsEmpty()) StorageProbeId=ContainerEntries[0].Id;ProbeKey(EKeys::X);}
        if (Step==5) ProbeKey(EKeys::Tab);
        if (Step==6) ProbeKey(EKeys::Down);
        if (Step==2 || Step==4 || Step==8) FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("storage_%d.png"),Step),true,false);
        if (Step==9) ProbeKey(EKeys::I);
        if (Step==10)
        {
            auto* PS=GetPlayerState<ABunkerPlayerState>();const bool Pass=PS && PS->Inventory.Num()==1 && PS->Inventory[0].ItemType==TEXT("Medkit") && Target->Contents.Num()==2 && Target->Contents.ContainsByPredicate([this](const auto& E){return E.Id==StorageProbeId;}) && !ViewedContainer && ContainerEntries.IsEmpty() && !IsLookInputIgnored() && !IsMoveInputIgnored();
            UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_VISUAL_AUDIT %s"),Pass?TEXT("PASS"):TEXT("FAIL"));
        }
        if (Step==11) FGenericPlatformMisc::RequestExit(false);
        return;
    }
    const float Times[]={4,5,6,7,9.5f,10,11,12,13,15,16,19,20,21,27,28,30,34,38,39,41,45,46};
    if (StorageProbeStage>=UE_ARRAY_COUNT(Times) || T<Times[StorageProbeStage]) return;
    const int32 Step=StorageProbeStage++;
    if (Step==0 || Step==7 || Step==14 || Step==18) ServerPrepareStorageProbe(false);
    if (Step==1 || Step==8 || Step==15 || Step==19) ProbeKey(EKeys::E);
    if (Step==2 && !ContainerEntries.IsEmpty()) {StorageProbeId=ContainerEntries[0].Id;StorageOriginalRevision=ContainerRevision;}
    if (Step==3 || Step==10 || Step==16 || Step==20) ProbeKey(EKeys::X);
    if (Step==4) ServerTransferItem(Target,StorageProbeId,true,StorageOriginalRevision);
    if (Step==5 || Step==11 || Step==17 || Step==21) {if (ViewedContainer) ProbeKey(EKeys::I);}
    if (Step==6) {bool Private=HasAuthority() || Target->Contents.IsEmpty();UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_PRIVATE value=%d closed=%d"),Private,ContainerEntries.IsEmpty() && !ViewedContainer);}
    if (Step==9) ProbeKey(EKeys::Tab);
    if (Step==12) ServerPrepareStorageProbe(true);
    if (Step==13) ServerTransferItem(Target,StorageProbeId,true,2);
    if (Step==22) UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_CLIENT_DONE closed=%d"),!ViewedContainer && ContainerEntries.IsEmpty() && !IsLookInputIgnored() && !IsMoveInputIgnored());
#endif
}
