#pragma once
#include "CoreMinimal.h"
#include "BunkerInteractable.h"
#include "BunkerDoor.generated.h"
class UBoxComponent;

UCLASS()
class CONDOMINIO13_API ABunkerDoor : public ABunkerInteractable
{
    GENERATED_BODY()
public:
    ABunkerDoor();
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Hinge;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> LeafCollision;
    UPROPERTY(EditAnywhere, Replicated) float Width = 110.f;
    UPROPERTY(EditAnywhere, Replicated) float Height = 220.f;
    UPROPERTY(EditAnywhere, Replicated) float ClosedYaw = 0.f;
    UPROPERTY(EditAnywhere, Replicated) float OpenAngle = 90.f;
    UPROPERTY(EditAnywhere, Replicated) bool bOpen = true;
    UPROPERTY(Replicated) float CurrentAngle = 90.f;
    bool TryToggle();
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    virtual void Tick(float DT) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
private:
    float VisualAngle = 90.f;
    double NextToggleTime = 0;
    void ConfigureLeaf();
    bool PawnInArc(float From, float To) const;
};
