#pragma once
#include "GameFramework/Actor.h"
#include "BunkerInventoryTypes.h"
#include "BunkerObservedAction.generated.h"
// Only the current gesture is shared; never the player's backpack or needs.
UCLASS()
class CONDOMINIO13_API ABunkerObservedAction : public AActor
{
    GENERATED_BODY()
public:
    ABunkerObservedAction();
    UPROPERTY(Replicated) TObjectPtr<APawn> Performer;
    UPROPERTY(Replicated) FBunkerInventoryEntry Visual;
    UPROPERTY(Replicated) FVector Contact=FVector::ZeroVector;
    UPROPERTY(Replicated) TObjectPtr<AActor> ContactTarget;
    UPROPERTY(Replicated) FVector ContactLocal=FVector::ZeroVector;
    UPROPERTY(Replicated) uint8 Kind=0; // 0 pickup,1 put,2 handle,3 consume
    UPROPERTY(Replicated) float Start=0;
    UPROPERTY(Replicated) float Duration=1;
    bool bObservedLogged=false;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Left;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Right;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Item;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Accessory;
    static void StartFor(class ABunkerPlayerController* PC,const FBunkerInventoryEntry& Entry,FVector Point,uint8 Action,float Length,AActor* Target=nullptr);
    virtual void Tick(float DT) override;
    virtual bool IsNetRelevantFor(const AActor* RealViewer,const AActor* ViewTarget,const FVector& SrcLocation) const override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
