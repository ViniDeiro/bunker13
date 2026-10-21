#include "BunkerNetwork.h"
#include "BunkerContainer.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

namespace
{
bool Test()
{
#if !UE_BUILD_SHIPPING
    return FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectTest"));
#else
    return false;
#endif
}
TArray<ABunkerInteractable*> Resources(UWorld* World)
{
    TArray<ABunkerInteractable*> Result;
    for(TActorIterator<ABunkerInteractable> It(World);It;++It)
        if (!It->WorldKey.IsEmpty() && It->Interaction==EBunkerInteraction::Pickup) Result.Add(*It);
    Result.Sort([](const auto& A,const auto& B){return A.WorldKey<B.WorldKey;});return Result;
}
FBunkerInventoryEntry TakeFixture(ABunkerInteractable* Actor,ABunkerPlayerState* PS,int32 ProbeIndex)
{
    FBunkerInventoryEntry E;E.Id=FGuid(13,77,ProbeIndex,1);E.Name=Actor->DisplayName.ToString();E.ItemType=Actor->ItemType;
    E.WorldMesh=Actor->Mesh->GetStaticMesh();E.WorldScale=Actor->GetActorScale3D();E.WeightKg=PS->Rules->Find(E.ItemType)->WeightKg;
    for(int32 I=0;I<Actor->Mesh->GetNumMaterials();++I) E.Materials.Add(Actor->Mesh->GetMaterial(I));
    Actor->ItemId=E.Id;Actor->bActive=false;Actor->OnRep_State();Actor->ForceNetUpdate();return E;
}
}
void ABunkerPlayerController::ServerReconnectProbe_Implementation(int32 ProbeIndex)
{
#if !UE_BUILD_SHIPPING
    auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();auto* PS=GetPlayerState<ABunkerPlayerState>();
    FString Stage;FParse::Value(FCommandLine::Get(),TEXT("C13ReconnectStage="),Stage);
    if (!Test() || Stage!=TEXT("seed") || !GM || !PS || !PS->bSessionReady) return;
    if (ProbeIndex==-1 && GM->RemotePlayers.Num()==3)
    {
        ABunkerContainer* Box=nullptr;for(TActorIterator<ABunkerContainer> It(GetWorld());It;++It) if(!It->Contents.IsEmpty()) {Box=*It;break;}
        if (Box && !GM->RemotePlayers[0].Inventory.IsEmpty())
        {
            const auto Duplicate=GM->RemotePlayers[0].Inventory[0];Box->Contents.Add(Duplicate);
            const int64 Before=GM->SaveSequence;const bool Rejected=!GM->SaveCheckpoint() && GM->SaveSequence==Before;
            Box->Contents.Pop();UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_DUPLICATE_SAVE rejected=%d"),Rejected);
        }
        UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_QUIT requested=1"));FPlatformMisc::RequestExit(false);return;
    }
    if (!PS->Inventory.IsEmpty() || ProbeIndex<1 || ProbeIndex>3) return;
    auto Items=Resources(GetWorld());if (Items.Num()!=6 || !Items[ProbeIndex]->bActive) return;
    PS->Inventory.Add(TakeFixture(Items[ProbeIndex],PS,ProbeIndex));
    PS->Health=51+ProbeIndex;PS->Food=40+ProbeIndex;PS->Water=30+ProbeIndex;PS->Energy=20+ProbeIndex;
    if (ProbeIndex==1)
    {
        for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It) if(It->Interaction==EBunkerInteraction::Bed && !It->Occupant)
        {
            RestExit=GetPawn()->GetActorLocation();PS->RestingBed=*It;It->Occupant=PS;It->ForceNetUpdate();
            Cast<ACharacter>(GetPawn())->GetCharacterMovement()->DisableMovement();break;
        }
    }
    PS->ForceNetUpdate();
    const bool Saved=GM->SaveCheckpoint();
    UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_PREPARED role=%d saved=%d items=%d"),ProbeIndex,Saved,PS->Inventory.Num());
