#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerInfrastructure.generated.h"
class ULightComponent;class UMeshComponent;
class ABunkerInteractable;class ABunkerPlayerController;class UBunkerSurvivalRules;class UBunkerSaveGame;
USTRUCT()
struct FBunkerInfrastructureState
{
 GENERATED_BODY()
 UPROPERTY() float Fuel=1.2f;
 UPROPERTY() float Condition=65;
 UPROPERTY() bool Running=true;
 UPROPERTY() bool Lights=true;
 UPROPERTY() bool Services=true;
 UPROPERTY() bool Pump=true;
 UPROPERTY() float RawWater=12;
 UPROPERTY() float CleanWater=1.5f;
 UPROPERTY() float Filter=100;
};
UCLASS()
class CONDOMINIO13_API ABunkerInfrastructure:public AActor
{
 GENERATED_BODY()
public:
 ABunkerInfrastructure();
 UPROPERTY(ReplicatedUsing=OnRep_State) FBunkerInfrastructureState State;
 UPROPERTY(Replicated) float TestEpoch=0;
 UPROPERTY(Replicated) uint8 Task=0;
 UPROPERTY(Replicated) float TaskDeadline=0;
 TWeakObjectPtr<ABunkerPlayerController> Worker;
 FGuid ReservedItem;
 UPROPERTY() TObjectPtr<ABunkerInteractable> TaskTerminal;
 UPROPERTY() TObjectPtr<UBunkerSurvivalRules> Rules;
 UPROPERTY() TArray<TObjectPtr<ABunkerInteractable>> Terminals;
 virtual void BeginPlay()override;
 virtual void Tick(float DT)override;
 virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out)const override;
 UFUNCTION() void OnRep_State();
 bool Powered()const;
 bool LightingPowered()const{return Powered()&&State.Lights;}
 bool ServicesPowered()const{return Powered()&&State.Services;}
 FString WaterStatus()const;
 bool Filtering()const;
 int32 ControlledLightCount()const{return ControlledLights.Num();}
 int32 EmergencyCount=0;
 bool Operate(ABunkerPlayerController* PC,ABunkerInteractable* Target,uint8 Action);
 FString Status()const;
 static ABunkerInfrastructure* Find(UWorld* W);
 static bool Extension(const ABunkerInteractable* A);
 static bool SupplyExtension(const ABunkerInteractable* A);
 static bool Valid(const FBunkerInfrastructureState& S);
 void Store(UBunkerSaveGame* S)const;
 void Restore(const UBunkerSaveGame* S);
private:
 bool SettingsValid()const;
 bool Accessible(ABunkerPlayerController* PC,ABunkerInteractable* Target)const;
 void Commit();
 void CancelTask();
 void BuildFixtures();
 void CapturePowerConsumers();
 void ApplyPower();
 int32 AppliedPower=-1;
 TArray<TWeakObjectPtr<ULightComponent>> ControlledLights;
 TArray<float> OriginalIntensities;
 TArray<TWeakObjectPtr<ULightComponent>> EmergencyLights;
 TArray<TWeakObjectPtr<UMeshComponent>> EmissiveMeshes;
 TArray<int32> EmissiveSlots;
 UPROPERTY() TArray<TObjectPtr<UMaterialInterface>> OriginalMaterials;
};
