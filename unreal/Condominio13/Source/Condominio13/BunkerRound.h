#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerRound.generated.h"
class ABunkerDoor;
class ABunkerPlayerController;
class UBunkerSaveGame;
UCLASS()
class CONDOMINIO13_API ABunkerRound : public AActor
{
    GENERATED_BODY()
public:
    ABunkerRound();
    // 0 preparation, 1 collection, 2 closing without crushing, 3 shelter.
    UPROPERTY(Replicated) uint8 Phase=0;
    UPROPERTY(Replicated) float Deadline=0;
    UPROPERTY(Replicated) TObjectPtr<ABunkerDoor> Gate;
    UPROPERTY(Replicated) TObjectPtr<ABunkerDoor> InnerGate;
    UPROPERTY(Replicated) bool bAirlockEnabled=false;
    // Transient pressure procedure: never resume an unfinished cycle from a checkpoint.
    UPROPERTY(Replicated) uint8 AirlockTarget=0;
    UPROPERTY(Replicated) float AirlockDeadline=0;
    UPROPERTY(Replicated) bool bAirlockManual=false;
    bool OperateInner(ABunkerPlayerController* PC);
    FString AirlockStatus() const;
    UPROPERTY(Replicated) float ReleaseDeadline=0;
    UPROPERTY(Replicated) bool bRecoveryOpen=false;
    UPROPERTY(Replicated) double ShelterElapsed=0;
    UPROPERTY(Replicated) float ShelterAnchor=-1;
    UPROPERTY(Replicated) float DaySeconds=240;
    double ShelterSeconds() const;
    int32 SurvivalDay() const;
    int32 DayMinute() const;
    TWeakObjectPtr<ABunkerPlayerController> Cranking;
    int32 Alerts=0;
    float LastRemaining=0;
    virtual void BeginPlay() override;
    virtual void Tick(float DT) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    float Remaining() const;
    bool Start(ABunkerPlayerController* PC);
    bool Operate(ABunkerPlayerController* PC);
    void Cancel(ABunkerPlayerController* PC);
    void Store(UBunkerSaveGame* Save) const;
    void Restore(const UBunkerSaveGame* Save);
    UFUNCTION(NetMulticast,Reliable) void Alert(int32 Seconds);
    static ABunkerRound* Find(UWorld* World);
private:
    float AirlockManualDuration=12;
    float ServerNow() const;
    bool Accessible(ABunkerPlayerController* PC) const;
    bool AccessibleDoor(ABunkerPlayerController* PC, ABunkerDoor* Door) const;
    bool AirlockAllows(ABunkerPlayerController* PC, ABunkerDoor* Door);
    void ResetAirlock();
    void Commit();
};
