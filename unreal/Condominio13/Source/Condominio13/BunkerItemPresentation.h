#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerItemPresentation.generated.h"
class ABunkerPlayerController;
UCLASS()
class CONDOMINIO13_API ABunkerItemPresentation : public AActor
{
    GENERATED_BODY()
public:
    ABunkerItemPresentation();
    virtual void Tick(float DeltaSeconds) override;
    void Play(ABunkerPlayerController* Controller,FName Type,UStaticMesh* Mesh,const TArray<TObjectPtr<UMaterialInterface>>& Materials,FVector Scale,bool bConsume,float Duration);
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> Root;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Left;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Right;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Item;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Accessory;
    UPROPERTY() TObjectPtr<class UPointLightComponent> KeyLight;
    UPROPERTY() TObjectPtr<class UPointLightComponent> FillLight;
    UPROPERTY() TObjectPtr<ABunkerPlayerController> Viewer;
    UPROPERTY() FName ItemType;
    UPROPERTY() TObjectPtr<UStaticMesh> ClosedMesh;
    UPROPERTY() TObjectPtr<UStaticMesh> OpenMesh;
    float Elapsed=0,Length=1;
    bool bUsing=false,bPlaying=false;
};
