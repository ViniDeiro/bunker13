#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "BunkerSurvival.h"
#include "BunkerInventoryTypes.h"
#include "BunkerNetwork.generated.h"
class ABunkerInteractable;
class ABunkerContainer;
class ABunkerItemPresentation;

UCLASS()
class CONDOMINIO13_API ABunkerPlayerState : public APlayerState
{
    GENERATED_BODY()
public:
    UPROPERTY(Replicated, BlueprintReadOnly) TArray<FBunkerInventoryEntry> Inventory;
    UPROPERTY(ReplicatedUsing=OnRep_RestingBed, BlueprintReadOnly) TObjectPtr<ABunkerInteractable> RestingBed;
    UPROPERTY(Replicated,BlueprintReadOnly) float Health = 100;
    UPROPERTY(Replicated,BlueprintReadOnly) float Food = 100;
    UPROPERTY(Replicated,BlueprintReadOnly) float Water = 100;
    UPROPERTY(Replicated,BlueprintReadOnly) float Energy = 100;
    UPROPERTY() TObjectPtr<UBunkerSurvivalRules> Rules;
    float Weight() const;
    virtual void BeginPlay() override;
    virtual void Tick(float DT) override;
    ABunkerPlayerState();
    UFUNCTION() void OnRep_RestingBed();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
};

UCLASS()
class CONDOMINIO13_API ABunkerPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    ABunkerPlayerController();
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
    virtual void PlayerTick(float DeltaSeconds) override;
    UFUNCTION(Server, Reliable) void ServerInteract(ABunkerInteractable* Target);
    UFUNCTION(Server, Reliable) void ServerLeaveBed();
    UFUNCTION(Client, Reliable) void ClientNotice(const FString& Message);
    UFUNCTION(Exec) void C13Save();
    UFUNCTION(Exec) void C13Host();
    UFUNCTION(Exec) void C13Join(const FString& Address);
    void ReleaseBed(bool bDisconnect = false);
    FVector CheckpointLocation() const;
    UFUNCTION(Server,Reliable) void ServerUseItem(FGuid Id);
    UFUNCTION(Server,Reliable) void ServerDropItem(FGuid Id);
    UFUNCTION(Client,Reliable) void ClientPlayItemAction(const FBunkerInventoryEntry& Entry,bool bConsume);
    UPROPERTY() TObjectPtr<ABunkerItemPresentation> ItemPresentation;
    UFUNCTION(Server,Reliable) void ServerTransferItem(ABunkerContainer* Container,FGuid Id,bool bTake,int32 Revision);
    UFUNCTION(Server,Reliable) void ServerCloseContainer();
    UFUNCTION(Client,Reliable) void ClientContainerSnapshot(ABunkerContainer* Container,const TArray<FBunkerInventoryEntry>& Entries,int32 Revision);
    UFUNCTION(Client,Reliable) void ClientCloseContainer();
    UPROPERTY() TObjectPtr<ABunkerContainer> ServerContainer;
    UPROPERTY() TObjectPtr<ABunkerContainer> ViewedContainer;
    UPROPERTY() TArray<FBunkerInventoryEntry> ContainerEntries;
    int32 ContainerRevision=0;
    bool bContainerSide=true;
    bool CanAccessContainer(ABunkerContainer* Container) const;
    void CloseContainerView();
    void StorageTick(float DT);
    void StorageProbeTick(float DT);
    UFUNCTION(Server,Reliable) void ServerPrepareStorageProbe(bool bFar);
    int32 StorageProbeStage=0;
    int32 StorageOriginalRevision=0;
    FGuid StorageProbeId;
    bool bInventoryOpen = false;
    int32 SelectedItem = 0;
    void SurvivalProbeTick(float DT);
    void HandsProbeTick(float DT);
    int32 HandsProbeStage=0;
    FGuid HandsUsedId;
    UFUNCTION(Server, Reliable) void ServerPrepareProbe(int32 Phase);
    void NetProbeTick(float DT);
private:
    TWeakObjectPtr<ABunkerInteractable> Focused;
    FVector RestExit = FVector::ZeroVector;
    double NextActionTime = 0;
    float PromptTimer = 0;
    float ProbeTime = 0, ProbePreparedAt = 0;
    bool bProbePrepared = false;
    int ProbeCompleted = -1;
    bool bProbeReleased = false, bReleaseChecked = false, bDoorOpenChecked = false, bDoorClosedChecked = false;
    void ProbeKey(FKey Key);
    int32 DartThrows = 0, DartScore = 0;
    double NextInventoryTime = 0;
    int32 SurvivalProbeStage = 0;
    FGuid UsedProbeId;
    void ToggleInventory();
    void InventoryUp();
    void SwitchContainerSide();
    void TransferSelected();
    float StorageCheckTime=0;
    void InventoryDown();
    void UseSelected();
    void DropSelected();
    void Interact();
    void LeaveBed();
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
};

UCLASS()
class CONDOMINIO13_API ABunkerGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ABunkerGameMode();
    void StartPersistence();
    void C13AutoSave();
    bool SaveCheckpoint();
    bool LoadCheckpoint();
    void PersistenceProbe();
    bool bPersistenceReady=false, bPersistenceBlocked=false;
    int64 SaveSequence=0;
    FString SavePrefix;
    FTimerHandle PersistenceTimer;
    void StartDoorValidation();
    void StartSurvivalValidation();
    void StartHandsValidation();
    void StartStorageValidation();
    virtual void Logout(AController* Exiting) override;
    virtual void BeginPlay() override;
    virtual void PreLogin(const FString& Options, const FString& Address, const FUniqueNetIdRepl& Id, FString& Error) override;
};
