#pragma once
#include "BunkerContainer.h"
#include "BunkerReferenceCabinet.generated.h"
class UBoxComponent;
class USoundBase;

// Additive reference-room fixture. Logical slot addresses never depend on array order.
UCLASS()
class CONDOMINIO13_API ABunkerReferenceCabinet : public ABunkerContainer
{
    GENERATED_BODY()
public:
    ABunkerReferenceCabinet();
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Anchor;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Hinge;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Leaf;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> DoorCollision;
    UPROPERTY() TArray<TObjectPtr<UBoxComponent>> Slots;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Displays;
    UPROPERTY(Replicated) bool bDoorOpen=false;
    UPROPERTY(Replicated) float DoorAngle=0;
    UPROPERTY() TObjectPtr<class USoundAttenuation> FoleyAttenuation;
    UPROPERTY(EditAnywhere) TObjectPtr<USoundBase> OpenSound;
    UPROPERTY(EditAnywhere) TObjectPtr<USoundBase> CloseSound;
    virtual void BeginPlay() override;
    virtual void Tick(float DT) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    bool ToggleDoor();
    bool Transfer(class ABunkerPlayerController* PC,int32 Slot,FGuid Id,int32 ExpectedRevision,bool bTake);
    int32 SlotFor(const UPrimitiveComponent* Component) const;
    FVector SlotPoint(int32 Slot) const;
    FVector ItemPoint(int32 Slot) const;
    void UpdateQueries(const TArray<FBunkerInventoryEntry>& Entries);
    void Present(const TArray<FBunkerInventoryEntry>& Entries,int32 NewRevision);
    void NormalizeSlots();
    bool ValidSlots(const TArray<FBunkerInventoryEntry>& Entries) const;
    UFUNCTION(NetMulticast,Reliable) void PlayDoorSound(bool bOpening);
private:
    float VisualAngle=0,ObserverClock=0;
    double NextToggle=0,NextTransfer=0;
    TMap<TWeakObjectPtr<ABunkerPlayerController>,int32> Observers;
    bool Blocked(float From,float To) const;
    bool CanObserve(class ABunkerPlayerController* PC) const;
};
