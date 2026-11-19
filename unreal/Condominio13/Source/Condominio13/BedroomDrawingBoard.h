#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BedroomDrawingBoard.generated.h"

class UStaticMeshComponent;
class UInstancedStaticMeshComponent;
class UTextRenderComponent;

// Local review prop. It neither creates inventory entries nor mutates campaign state.
UCLASS()
class CONDOMINIO13_API ABedroomDrawingBoard : public AActor
{
    GENERATED_BODY()
public:
    ABedroomDrawingBoard();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Frame;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Surface;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Pen;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UInstancedStaticMeshComponent> Ink;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UTextRenderComponent> Label;
private:
    bool bHolding=false, bPreviousUse=false, bPreviousClear=false;
    TOptional<FVector> PreviousPoint;
    FTransform PenRest() const;
    void UpdateBoard(APlayerController& PC, bool Use, bool Draw, bool Clear, FVector Eye, FRotator Look);
#if !UE_BUILD_SHIPPING
    int32 TestStage=0;
    float TestSeconds=0;
    bool bTestReleased=false;
    TArray<float> TestFrames;
    void Probe(APlayerController& PC,float DT);
#endif
};
