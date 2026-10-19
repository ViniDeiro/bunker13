#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameFramework/HUD.h"
#include "BunkerSurvival.generated.h"

USTRUCT(BlueprintType)
struct FBunkerItemDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FName ItemType;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float WeightKg = 0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FoodGain = 0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float WaterGain = 0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float HealthGain = 0;
};
UCLASS(BlueprintType)
class CONDOMINIO13_API UBunkerSurvivalRules : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FBunkerItemDefinition> Items;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float MaxWeightKg = 20;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 MaxSlots = 12;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FoodLossPerMinute = .6f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float WaterLossPerMinute = 1.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float EnergyLossPerMinute = .4f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float RestGainPerMinute = 15.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float StarvationDamagePerMinute = 4.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float ActionInterval = .2f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float TiredActionInterval = .6f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float TiredThreshold = 15;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float InventoryActionInterval = .3f;
    const FBunkerItemDefinition* Find(FName Type) const;
};
UCLASS()
class CONDOMINIO13_API ABunkerHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
