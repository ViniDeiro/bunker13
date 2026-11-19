#pragma once
#include "Camera/CameraModifier.h"
#include "BedroomRestCamera.generated.h"
class USkeletalMeshComponent;

// Presentation only. Bed ownership, energy, exit validation and persistence stay server-owned.
UCLASS()
class CONDOMINIO13_API UBedroomRestCamera : public UCameraModifier
{
    GENERATED_BODY()
public:
    virtual bool ModifyCamera(float DeltaTime, FMinimalViewInfo& InOutPOV) override;
private:
    bool bResting = false;
    bool bInitialized = false;
    float Elapsed = 2.f;
    FMinimalViewInfo Previous;
    FMinimalViewInfo From;
    TMap<TWeakObjectPtr<USkeletalMeshComponent>, bool> OwnerVisibility;
};
