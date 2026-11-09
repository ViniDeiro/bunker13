#include "BunkerDoor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
#include "UObject/ConstructorHelpers.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundAttenuation.h"

ABunkerDoor::ABunkerDoor()
{
    PrimaryActorTick.bCanEverTick = true;
    SetReplicateMovement(false);
    SetNetUpdateFrequency(20.f);
    Hinge = CreateDefaultSubobject<USceneComponent>(TEXT("Hinge"));
    SetRootComponent(Hinge);
    Mesh->SetupAttachment(Hinge);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> DoorMesh(TEXT("/Game/Bunker/HeroKit/SM_Hero_BlastDoor.SM_Hero_BlastDoor"));
    if (DoorMesh.Succeeded()) Mesh->SetStaticMesh(DoorMesh.Object);
    LeafCollision = CreateDefaultSubobject<UBoxComponent>(TEXT("LeafCollision"));
    LeafCollision->SetupAttachment(Hinge);
    LeafCollision->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    Interaction = EBunkerInteraction::Door;
    DisplayName = FText::FromString(TEXT("Porta de contenção"));
    ActionText = FText::FromString(TEXT("abrir / fechar"));
}
void ABunkerDoor::ConfigureLeaf()
{
    Width = FMath::Clamp(Width, 80.f, 300.f);
    Height = FMath::Clamp(Height, 180.f, 350.f);
    // Keep rendered hardware separate from the thin physical leaf. A convex hull
    // around the wheel would incorrectly block narrow passages while open.
    Mesh->SetRelativeScale3D(FVector(Width/180.f, 1.f, Height/240.f));
    LeafCollision->SetRelativeLocation(FVector(Width*.5f,0,Height*.5f));
    LeafCollision->SetBoxExtent(FVector(Width*.5f,8.f,Height*.5f));
}
void ABunkerDoor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ConfigureLeaf();
    CurrentAngle = bOpen ? OpenAngle : 0.f;
    SetActorRotation(FRotator(0,ClosedYaw+CurrentAngle,0));
}
void ABunkerDoor::BeginPlay()
{
    Super::BeginPlay();
    // The comparison map retains legacy roots for future checkpoint migration,
    // while removed partitions must have no rendered or physical door leaf.
    if (ActorHasTag(TEXT("C13_OpenPlanRetiredDoor")))
    {
        Mesh->SetVisibility(false,true);Mesh->SetHiddenInGame(true,true);
        SetActorHiddenInGame(true);SetActorEnableCollision(false);SetActorTickEnabled(false);
        return;
    }
    FoleyAttenuation=NewObject<USoundAttenuation>(this);FoleyAttenuation->Attenuation.bAttenuate=true;FoleyAttenuation->Attenuation.AttenuationShapeExtents=FVector(100,0,0);FoleyAttenuation->Attenuation.FalloffDistance=600;
    ConfigureLeaf();
    if (HasAuthority()) CurrentAngle = bOpen ? OpenAngle : 0.f;
    VisualAngle = CurrentAngle;
    SetActorRotation(FRotator(0,ClosedYaw+CurrentAngle,0));
}
bool ABunkerDoor::PawnInArc(float From, float To) const
{
    FCollisionObjectQueryParams Objects(ECC_Pawn);
    FCollisionQueryParams Query(SCENE_QUERY_STAT(BunkerDoorArc),false,this);
    const int Steps=FMath::Max(1,FMath::CeilToInt(FMath::Abs(To-From)/3.f));
    for (int I=0;I<=Steps;I++)
    {
        const FQuat Rotation = FRotator(0,ClosedYaw+FMath::Lerp(From,To,float(I)/Steps),0).Quaternion();
        const FVector Center = GetActorLocation()+Rotation.RotateVector(FVector(Width*.5f,0,Height*.5f));
        if (GetWorld()->OverlapAnyTestByObjectType(Center,Rotation,Objects,
            FCollisionShape::MakeBox(FVector(Width*.5f+3,11,Height*.5f)),Query)) return true;
    }
    return false;
}
bool ABunkerDoor::TryToggle()
{
    if (!HasAuthority() || bRoundLocked || GetWorld()->GetTimeSeconds()<NextToggleTime) return false;
    const float Goal = bOpen ? 0.f : OpenAngle;
    if (PawnInArc(CurrentAngle,Goal)) return false;
    bOpen = !bOpen;PlayFoley(bOpen);
    NextToggleTime = GetWorld()->GetTimeSeconds()+1.5;
    ForceNetUpdate();
    UE_LOG(LogTemp,Display,TEXT("C13_DOOR_COMMAND name=%s open=%d"),*GetName(),bOpen);
    return true;
}
void ABunkerDoor::Tick(float DT)
{
    Super::Tick(DT);
    if (HasAuthority())
    {
        const float Next = FMath::FInterpConstantTo(CurrentAngle,bOpen?OpenAngle:0.f,DT,75.f);
        // Also stop if a player enters the arc after the action was accepted.
        if (!FMath::IsNearlyEqual(Next,CurrentAngle) && !PawnInArc(CurrentAngle,Next)) CurrentAngle=Next;
        VisualAngle=CurrentAngle;
    }
    else VisualAngle=FMath::FInterpConstantTo(VisualAngle,CurrentAngle,DT,180.f);
    SetActorRotation(FRotator(0,ClosedYaw+VisualAngle,0));
}
void ABunkerDoor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ABunkerDoor,Width);
    DOREPLIFETIME(ABunkerDoor,Height);
    DOREPLIFETIME(ABunkerDoor,ClosedYaw);
    DOREPLIFETIME(ABunkerDoor,OpenAngle);
    DOREPLIFETIME(ABunkerDoor,bOpen);
    DOREPLIFETIME(ABunkerDoor,CurrentAngle);
    DOREPLIFETIME(ABunkerDoor,bRoundLocked);
}

void ABunkerDoor::PlayFoley_Implementation(bool bOpening)
{
    auto* Sound=LoadObject<USoundBase>(nullptr,bOpening?TEXT("/Game/Bunker/ReferenceRoom/Audio/S_Cabinet_Open.S_Cabinet_Open"):TEXT("/Game/Bunker/ReferenceRoom/Audio/S_Cabinet_Close.S_Cabinet_Close"));
    if(Sound)UGameplayStatics::PlaySoundAtLocation(this,Sound,GetActorTransform().TransformPosition(FVector(Width*.85f,0,Height*.5f)),.6f,.72f,0.f,FoleyAttenuation);
}
