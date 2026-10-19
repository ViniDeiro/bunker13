#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "BunkerSurvival.h"
#include "BunkerNetwork.generated.h"
class ABunkerInteractable;
class ABunkerItemPresentation;

USTRUCT(BlueprintType)
struct FBunkerInventoryEntry
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FGuid Id;
    UPROPERTY(BlueprintReadOnly) FString Name;
    UPROPERTY(BlueprintReadOnly) FName ItemType;
    UPROPERTY(BlueprintReadOnly) float WeightKg = 0;
    UPROPERTY() TObjectPtr<UStaticMesh> WorldMesh;
    UPROPERTY() TArray<TObjectPtr<UMaterialInterface>> Materials;
    UPROPERTY() FVector WorldScale = FVector::OneVector;
};

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
    UFUNCTION(Exec) void C13Host();
    UFUNCTION(Exec) void C13Join(const FString& Address);
    void ReleaseBed(bool bDisconnect = false);
    UFUNCTION(Server,Reliable) void ServerUseItem(FGuid Id);
    UFUNCTION(Server,Reliable) void ServerDropItem(FGuid Id);
    UFUNCTION(Client,Reliable) void ClientPlayItemAction(const FBunkerInventoryEntry& Entry,bool bConsume);
    UPROPERTY() TObjectPtr<ABunkerItemPresentation> ItemPresentation;
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
    void StartDoorValidation();
    void StartSurvivalValidation();
    void StartHandsValidation();
    virtual void Logout(AController* Exiting) override;
    virtual void BeginPlay() override;
    virtual void PreLogin(const FString& Options, const FString& Address, const FUniqueNetIdRepl& Id, FString& Error) override;
};
