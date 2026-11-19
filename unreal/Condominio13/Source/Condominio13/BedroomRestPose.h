#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BedroomRestPose.generated.h"
class ACharacter;
class ABunkerInteractable;
class UAnimSequence;
class UAnimInstance;

// Cosmetic layer only. Gameplay ownership and energy remain in the existing bed system.
UCLASS()
class CONDOMINIO13_API ABedroomRestPose : public AActor
{
 GENERATED_BODY()
public:
 ABedroomRestPose();
 static void StartFor(ACharacter* Character,ABunkerInteractable* Bed,const FTransform& StandingMesh);
 static void LeaveFor(ACharacter* Character,const FVector& Exit);
 virtual void Tick(float DeltaSeconds) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
 UPROPERTY(Replicated) TObjectPtr<ACharacter> Performer;
 UPROPERTY(Replicated) TObjectPtr<ABunkerInteractable> Bed;
 UPROPERTY(Replicated) FTransform StandingWorld;
 UPROPERTY(Replicated) FTransform DefaultRelative;
 UPROPERTY(Replicated) FTransform ExitStartWorld;
 UPROPERTY(Replicated) FTransform ExitWorld;
 UPROPERTY(Replicated) float StartedAt=0;
 UPROPERTY(Replicated) float LeaveAt=-1;
 UPROPERTY(Replicated) float ReverseFrom=1;
 float PoseProgress() const;
private:
 UPROPERTY() TObjectPtr<UAnimSequence> Sequence;
 UPROPERTY() TSubclassOf<UAnimInstance> OriginalClass;
 uint8 OriginalMode=0;
 bool bInitialized=false;
 float LastSampleTime=-1;
 void Restore();
 FTransform RestWorld() const;
};
