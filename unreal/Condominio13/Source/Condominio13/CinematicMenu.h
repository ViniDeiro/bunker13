#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameModeBase.h"
#include "CinematicMenu.generated.h"
class UVerticalBox;
class UButton;
class UTextBlock;
class UCameraComponent;

UCLASS()
class CONDOMINIO13_API UCinematicMenuWidget : public UUserWidget
{
 GENERATED_BODY()
public:
 virtual void NativeOnInitialized() override;
 virtual void NativeTick(const FGeometry& Geometry,float DT) override;
 UPROPERTY() TObjectPtr<UVerticalBox> List;
 UPROPERTY() TObjectPtr<UTextBlock> Notice;
 UPROPERTY() TArray<TObjectPtr<UButton>> Buttons;
 UFUNCTION() void Start();
 UFUNCTION() void Group();
 UFUNCTION() void Settings();
 UFUNCTION() void Journal();
 UFUNCTION() void Quit();
 UFUNCTION() void Hover();
 UFUNCTION() void ToggleParallax();
 UFUNCTION() void ToggleEffects();
 UFUNCTION() void Back();
 UPROPERTY() TObjectPtr<class UBorder> SettingsPanel;
 UPROPERTY() TObjectPtr<class UTextBlock> SettingsTitle;
 UPROPERTY() TArray<TObjectPtr<UTextBlock>> SettingLabels;
};

UCLASS()
class CONDOMINIO13_API ACinematicMenuController : public APlayerController
{
 GENERATED_BODY()
public:
 virtual void BeginPlay() override;
 virtual void PlayerTick(float DT) override;
 void BeginEntrance();
 bool bParallax=true,bEffects=true;
 UPROPERTY() TObjectPtr<UCinematicMenuWidget> Menu;
private:
 UPROPERTY() TObjectPtr<AActor> View;
 UPROPERTY() TObjectPtr<UCameraComponent> MenuCamera;
 FTransform Origin;
 float Entrance=-1,Time=0;
 int TestStage=0;
 float NextFrame=0;int CaptureIndex=0;
 TArray<float> Timing;
 UPROPERTY() TObjectPtr<AActor> Fan;
 TArray<TWeakObjectPtr<AActor>> Dust;
 float NextRadio=6;
 UPROPERTY() TObjectPtr<class UPointLightComponent> RedLight;
};

UCLASS()
class CONDOMINIO13_API ACinematicMenuMode : public AGameModeBase
{
 GENERATED_BODY()
public:
 ACinematicMenuMode();
};
