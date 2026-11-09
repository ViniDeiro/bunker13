#pragma once
#include "CoreMinimal.h"
#include "BunkerInventoryTypes.generated.h"

class UStaticMesh;
class UMaterialInterface;

USTRUCT(BlueprintType)
struct FBunkerInventoryEntry
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FGuid Id;
    UPROPERTY() int32 StorageSlot=-1;
    UPROPERTY(BlueprintReadOnly) FString Name;
    UPROPERTY(BlueprintReadOnly) FName ItemType;
    UPROPERTY(BlueprintReadOnly) float WeightKg = 0;
    UPROPERTY() TObjectPtr<UStaticMesh> WorldMesh;
    UPROPERTY() TArray<TObjectPtr<UMaterialInterface>> Materials;
    UPROPERTY() FVector WorldScale = FVector::OneVector;
};
