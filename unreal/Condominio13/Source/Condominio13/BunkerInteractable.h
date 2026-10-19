#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerInteractable.generated.h"

UENUM(BlueprintType)
enum class EBunkerInteraction : uint8
{
    Pickup,
    Bed,
    Darts,
    Generator,
    Radio,
    Panel,
    Door,
    Container
};

UCLASS(Blueprintable)
class CONDOMINIO13_API ABunkerInteractable : public AActor
{
    GENERATED_BODY()

public:
    ABunkerInteractable();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Replicated, Category="Interaction")
    EBunkerInteraction Interaction = EBunkerInteraction::Pickup;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Replicated, Category="Interaction")
    FText DisplayName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Replicated, Category="Interaction")
    FText ActionText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, ReplicatedUsing=OnRep_State, Category="Interaction")
    bool bActive = true;

    UPROPERTY(EditAnywhere,BlueprintReadWrite,Replicated) FName ItemType = TEXT("Generic");
    UPROPERTY(ReplicatedUsing=OnRep_Visual) TObjectPtr<UStaticMesh> PickupMesh;
    UPROPERTY(ReplicatedUsing=OnRep_Visual) TArray<TObjectPtr<UMaterialInterface>> PickupMaterials;
    UPROPERTY(ReplicatedUsing=OnRep_Visual) FVector PickupScale = FVector::OneVector;
    UFUNCTION() void OnRep_Visual();
    UPROPERTY(Replicated) FGuid ItemId;
    UPROPERTY(ReplicatedUsing=OnRep_State) TObjectPtr<APlayerState> Occupant;
    UFUNCTION() void OnRep_State();
    virtual void BeginPlay() override;
    UFUNCTION(BlueprintCallable)
    FString GetPrompt() const;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
