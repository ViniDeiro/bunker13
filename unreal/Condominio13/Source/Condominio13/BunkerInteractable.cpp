#include "BunkerInteractable.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
#include "UObject/ConstructorHelpers.h"

ABunkerInteractable::ABunkerInteractable()
{
    bReplicates = true;
    SetReplicateMovement(true);
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (Cube.Succeeded()) Mesh->SetStaticMesh(Cube.Object);
    Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
    DisplayName = FText::FromString(TEXT("Objeto"));
    ActionText = FText::FromString(TEXT("usar"));
}

FString ABunkerInteractable::GetPrompt() const
{
    return FString::Printf(TEXT("[E] %s — %s"), *ActionText.ToString(), *DisplayName.ToString());
}

void ABunkerInteractable::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ABunkerInteractable, bActive);
    DOREPLIFETIME(ABunkerInteractable, ItemId);
    DOREPLIFETIME(ABunkerInteractable, ItemType);
    DOREPLIFETIME(ABunkerInteractable, PickupMesh);
    DOREPLIFETIME(ABunkerInteractable, PickupMaterials);
    DOREPLIFETIME(ABunkerInteractable, PickupScale);
    DOREPLIFETIME(ABunkerInteractable, Interaction);
    DOREPLIFETIME(ABunkerInteractable, DisplayName);
    DOREPLIFETIME(ABunkerInteractable, ActionText);
    DOREPLIFETIME(ABunkerInteractable, Occupant);
}

void ABunkerInteractable::BeginPlay()
{
    Super::BeginPlay();
    if (HasAuthority() && !ItemId.IsValid()) ItemId = FGuid::NewGuid();
    OnRep_State();
}
void ABunkerInteractable::OnRep_State()
{
    if (Interaction == EBunkerInteraction::Pickup)
    {
        SetActorHiddenInGame(!bActive);
        SetActorEnableCollision(bActive);
    }
}

void ABunkerInteractable::OnRep_Visual()
{
    if (!PickupMesh) return;
    Mesh->SetStaticMesh(PickupMesh);
    SetActorScale3D(PickupScale);
    for (int32 I=0;I<PickupMaterials.Num();I++) Mesh->SetMaterial(I,PickupMaterials[I]);
}
