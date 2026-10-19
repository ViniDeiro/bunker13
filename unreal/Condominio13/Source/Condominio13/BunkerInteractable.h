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
    Panel
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

    UPROPERTY(Replicated) FGuid ItemId;
    UPROPERTY(ReplicatedUsing=OnRep_State) TObjectPtr<APlayerState> Occupant;
    UFUNCTION() void OnRep_State();
    virtual void BeginPlay() override;
    UFUNCTION(BlueprintCallable)
    FString GetPrompt() const;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
