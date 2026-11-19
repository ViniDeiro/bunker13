#include "CinematicMenu.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Camera/PlayerCameraManager.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/HorizontalBox.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Camera/CameraComponent.h"
#include "Camera/CameraActor.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundAttenuation.h"
#include "Styling/CoreStyle.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Components/PointLightComponent.h"
#include "UnrealClient.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "Engine/Texture2D.h"

void UCinematicMenuWidget::NativeOnInitialized()
{
 Super::NativeOnInitialized();
 auto* Root=WidgetTree->ConstructWidget<UCanvasPanel>();WidgetTree->RootWidget=Root;
 auto* Scale=WidgetTree->ConstructWidget<UScaleBox>();
 auto* Slot=Root->AddChildToCanvas(Scale);Slot->SetAnchors(FAnchors(.5f,.55f));Slot->SetAlignment(FVector2D(.5f,.5f));Slot->SetSize(FVector2D(530,690));
 auto* Bounds=WidgetTree->ConstructWidget<USizeBox>();Bounds->SetWidthOverride(530);Bounds->SetHeightOverride(690);Scale->AddChild(Bounds);
 List=WidgetTree->ConstructWidget<UVerticalBox>();Bounds->AddChild(List);
 auto Label=[&](FString Words,int Size,FLinearColor Color,float Gap)
 {
  auto* T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(Words));
  T->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",Size));T->SetColorAndOpacity(FSlateColor(Color));T->SetJustification(ETextJustify::Center);
  T->SetShadowOffset(FVector2D(2,3));T->SetShadowColorAndOpacity(FLinearColor(0,0,0,.9));
  auto* S=List->AddChildToVerticalBox(T);S->SetPadding(FMargin(0,Gap,0,0));return T;
 };
 Label(TEXT(" "),56,FLinearColor(.91,.79,.59),0);
 auto* Brand=WidgetTree->ConstructWidget<UHorizontalBox>();
 auto* BrandSlot=Root->AddChildToCanvas(Brand);BrandSlot->SetAnchors(FAnchors(.5f,.24f));BrandSlot->SetAlignment(FVector2D(.5f,.5f));BrandSlot->SetSize(FVector2D(1000,125));
 for(int Part=0;Part<2;++Part)
 {
  auto* Word=WidgetTree->ConstructWidget<UTextBlock>();
  Word->SetText(FText::FromString(Part==0?TEXT("ÚLTIMO "):TEXT("ABRIGO")));
  Word->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",80));
  Word->SetColorAndOpacity(FSlateColor(Part==0?FLinearColor(.91,.85,.72):FLinearColor(.77,.24,.035)));
  Word->SetShadowOffset(FVector2D(2,4));Word->SetShadowColorAndOpacity(FLinearColor(0,0,0,.9));
  Brand->AddChildToHorizontalBox(Word);
 }
 Label(TEXT("SOBREVIVA  •  COOPERE  •  DECIDA"),15,FLinearColor(.85,.7,.47),16);
 const TCHAR* Words[]={TEXT("INICIAR PARTIDA"),TEXT("JOGAR EM GRUPO · EM DESENVOLVIMENTO"),TEXT("CONFIGURAÇÕES"),TEXT("DIÁRIO DO ABRIGO"),TEXT("SAIR")};
 for(int I=0;I<5;++I)
 {
  auto* Box=WidgetTree->ConstructWidget<USizeBox>();Box->SetHeightOverride(64);
  List->AddChildToVerticalBox(Box)->SetPadding(FMargin(35,I==0?42:12,35,0));
  auto* B=WidgetTree->ConstructWidget<UButton>();Box->AddChild(B);
  FButtonStyle Style;
  auto Brush=[I](FLinearColor C){FSlateBrush V;V.DrawAs=ESlateBrushDrawType::Image;if(I>0)V.SetResourceObject(LoadObject<UTexture2D>(nullptr,TEXT("/Game/Bunker/Textures/T_Steel_BaseColor.T_Steel_BaseColor")));V.TintColor=FSlateColor(C);return V;};
  Style.Normal=Brush(I==0?FLinearColor(.92,.34,.035,.98):FLinearColor(.032,.036,.034,.93));
  Style.Hovered=Brush(FLinearColor(.85,.39,.055,.97));
  Style.Pressed=Brush(FLinearColor(.37,.15,.025,.98));
  Style.Disabled=Brush(FLinearColor(.045,.045,.043,.85));B->SetStyle(Style);
  auto* T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(Words[I]));
  T->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",I==1?14:22));T->SetColorAndOpacity(FSlateColor(FLinearColor(.94,.88,.73)));
  B->AddChild(T);B->OnHovered.AddDynamic(this,&UCinematicMenuWidget::Hover);Buttons.Add(B);
 }
 Buttons[0]->OnClicked.AddDynamic(this,&UCinematicMenuWidget::Start);
 Buttons[1]->SetIsEnabled(false);
 Buttons[2]->OnClicked.AddDynamic(this,&UCinematicMenuWidget::Settings);
 Buttons[3]->OnClicked.AddDynamic(this,&UCinematicMenuWidget::Journal);
 Buttons[3]->SetIsEnabled(false);
 Buttons[4]->OnClicked.AddDynamic(this,&UCinematicMenuWidget::Quit);
 Notice=Label(TEXT("DEIROS DEV  /  DIÁRIO E GRUPO EM DESENVOLVIMENTO"),12,FLinearColor(.69,.65,.54),24);
 Notice->SetAutoWrapText(true);
 SettingsPanel=WidgetTree->ConstructWidget<UBorder>();SettingsPanel->SetBrushColor(FLinearColor(.025,.03,.029,.98));SettingsPanel->SetPadding(FMargin(30));
 auto* PanelSlot=Root->AddChildToCanvas(SettingsPanel);PanelSlot->SetAnchors(FAnchors(.5,.5));PanelSlot->SetAlignment(FVector2D(.5,.5));PanelSlot->SetSize(FVector2D(500,350));
 auto* Column=WidgetTree->ConstructWidget<UVerticalBox>();SettingsPanel->AddChild(Column);
 SettingsTitle=WidgetTree->ConstructWidget<UTextBlock>();SettingsTitle->SetText(FText::FromString(TEXT("CONFIGURAÇÕES DE ACESSIBILIDADE")));
 SettingsTitle->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",19));Column->AddChildToVerticalBox(SettingsTitle);
 for(int I=0;I<3;++I)
 {
  auto* Button=WidgetTree->ConstructWidget<UButton>();Column->AddChildToVerticalBox(Button)->SetPadding(FMargin(0,20,0,0));
  auto* Text=WidgetTree->ConstructWidget<UTextBlock>();Text->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",17));Text->SetColorAndOpacity(FSlateColor(FLinearColor(.07,.08,.07)));
  Text->SetText(FText::FromString(I==0?TEXT("PARALLAX: ATIVO"):I==1?TEXT("PULSO AMBIENTAL: ATIVO"):TEXT("VOLTAR")));Button->AddChild(Text);SettingLabels.Add(Text);
  if(I==0)Button->OnClicked.AddDynamic(this,&UCinematicMenuWidget::ToggleParallax);
  else if(I==1)Button->OnClicked.AddDynamic(this,&UCinematicMenuWidget::ToggleEffects);
  else Button->OnClicked.AddDynamic(this,&UCinematicMenuWidget::Back);
 }
 SettingsPanel->SetVisibility(ESlateVisibility::Collapsed);

}
void UCinematicMenuWidget::Hover()
{
 if(auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Bunker/ReferenceRoom/Audio/S_Cabinet_Close.S_Cabinet_Close")))UGameplayStatics::PlaySound2D(this,Sound,.07f);
}
void UCinematicMenuWidget::Start(){if(auto* PC=Cast<ACinematicMenuController>(GetOwningPlayer()))PC->BeginEntrance();}
void UCinematicMenuWidget::Group(){}
void UCinematicMenuWidget::Settings(){SettingsPanel->SetVisibility(ESlateVisibility::Visible);List->SetVisibility(ESlateVisibility::Hidden);}
void UCinematicMenuWidget::Back(){SettingsPanel->SetVisibility(ESlateVisibility::Collapsed);List->SetVisibility(ESlateVisibility::Visible);}
void UCinematicMenuWidget::ToggleParallax()
{
 if(auto* PC=Cast<ACinematicMenuController>(GetOwningPlayer())){PC->bParallax=!PC->bParallax;SettingLabels[0]->SetText(FText::FromString(PC->bParallax?TEXT("PARALLAX: ATIVO"):TEXT("PARALLAX: DESATIVADO")));}
}
void UCinematicMenuWidget::ToggleEffects()
{
 if(auto* PC=Cast<ACinematicMenuController>(GetOwningPlayer())){PC->bEffects=!PC->bEffects;SettingLabels[1]->SetText(FText::FromString(PC->bEffects?TEXT("PULSO AMBIENTAL: ATIVO"):TEXT("PULSO AMBIENTAL: DESATIVADO")));}
}
void UCinematicMenuWidget::NativeTick(const FGeometry& Geometry,float DT)
{
 Super::NativeTick(Geometry,DT);
 const FVector2D Viewport=UWidgetLayoutLibrary::GetViewportSize(this)/FMath::Max(.01f,UWidgetLayoutLibrary::GetViewportScale(this));
 if(auto* S=Cast<UCanvasPanelSlot>(List->GetParent()->GetParent()->Slot))
  S->SetSize(FVector2D(FMath::Min(530.f,float(Viewport.X*.48)),FMath::Min(690.f,float(Viewport.Y*.87))));
 for(auto Button:Buttons)
 {
  const float Target=Button->IsHovered()?1.015f:1.f;
  const float Current=FMath::FInterpTo(Button->GetRenderTransform().Scale.X,Target,DT,9);
  Button->SetRenderScale(FVector2D(Current,Current));
 }
}
void UCinematicMenuWidget::Journal(){Notice->SetText(FText::FromString(TEXT("DIÁRIO · CHEGADA AO B-13\nReúna suprimentos. Mantenha energia e água.\nAs decisões do grupo determinam quanto tempo o abrigo resiste.")));}
void UCinematicMenuWidget::Quit(){UKismetSystemLibrary::QuitGame(this,GetOwningPlayer(),EQuitPreference::Quit,false);}

ACinematicMenuMode::ACinematicMenuMode(){PlayerControllerClass=ACinematicMenuController::StaticClass();DefaultPawnClass=nullptr;HUDClass=nullptr;}
void ACinematicMenuController::BeginPlay()
{
 Super::BeginPlay();
 TActorIterator<ACameraActor> It(GetWorld());
 if(It){View=*It;MenuCamera=It->GetCameraComponent();}
 if(!View)return;
 Origin=View->GetActorTransform();SetViewTarget(View);
 Menu=CreateWidget<UCinematicMenuWidget>(this);Menu->AddToViewport();
 for(TActorIterator<AActor> Actor(GetWorld());Actor;++Actor){
  if(Actor->ActorHasTag(TEXT("MenuEmergency")))RedLight=Actor->FindComponentByClass<UPointLightComponent>();
  if(Actor->ActorHasTag(TEXT("MenuFan")))Fan=*Actor;
  if(Actor->ActorHasTag(TEXT("MenuDust")))Dust.Add(*Actor);
 }
 auto* Attenuation=NewObject<USoundAttenuation>(this);Attenuation->Attenuation.bAttenuate=true;Attenuation->Attenuation.AttenuationShapeExtents=FVector(200,0,0);Attenuation->Attenuation.FalloffDistance=1000;
 if(auto* Hum=LoadObject<USoundBase>(nullptr,TEXT("/Game/Bunker/MainMenu/S_Menu_Hum.S_Menu_Hum")))UGameplayStatics::SpawnSoundAtLocation(this,Hum,FVector(450,-120,160),FRotator::ZeroRotator,.14f,1,0,Attenuation);

 bShowMouseCursor=true;FInputModeGameAndUI Input;Input.SetHideCursorDuringCapture(false);Input.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);SetInputMode(Input);
}
void ACinematicMenuController::BeginEntrance(){if(Entrance>=0)return;Entrance=0;if(Menu)Menu->SetIsEnabled(false);UE_LOG(LogTemp,Display,TEXT("C13_MENU_ENTRANCE_BEGIN"));}
void ACinematicMenuController::PlayerTick(float DT)
{
 Super::PlayerTick(DT);if(!View||!MenuCamera)return;Time+=DT;
 for(auto Particle:Dust)if(Particle.IsValid())
 {
  Particle->SetActorHiddenInGame(!bEffects);
  if(bEffects){FVector P=Particle->GetActorLocation();P.Z+=DT*.8f;if(P.Z>220)P.Z=100;Particle->SetActorLocation(P);}
 }
 if(Time>NextRadio){NextRadio=Time+19;if(auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Bunker/MainMenu/S_Menu_Radio.S_Menu_Radio")))UGameplayStatics::PlaySoundAtLocation(this,Sound,FVector(250,-165,103),.045f);}
 if(Fan && bEffects)Fan->AddActorLocalRotation(FRotator(0,DT*16,0));
 if(Time>3&&Time<8&&DT>0)Timing.Add(DT);
#if !UE_BUILD_SHIPPING
 if(FParse::Param(FCommandLine::Get(),TEXT("C13CinematicVideo")) && Time>5 && Time>NextFrame)
 {
  NextFrame=Time+.125f;const FString Name=FString::Printf(TEXT("cinematic_video_%05d.png"),CaptureIndex++);
  FScreenshotRequest::RequestScreenshot(Name,true,false);
  UE_LOG(LogTemp,Display,TEXT("C13_MENU_FRAME time=%.5f file=%s"),Time,*Name);
 }
#endif
 if(Entrance>=0)
 {
  Entrance+=DT;const float T=FMath::Clamp(Entrance/2.8f,0.f,1.f),Ease=T*T*(3-2*T);
  View->SetActorLocation(FMath::Lerp(Origin.GetLocation(),FVector(380,130,157),Ease));
  View->SetActorRotation(FQuat::Slerp(Origin.GetRotation(),FRotator(-8,38,0).Quaternion(),Ease));
  if(Menu)Menu->SetRenderOpacity(1-FMath::Clamp(Entrance/.65f,0.f,1.f));
  if(Entrance>2.8f)
  {
   if(Entrance-DT<=2.8f)PlayerCameraManager->StartCameraFade(0,1,.6f,FLinearColor::Black,false,true);
   if(Entrance>3.45f){if(Menu)Menu->RemoveFromParent();UE_LOG(LogTemp,Display,TEXT("C13_MENU_TRAVEL"));UGameplayStatics::OpenLevel(this,TEXT("/Game/Bunker/Lvl_CollectionRound"),true,TEXT("C13MenuStart"));Entrance=-100;}
  }
  return;
 }
 float X=0,Y=0;GetMousePosition(X,Y);int32 W,H;GetViewportSize(W,H);
 const float NX=bParallax&&W>0?FMath::Clamp(X/W*2-1,-1.f,1.f):0;
 const float NY=bParallax&&H>0?FMath::Clamp(Y/H*2-1,-1.f,1.f):0;
 const FVector Target=Origin.GetLocation()+FVector(0,NX*6,-NY*4);
 View->SetActorLocation(FMath::VInterpTo(View->GetActorLocation(),Target,DT,2.5));
 View->SetActorRotation(FMath::RInterpTo(View->GetActorRotation(),Origin.Rotator()+FRotator(-NY*.7f,NX*1.2f,0),DT,2.5));
 if(RedLight)RedLight->SetIntensity(bEffects?90+25*FMath::Sin(Time*.6f):90);
#if !UE_BUILD_SHIPPING
 if(FParse::Param(FCommandLine::Get(),TEXT("C13CinematicTest")))
 {
  if(Time>5&&Time<8){int32 VW,VH;GetViewportSize(VW,VH);SetMouseLocation(VW*(.5f+.35f*FMath::Sin(Time)),VH*(.5f+.2f*FMath::Cos(Time)));}
  if(Time>8&&TestStage==0){
   float Sum=0;for(float V:Timing)Sum+=V;Timing.Sort();
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_FPS mean=%.2f p95_ms=%.2f samples=%d"),Sum>0?Timing.Num()/Sum:0,Timing.IsEmpty()?0:Timing[FMath::Min(Timing.Num()-1,int(Timing.Num()*.95))]*1000,Timing.Num());
   const FVector Offset=View->GetActorLocation()-Origin.GetLocation();
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_PARALLAX pass=%d offset_cm=%.3f"),Offset.Size()>.1f&&Offset.Size()<8,Offset.Size());
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_DISABLED pass=%d"),!Menu->Buttons[1]->GetIsEnabled()&&!Menu->Buttons[3]->GetIsEnabled());
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_DEPTH pass=%d camera_x=%.2f"),Origin.GetLocation().X<0,Origin.GetLocation().X);
   FScreenshotRequest::RequestScreenshot(TEXT("cinematic_menu.png"),true,false);TestStage=1;}
  if(Time>9&&TestStage==1&&FParse::Param(FCommandLine::Get(),TEXT("C13CinematicQuitTest")))
  {
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_QUIT_REQUEST pass=1"));
   Menu->Buttons[4]->OnClicked.Broadcast();return;
  }
  if(Time>9&&TestStage==1)
  {
   Menu->Settings();Menu->ToggleParallax();Menu->ToggleEffects();
   UE_LOG(LogTemp,Display,TEXT("C13_MENU_ACCESSIBILITY pass=%d"),!bParallax&&!bEffects);
   Menu->Back();Menu->ToggleParallax();Menu->ToggleEffects();TestStage=2;
  }
  if(Time>11&&TestStage==2){Menu->Buttons[0]->OnClicked.Broadcast();TestStage=3;}
 }
#endif
}
