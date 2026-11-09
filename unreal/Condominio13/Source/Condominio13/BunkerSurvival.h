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
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FuelInitialLiters=1.2f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float GeneratorInitialCondition=65;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float RawWaterCapacityLiters=20;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float RawWaterInitialLiters=12;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float CleanWaterInitialLiters=1.5f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float CleanWaterCapacityLiters=12;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FilterLitersPerMinute=.75f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FilterWearPerLiter=6;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float DrinkLiters=.35f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float HydrationPerLiter=100;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FuelCapacityLiters=8;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FuelCanLiters=2;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float FuelLitersPerMinute=.3f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float GeneratorWearPerMinute=3;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float GeneratorRepairGain=40;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float InfrastructureWorkSeconds=5;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="30",ClampMax="3600")) float DaySeconds=240;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float CollectionSeconds=90;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float EmergencyReleaseSeconds=12;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float EmergencyReleaseEnergy=15;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float AirlockPoweredSeconds=5;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float AirlockManualSeconds=12;
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
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float ItemUseDuration = 1.8f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float ItemPickupDuration = .55f;
    const FBunkerItemDefinition* Find(FName Type) const;
};
UCLASS()
class CONDOMINIO13_API ABunkerHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
