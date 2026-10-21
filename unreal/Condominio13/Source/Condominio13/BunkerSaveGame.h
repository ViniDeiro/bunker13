#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "BunkerInventoryTypes.h"
#include "BunkerSaveGame.generated.h"

USTRUCT()
struct FBunkerSavedActor
{
    GENERATED_BODY()
    UPROPERTY() FString Key;
    UPROPERTY() uint8 Kind=0;
    UPROPERTY() bool Active=true;
    UPROPERTY() float DoorAngle=0;
    UPROPERTY() FTransform Transform;
    UPROPERTY() FBunkerInventoryEntry Item;
    UPROPERTY() TArray<FBunkerInventoryEntry> Contents;
};

// Explicit version boundary: incompatible layouts are rejected before world mutation.
UCLASS()
class CONDOMINIO13_API UBunkerSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY() int32 Version=1;
    UPROPERTY() int64 Sequence=0;
    UPROPERTY() FString Layout;
    UPROPERTY() TArray<FBunkerInventoryEntry> Inventory;
    UPROPERTY() float Health=100;
    UPROPERTY() float Food=100;
    UPROPERTY() float Water=100;
    UPROPERTY() float Energy=100;
    UPROPERTY() FVector PlayerLocation;
    UPROPERTY() FRotator PlayerRotation;
    UPROPERTY() TArray<FBunkerSavedActor> Actors;
};
