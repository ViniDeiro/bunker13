#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "BunkerInventoryTypes.h"
#include "BunkerInfrastructure.h"
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

USTRUCT()
struct FBunkerSavedPlayer
{
    GENERATED_BODY()
    UPROPERTY() FGuid Key;
    UPROPERTY() FString TicketHash;
    UPROPERTY() TArray<FBunkerInventoryEntry> Inventory;
    UPROPERTY() float Health=100;
    UPROPERTY() float Food=100;
    UPROPERTY() float Water=100;
    UPROPERTY() float Energy=100;
    UPROPERTY() FVector Location=FVector::ZeroVector;
    UPROPERTY() FRotator Rotation=FRotator::ZeroRotator;
};

UCLASS()
class CONDOMINIO13_API UBunkerReconnectProfile : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY() int32 Version=1;
    UPROPERTY() int64 Generation=0;
    UPROPERTY() TMap<FString,FString> Tickets;
};

// Explicit version boundary: incompatible layouts are rejected before world mutation.
UCLASS()
class CONDOMINIO13_API UBunkerSaveGame : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY() int32 Version=1;
    UPROPERTY() int64 Sequence=0;
    UPROPERTY() bool bExternalSupplies=false;
    UPROPERTY() bool bInfrastructure=false;
    UPROPERTY() FBunkerInfrastructureState Infrastructure;
    UPROPERTY() bool bRoundMode=false;
    UPROPERTY() uint8 RoundPhase=0;
    UPROPERTY() float RoundRemaining=0;
    UPROPERTY() bool bRoundRecoveryOpen=false;
    UPROPERTY() double ShelterSeconds=0;
    UPROPERTY() float ShelterDaySeconds=240;
    UPROPERTY() FString Layout;
    UPROPERTY() FGuid CampaignId;
    UPROPERTY() TArray<FBunkerSavedPlayer> RemotePlayers;
    UPROPERTY() TArray<FBunkerInventoryEntry> Inventory;
    UPROPERTY() float Health=100;
    UPROPERTY() float Food=100;
    UPROPERTY() float Water=100;
    UPROPERTY() float Energy=100;
    UPROPERTY() FVector PlayerLocation;
    UPROPERTY() FRotator PlayerRotation;
    UPROPERTY() TArray<FBunkerSavedActor> Actors;
};
