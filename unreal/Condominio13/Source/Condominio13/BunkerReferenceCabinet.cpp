#include "BunkerReferenceCabinet.h"
#include "BunkerNetwork.h"
#include "BunkerObservedAction.h"
#include "BunkerItemPresentation.h"
#include "GameFramework/GameStateBase.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "EngineUtils.h"
#include "Engine/StaticMesh.h"
#include "Sound/SoundAttenuation.h"

ABunkerReferenceCabinet::ABunkerReferenceCabinet()
{
    PrimaryActorTick.bCanEverTick=true;bReplicates=true;SetReplicateMovement(false);SetNetUpdateFrequency(20);
    Anchor=CreateDefaultSubobject<USceneComponent>(TEXT("Anchor"));SetRootComponent(Anchor);
    Mesh->SetupAttachment(Anchor);Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Hinge=CreateDefaultSubobject<USceneComponent>(TEXT("DoorHinge"));Hinge->SetupAttachment(Anchor);Hinge->SetRelativeLocation(FVector(-57.6f,27,0));
    Leaf=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Leaf"));Leaf->SetupAttachment(Hinge);Leaf->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    DoorCollision=CreateDefaultSubobject<UBoxComponent>(TEXT("LeafCollision"));DoorCollision->SetupAttachment(Hinge);DoorCollision->SetBoxExtent(FVector(57.6f,2,94));DoorCollision->SetRelativeLocation(FVector(57.6f,0,100));DoorCollision->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    auto Wall=[this](const TCHAR* N,FVector P,FVector Ext)
    {auto* B=CreateDefaultSubobject<UBoxComponent>(N);B->SetupAttachment(Anchor);B->SetRelativeLocation(P);B->SetBoxExtent(Ext);B->SetCollisionProfileName(TEXT("BlockAllDynamic"));};
    Wall(TEXT("BackCollision"),FVector(0,-26,100),FVector(60,1,96));
    Wall(TEXT("LeftCollision"),FVector(-59,0,100),FVector(1,27,96));Wall(TEXT("RightCollision"),FVector(59,0,100),FVector(1,27,96));
    for (int32 I=0;I<5;I++) Wall(*FString::Printf(TEXT("ShelfCollision%d"),I),FVector(0,0,5+45*I),FVector(59,27,1.2));
    for (int32 I=0;I<12;I++)
    {
        const FVector P(-40+40*(I%3),0,6.15f+45*(I/3));
        auto* B=CreateDefaultSubobject<UBoxComponent>(*FString::Printf(TEXT("SlotQuery%d"),I));B->SetupAttachment(Anchor);B->SetRelativeLocation(P+FVector(0,10,13));B->SetBoxExtent(FVector(16,15,15));
        B->SetCollisionEnabled(ECollisionEnabled::QueryOnly);B->SetCollisionResponseToAllChannels(ECR_Ignore);B->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);Slots.Add(B);
        auto* D=CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("SlotVisual%d"),I));D->SetupAttachment(Anchor);D->SetRelativeLocation(P);D->SetCollisionEnabled(ECollisionEnabled::NoCollision);Displays.Add(D);
    }
    MaxSlots=12;MaxWeightKg=30;DisplayName=FText::FromString(TEXT("Armário da convivência"));ActionText=FText::FromString(TEXT("abrir / fechar | E no item: pegar | X no espaço: guardar"));
}
void ABunkerReferenceCabinet::BeginPlay()
{
    Super::BeginPlay();WorldKey=TEXT("C13_Reference_CommonCabinet_v1");NormalizeSlots();UpdateQueries(Contents);
    FoleyAttenuation=NewObject<USoundAttenuation>(this);FoleyAttenuation->Attenuation.bAttenuate=true;FoleyAttenuation->Attenuation.AttenuationShapeExtents=FVector(75,0,0);FoleyAttenuation->Attenuation.FalloffDistance=450;
    VisualAngle=DoorAngle;
}
bool ABunkerReferenceCabinet::ValidSlots(const TArray<FBunkerInventoryEntry>& Entries) const
{
    TSet<int32> Seen;
    for (const auto& E:Entries) {if (E.StorageSlot<0 || E.StorageSlot>=12 || Seen.Contains(E.StorageSlot)) return false;Seen.Add(E.StorageSlot);}
    return true;
}
void ABunkerReferenceCabinet::NormalizeSlots()
{
    TSet<int32> Used;for (const auto& E:Contents) if (E.StorageSlot>=0) Used.Add(E.StorageSlot);
    for (auto& E:Contents) if (E.StorageSlot<0) for (int32 I=0;I<12;I++) if (!Used.Contains(I)) {E.StorageSlot=I;Used.Add(I);break;}
}
int32 ABunkerReferenceCabinet::SlotFor(const UPrimitiveComponent* C) const {return Slots.IndexOfByPredicate([C](const auto& S){return S==C;});}
FVector ABunkerReferenceCabinet::SlotPoint(int32 I) const
{return GetActorTransform().TransformPosition(FVector(-40+40*(I%3),0,6.15f+45*(I/3)));}
FVector ABunkerReferenceCabinet::ItemPoint(int32 I) const
{
    FVector P(-40+40*(I%3),0,6.15f+45*(I/3));
    if(const auto* E=Contents.FindByPredicate([I](const auto& V){return V.StorageSlot==I;}))if(E->WorldMesh){const auto B=E->WorldMesh->GetBounds();P+=(B.Origin-FVector(0,0,B.Origin.Z-B.BoxExtent.Z))*E->WorldScale;}
    return GetActorTransform().TransformPosition(P);
}
void ABunkerReferenceCabinet::UpdateQueries(const TArray<FBunkerInventoryEntry>& Entries)
{
    for(int I=0;I<Slots.Num();I++)
    {
        FVector P(-40+40*(I%3),0,6.15f+45*(I/3));FVector Center=P+FVector(0,8,12),Extent(16,15,14);
        if(const auto* E=Entries.FindByPredicate([I](const auto& V){return V.StorageSlot==I;}))if(E->WorldMesh)
        {const auto B=E->WorldMesh->GetBounds();Center=P+(B.Origin-FVector(0,0,B.Origin.Z-B.BoxExtent.Z))*E->WorldScale;Extent=B.BoxExtent*E->WorldScale+FVector(2);Extent.X=FMath::Clamp(Extent.X,4.f,16.f);Extent.Y=FMath::Clamp(Extent.Y,4.f,15.f);Extent.Z=FMath::Clamp(Extent.Z,4.f,20.f);}
        Slots[I]->SetRelativeLocation(Center);Slots[I]->SetBoxExtent(Extent);
    }
}
bool ABunkerReferenceCabinet::Blocked(float From,float To) const
{
    FCollisionObjectQueryParams O(ECC_Pawn);FCollisionQueryParams Q(SCENE_QUERY_STAT(CabinetArc),false,this);
    for (int I=0;I<=FMath::CeilToInt(FMath::Abs(To-From)/3);I++)
    {
        const float A=FMath::Lerp(From,To,float(I)/FMath::Max(1,FMath::CeilToInt(FMath::Abs(To-From)/3)));
        FTransform T(FRotator(0,A,0),FVector(-57.6f,27,0));T=T*GetActorTransform();
        if (GetWorld()->OverlapAnyTestByObjectType(T.TransformPosition(FVector(57.6f,0,100)),T.GetRotation(),O,FCollisionShape::MakeBox(FVector(59.6f,5,94)),Q)) return true;
    }
    return false;
}
bool ABunkerReferenceCabinet::ToggleDoor()
{
    const float Goal=bDoorOpen?0:110;
    if (!HasAuthority() || GetWorld()->GetTimeSeconds()<NextToggle || Blocked(DoorAngle,Goal)) return false;
    bDoorOpen=!bDoorOpen;NextToggle=GetWorld()->GetTimeSeconds()+1.2;PlayDoorSound(bDoorOpen);ForceNetUpdate();return true;
}
void ABunkerReferenceCabinet::PlayDoorSound_Implementation(bool bOpening)
{if (auto* S=bOpening?OpenSound.Get():CloseSound.Get()) UGameplayStatics::PlaySoundAtLocation(this,S,GetActorLocation(),.65f,1.f,0.f,FoleyAttenuation);}
void ABunkerReferenceCabinet::Present(const TArray<FBunkerInventoryEntry>& Entries,int32 NewRevision)
{
    UpdateQueries(Entries);
    for (int I=0;I<Displays.Num();I++) {Displays[I]->SetStaticMesh(nullptr);Displays[I]->SetRelativeLocation(FVector(-40+40*(I%3),0,6.15f+45*(I/3)));}
    for (const auto& E:Entries) if (Displays.IsValidIndex(E.StorageSlot) && E.WorldMesh)
    {
        auto* D=Displays[E.StorageSlot].Get();D->SetStaticMesh(E.WorldMesh);D->EmptyOverrideMaterials();
        for (int32 I=0;I<E.Materials.Num();I++) D->SetMaterial(I,E.Materials[I]);
        const auto B=E.WorldMesh->GetBounds();D->AddLocalOffset(FVector(0,0,-(B.Origin.Z-B.BoxExtent.Z)*E.WorldScale.Z));
        D->SetRelativeScale3D(E.WorldScale);D->SetLightingChannels(false,false,true);
        // Existing item pivots are at their base. Preserve physical scale.
    }
}
bool ABunkerReferenceCabinet::CanObserve(ABunkerPlayerController* PC) const
{
    auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;auto* C=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
    if(!PS || !PS->bSessionReady || PS->Health<=0 || !C)return false;
    FVector Eye;FRotator R;C->GetActorEyesViewPoint(Eye,R);const FVector Center=Mesh->Bounds.Origin;
    if(FVector::DistSquared(Eye,Center)>900.f*900.f)return false;
    FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(PhysicalObserver),false,C);
    return !GetWorld()->LineTraceSingleByChannel(Hit,Eye,Center,ECC_Visibility,Q) || Hit.GetActor()==this;
}
void ABunkerReferenceCabinet::Tick(float DT)
{
    Super::Tick(DT);
    if (HasAuthority())
    {
        const float N=FMath::FInterpConstantTo(DoorAngle,bDoorOpen?110.f:0.f,DT,95.f);
        if (!Blocked(DoorAngle,N)) DoorAngle=N;
        VisualAngle=DoorAngle;
        ObserverClock-=DT;
        if (ObserverClock<=0)
        {
            ObserverClock=.2;UpdateQueries(Contents);
            for (TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)
            {
                const bool Eligible=DoorAngle>75 && CanObserve(*It);
                auto Key=TWeakObjectPtr<ABunkerPlayerController>(*It);
                if (Eligible && (!Observers.Contains(Key) || Observers[Key]!=Revision))
                {It->ClientPhysicalSnapshot(this,Contents,Revision);Observers.Add(Key,Revision);}
                else if (!Eligible && Observers.Contains(Key)) {It->ClientPhysicalSnapshot(this,{},-1);Observers.Remove(Key);}
            }
            for (auto It=Observers.CreateIterator();It;++It) if (!It.Key().IsValid()) It.RemoveCurrent();
        }
    }
    else VisualAngle=FMath::FInterpConstantTo(VisualAngle,DoorAngle,DT,200.f);
    Hinge->SetRelativeRotation(FRotator(0,VisualAngle,0));
    // A stored unit has one canonical owner immediately, but is not drawn twice
    // while the hand is still carrying its cosmetic representation to the shelf.
    const float ServerTime=GetWorld()->GetGameState()?GetWorld()->GetGameState()->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();
    for(auto Display:Displays)
    {
        bool Held=false;
        for(TActorIterator<ABunkerObservedAction> A(GetWorld());A;++A)
            if(A->Kind==1 && A->ContactTarget==this && ServerTime-A->Start<A->Duration*.88f && FVector::DistSquared(A->Contact,Display->GetComponentLocation())<16)Held=true;
        for(TActorIterator<ABunkerPlayerController> PC(GetWorld());PC;++PC)if(PC->IsLocalController() && PC->ItemPresentation)
        {auto* A=PC->ItemPresentation.Get();if(A->bPlaying && A->bPlace && A->ContactActor==this && A->Elapsed<A->Length*.88f && FVector::DistSquared(A->ContactPoint,Display->GetComponentLocation())<16)Held=true;}
        Display->SetVisibility(!Held && Display->GetStaticMesh()!=nullptr);
    }
}
bool ABunkerReferenceCabinet::Transfer(ABunkerPlayerController* PC,int32 Slot,FGuid Id,int32 ExpectedRevision,bool bTake)
{
    auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
    if (!HasAuthority() || !PS || GetWorld()->GetTimeSeconds()<NextTransfer || !PC->CanAccessContainer(this) || DoorAngle<100 || !bDoorOpen || !Slots.IsValidIndex(Slot) || ExpectedRevision!=Revision) return false;
    auto* C=Cast<ACharacter>(PC->GetPawn());FMinimalViewInfo V;C->CalcCamera(0,V);FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(PhysicalTransfer),false,C);
    if (!GetWorld()->LineTraceSingleByChannel(Hit,V.Location,V.Location+PC->GetControlRotation().Vector()*350,ECC_Visibility,Q) || Hit.GetActor()!=this || SlotFor(Hit.GetComponent())!=Slot) return false;
    auto& Src=bTake?Contents:PS->Inventory;auto& Dst=bTake?PS->Inventory:Contents;
    const int32 I=Src.IndexOfByPredicate([&](const auto& E){return E.Id==Id && (!bTake || E.StorageSlot==Slot);});
    if (I<0 || Dst.ContainsByPredicate([&](const auto& E){return E.Id==Id || (!bTake && E.StorageSlot==Slot);})) return false;
    const auto* Def=PS->Rules->Find(Src[I].ItemType);if (!Def) return false;
    float Weight=0;for (const auto& E:Dst) {auto* D=PS->Rules->Find(E.ItemType);if (!D) return false;Weight+=D->WeightKg;}
    if (Dst.Num()>=(bTake?PS->Rules->MaxSlots:MaxSlots) || Weight+Def->WeightKg>(bTake?PS->Rules->MaxWeightKg:MaxWeightKg)) return false;
    auto E=Src[I];E.WeightKg=Def->WeightKg;E.StorageSlot=bTake?-1:Slot;
    Dst.Add(E);Src.RemoveAt(I);Revision++;UpdateQueries(Contents);NextTransfer=GetWorld()->GetTimeSeconds()+.95f;PS->ForceNetUpdate();
    PC->ClientPhysicalSnapshot(this,Contents,Revision);
    const auto Bounds=E.WorldMesh->GetBounds();const FVector Pivot=SlotPoint(Slot)-GetActorQuat().RotateVector(FVector(0,0,(Bounds.Origin.Z-Bounds.BoxExtent.Z)*E.WorldScale.Z));
    PC->ClientReachAction(E,Pivot,!bTake,false,this);
    ABunkerObservedAction::StartFor(PC,E,Pivot,bTake?0:1,.95f,this);
    UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_MOVE take=%d slot=%d id=%s revision=%d"),bTake,Slot,*Id.ToString(),Revision);
    return true;
}
void ABunkerReferenceCabinet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ABunkerReferenceCabinet,bDoorOpen);DOREPLIFETIME(ABunkerReferenceCabinet,DoorAngle);}