#endif
}
void ABunkerPlayerController::ReconnectProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    if (!Test() || !IsLocalController() || GetNetMode()!=NM_Client) return;
    auto* PS=GetPlayerState<ABunkerPlayerState>();if (!PS || !PS->bSessionReady) return;
    int32 ProbeIndex=0;FParse::Value(FCommandLine::Get(),TEXT("C13ReconnectProfile="),ProbeIndex);
    if (ProbeIndex<1 || ProbeIndex>3) return;
    if (ReconnectProbeStage==0)
    {
        if (!FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectCheck"))) ServerReconnectProbe(ProbeIndex);
        ReconnectProbeStage=1;ReconnectProbeTime=0;
    }
    if (ReconnectProbeStage!=1) return;
    ReconnectProbeTime+=DT;if (ReconnectProbeTime<1) return;
    bool Private=true;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) if(*It!=PS) Private&=It->Inventory.IsEmpty();
    bool Pass=PS->Inventory.Num()==1 && PS->Inventory[0].Id==FGuid(13,77,ProbeIndex,1) && PS->Inventory[0].WorldMesh &&
        PS->Health==51+ProbeIndex && FMath::Abs(PS->Food-(40+ProbeIndex))<2 && FMath::Abs(PS->Water-(30+ProbeIndex))<2 &&
        FMath::Abs(PS->Energy-(20+ProbeIndex))<4 && !ViewedContainer && !bInventoryOpen && Private;
    UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_CLIENT %s role=%d items=%d private=%d controls=%d"),Pass?TEXT("PASS"):TEXT("FAIL"),ProbeIndex,PS->Inventory.Num(),Private,!bInventoryOpen);
    ReconnectProbeStage=2;
    if (Pass && FParse::Param(FCommandLine::Get(),TEXT("C13ReconnectShutdown"))) ServerReconnectProbe(-1);
#endif
}
void ABunkerGameMode::StartReconnectValidation()
{
#if !UE_BUILD_SHIPPING
    if (!Test()) return;
    FString Stage;FParse::Value(FCommandLine::Get(),TEXT("C13ReconnectStage="),Stage);
    auto* PC=Cast<ABunkerPlayerController>(GetWorld()->GetFirstPlayerController());auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
    if (!PS) return;
    if (Stage==TEXT("seed"))
    {
        auto Items=Resources(GetWorld());ABunkerContainer* Box=nullptr;
        for(TActorIterator<ABunkerContainer> It(GetWorld());It;++It) if(!Box || It->WorldKey<Box->WorldKey) Box=*It;
        if (Items.Num()!=6 || !Box) return;
        PS->Inventory.Add(TakeFixture(Items[0],PS,0));PS->Health=60;
        Box->Contents.Add(TakeFixture(Items[4],PS,4));
        const auto Drop=TakeFixture(Items[5],PS,5);PS->Inventory.Add(Drop);PC->ServerDropItem(Drop.Id);
        PS->ForceNetUpdate();SaveCheckpoint();
        UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_HOST prepared=1"));
    }
    FTimerHandle Audit;
    GetWorldTimerManager().SetTimer(Audit,FTimerDelegate::CreateWeakLambda(this,[this]()
    {
        if (RemotePlayers.Num()!=3) return;
        for(const auto& R:RemotePlayers) if(R.Inventory.Num()!=1) return;
        bool Positions=true;for(const auto& R:RemotePlayers) Positions&=!R.Location.IsNearlyZero();
        TSet<FGuid> Unique;int32 Total=0,Ready=0,Beds=0,Stored=0,Dropped=0;
        auto Add=[&](const auto& Entries){for(const auto& E:Entries){++Total;Unique.Add(E.Id);}};
        auto* Host=Cast<ABunkerPlayerController>(GetWorld()->GetFirstPlayerController());auto* HostState=Host?Host->GetPlayerState<ABunkerPlayerState>():nullptr;
        if(!HostState) return;Add(HostState->Inventory);
        for(const auto& R:RemotePlayers) Add(R.Inventory);
        for(TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
            if(It->SessionPlayerKey.IsValid() && It->GetPlayerState<ABunkerPlayerState>()->bSessionReady) ++Ready;
        for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
        {
            Beds+=It->Interaction==EBunkerInteraction::Bed && It->Occupant!=nullptr;
            if(auto* C=Cast<ABunkerContainer>(*It)) {Stored+=C->Contents.Num();Add(C->Contents);}
            if(It->Interaction==EBunkerInteraction::Pickup && It->bActive) {++Dropped;++Total;Unique.Add(It->ItemId);}
        }
        const bool Pass=Positions && Total==6 && Unique.Num()==6 && Stored==1 && Dropped==1 && HostState->Inventory.Num()==1;
        UE_LOG(LogTemp,Display,TEXT("C13_RECONNECT_AUDIT %s ready=%d beds=%d unique=%d roster=%d stored=%d dropped=%d"),Pass?TEXT("PASS"):TEXT("FAIL"),Ready,Beds,Unique.Num(),RemotePlayers.Num(),Stored,Dropped);
    }),1,true);
#endif
}
