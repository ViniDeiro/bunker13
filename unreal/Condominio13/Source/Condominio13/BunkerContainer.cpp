#include "BunkerContainer.h"
#include "BunkerReferenceCabinet.h"
#include "BunkerNetwork.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "EngineUtils.h"

ABunkerContainer::ABunkerContainer()
{
    Interaction=EBunkerInteraction::Container;ActionText=FText::FromString(TEXT("abrir armazenamento"));
    DisplayName=FText::FromString(TEXT("Armário de suprimentos"));
}
void ABunkerContainer::RefreshViewers()
{
    if (!HasAuthority()) return;
    for (TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
        if (It->ServerContainer==this)
        {
            if (It->CanAccessContainer(this)) It->ClientContainerSnapshot(this,Contents,Revision);
            else {It->ServerContainer=nullptr;It->ClientCloseContainer();}
        }
}
bool ABunkerPlayerController::CanAccessContainer(ABunkerContainer* Storage) const
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();auto* C=Cast<ACharacter>(GetPawn());
    if (!IsValid(Storage) || !PS || !PS->bSessionReady || !PS->Rules || !C || PS->Health<=0 || PS->RestingBed) return false;
    FVector Eye;FRotator Rot;C->GetActorEyesViewPoint(Eye,Rot);
    const FVector Center=Storage->Mesh->Bounds.Origin;
    if (FVector::DistSquared(Eye,Center)>FMath::Square(350.f)) return false;
    FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(StorageAccess),false,C);
    const bool Block=GetWorld()->LineTraceSingleByChannel(Hit,Eye,Center,ECC_Visibility,Q);
    return !Block || Hit.GetActor()==Storage;
}
void ABunkerPlayerController::ClientContainerSnapshot_Implementation(ABunkerContainer* Storage,const TArray<FBunkerInventoryEntry>& Entries,int32 Revision)
{
    if (!IsLocalController() || !Storage) return;
    if (!bInventoryOpen) {bInventoryOpen=true;SetIgnoreLookInput(true);SetIgnoreMoveInput(true);}
    if (ViewedContainer!=Storage) {bContainerSide=true;SelectedItem=0;}
    ViewedContainer=Storage;ContainerEntries=Entries;ContainerRevision=Revision;
    UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_SNAPSHOT count=%d revision=%d"),Entries.Num(),Revision);
}
void ABunkerPlayerController::CloseContainerView()
{
    ViewedContainer=nullptr;ContainerEntries.Empty();SelectedItem=0;
    if (bInventoryOpen) {bInventoryOpen=false;SetIgnoreLookInput(false);SetIgnoreMoveInput(false);}
}
void ABunkerPlayerController::ClientCloseContainer_Implementation() {CloseContainerView();}
void ABunkerPlayerController::ServerCloseContainer_Implementation() {ServerContainer=nullptr;ClientCloseContainer();}
void ABunkerPlayerController::StorageTick(float DT)
{
    if (!HasAuthority() || !ServerContainer) return;
    StorageCheckTime-=DT;if (StorageCheckTime>0) return;StorageCheckTime=.5f;
    if (!CanAccessContainer(ServerContainer)) {ServerContainer=nullptr;ClientCloseContainer();}
}
void ABunkerPlayerController::SwitchContainerSide()
{
    if (ViewedContainer) {bContainerSide=!bContainerSide;SelectedItem=0;}
}
void ABunkerPlayerController::TransferSelected()
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (!ViewedContainer && PhysicalCabinet && PS && PS->Inventory.IsValidIndex(SelectedItem))
    {
        FVector Eye;FRotator R;GetPlayerViewPoint(Eye,R);FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(PhysicalPlace),false,GetPawn());
        GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+R.Vector()*350,ECC_Visibility,Q);
        if (Hit.GetActor()==PhysicalCabinet) ServerPhysicalTransfer(PhysicalCabinet,PhysicalCabinet->SlotFor(Hit.GetComponent()),PS->Inventory[SelectedItem].Id,PhysicalRevision,false);
        return;
    }
    if (!ViewedContainer || !PS) return;
    const auto& Entries=bContainerSide?ContainerEntries:PS->Inventory;
    if (Entries.IsValidIndex(SelectedItem)) ServerTransferItem(ViewedContainer,Entries[SelectedItem].Id,bContainerSide,ContainerRevision);
}
void ABunkerPlayerController::ServerTransferItem_Implementation(ABunkerContainer* Storage,FGuid Id,bool bTake,int32 ExpectedRevision)
{
    if (!Storage || ServerContainer!=Storage || !CanAccessContainer(Storage))
    {ServerContainer=nullptr;ClientCloseContainer();UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_REJECT access"));return;}
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
    if (ExpectedRevision!=Storage->Revision)
    {ClientContainerSnapshot(Storage,Storage->Contents,Storage->Revision);UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_REJECT stale"));return;}
    auto& Source=bTake?Storage->Contents:PS->Inventory;
    auto& Dest=bTake?PS->Inventory:Storage->Contents;
    const int32 I=Source.IndexOfByPredicate([Id](const auto& E){return E.Id==Id;});if (I==INDEX_NONE) return;
    const auto* Def=PS->Rules->Find(Source[I].ItemType);if (!Def) return;
    const int32 Slots=bTake?PS->Rules->MaxSlots:Storage->MaxSlots;
    const float Limit=bTake?PS->Rules->MaxWeightKg:Storage->MaxWeightKg;
    float Weight=0;for (const auto& E:Dest) {const auto* D=PS->Rules->Find(E.ItemType);if (!D) return;Weight+=D->WeightKg;}
    if (Dest.Num()>=Slots || Weight+Def->WeightKg>Limit)
    {ClientNotice(TEXT("Destino sem espaço ou acima do limite de peso."));UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_REJECT capacity slots=%d weight=%d"),Dest.Num()>=Slots,Weight+Def->WeightKg>Limit);return;}
    if (Dest.ContainsByPredicate([Id](const auto& E){return E.Id==Id;})) return;
    FBunkerInventoryEntry Entry=Source[I];Entry.WeightKg=Def->WeightKg;
    Dest.Add(Entry);Source.RemoveAt(I);Storage->Revision++;
    NextInventoryTime=GetWorld()->GetTimeSeconds()+PS->Rules->InventoryActionInterval;
    PS->ForceNetUpdate();Storage->RefreshViewers();
    UE_LOG(LogTemp,Display,TEXT("C13_STORAGE_MOVE take=%d id=%s revision=%d"),bTake,*Id.ToString(),Storage->Revision);
}

void ABunkerPlayerController::ClientPhysicalSnapshot_Implementation(ABunkerReferenceCabinet* Cabinet,const TArray<FBunkerInventoryEntry>& Entries,int32 Rev)
{
    if (!Cabinet) return;
    Cabinet->Present(Entries,Rev);
    if (Rev<0) {if (PhysicalCabinet==Cabinet) {PhysicalCabinet=nullptr;PhysicalEntries.Empty();PhysicalRevision=-1;}return;}
    PhysicalCabinet=Cabinet;PhysicalEntries=Entries;PhysicalRevision=Rev;
    UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_SNAPSHOT count=%d revision=%d modal=%d"),Entries.Num(),Rev,bInventoryOpen);
}
void ABunkerPlayerController::ServerPhysicalTransfer_Implementation(ABunkerReferenceCabinet* Cabinet,int32 Slot,FGuid Id,int32 Rev,bool bTake)
{
    if (GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
    if (IsValid(Cabinet) && Cabinet->Transfer(this,Slot,Id,Rev,bTake))
        NextInventoryTime=GetWorld()->GetTimeSeconds()+GetPlayerState<ABunkerPlayerState>()->Rules->InventoryActionInterval;
    else UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_REJECT slot=%d revision=%d"),Slot,Rev);
}
