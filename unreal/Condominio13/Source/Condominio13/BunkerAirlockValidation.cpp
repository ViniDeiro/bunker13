#include "BunkerNetwork.h"
#include "BunkerRound.h"
#include "BunkerDoor.h"
#include "BunkerInfrastructure.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "InputKeyEventArgs.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"

void ABunkerPlayerController::ServerAirlockProbe_Implementation(int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest"))||!FParse::Param(FCommandLine::Get(),TEXT("C13AirlockTest")))return;
 auto* R=ABunkerRound::Find(GetWorld());auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();
 if(!R||!R->Gate||!R->InnerGate||!C||!PS||!GM||!GM->bPersistenceReady||GM->bPersistenceBlocked)return;
 if(Step==0&&IsLocalController())
 {R->Phase=3;R->Gate->bOpen=false;R->Gate->CurrentAngle=0;R->InnerGate->bOpen=false;R->InnerGate->CurrentAngle=0;R->ForceNetUpdate();R->Gate->ForceNetUpdate();R->InnerGate->ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_FIXTURE_READY"));}
 if(Step==1||Step==2||Step==3||Step==4)
 {
  ABunkerDoor* D=(Step==4||!IsLocalController())?R->InnerGate.Get():R->Gate.Get();
  const FVector P=!IsLocalController()?FVector(2700,-900,100):Step==2?FVector(2550,160,100):Step==4?(GetWorld()->GetGameState()->GetServerWorldTimeSeconds()-ABunkerInfrastructure::Find(GetWorld())->TestEpoch>85?FVector(2550,-900,100):FVector(2550,-400,100)):FVector(2550,-250,100);
  C->GetCharacterMovement()->StopMovementImmediately();C->SetActorLocation(P);
  const FVector Aim=D->GetActorTransform().TransformPosition(FVector(D->Width*.5f,0,110));
  for(int I=0;I<3;I++){FMinimalViewInfo V;C->CalcCamera(0,V);SetControlRotation((Aim-V.Location).Rotation());}ClientSetRotation(GetControlRotation(),true);
  FMinimalViewInfo V;C->CalcCamera(0,V);FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(AirlockFixtureAim),false,C);GetWorld()->LineTraceSingleByChannel(H,V.Location,V.Location+GetControlRotation().Vector()*350,ECC_Visibility,Q);
  UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_AIM step=%d expected=%s hit=%s position=%s"),Step,*D->GetName(),*GetNameSafe(H.GetActor()),*C->GetActorLocation().ToString());
 }
 if(Step==5&&IsLocalController())if(auto* Infra=ABunkerInfrastructure::Find(GetWorld())){Infra->State.Services=false;Infra->ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_FIXTURE_POWER_OFF"));}
 if(Step==6&&IsLocalController())if(auto* Infra=ABunkerInfrastructure::Find(GetWorld())){Infra->State.Services=true;Infra->ForceNetUpdate();}
 if(Step>=10)
 {
  bool OK=false;
  if(Step==10)OK=R->Gate->bOpen&&!R->InnerGate->bOpen&&FMath::Abs(R->InnerGate->CurrentAngle)<.5f;
  if(Step==11)OK=C->GetActorLocation().Y>60;
  if(Step==12)OK=C->GetActorLocation().Y<-100&&C->GetActorLocation().Y>-640;
  if(Step==13)OK=C->GetActorLocation().Y<-750&&R->InnerGate->bOpen&&!R->Gate->bOpen;
  if(Step==14)OK=R->Phase==3&&R->AirlockTarget==0&&R->AirlockDeadline==0&&!R->InnerGate->bOpen&&!R->Gate->bOpen;
  if(Step==15)OK=R->AirlockTarget==1&&R->AirlockDeadline-GetWorld()->GetGameState()->GetServerWorldTimeSeconds()>9&&!R->InnerGate->bOpen&&!R->Gate->bOpen;
  if(Step==16)OK=!R->InnerGate->bOpen&&!R->Gate->bOpen;
  UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_CHECK step=%d pass=%d y=%.1f outer=%d inner=%d cycle=%d"),Step,OK,C->GetActorLocation().Y,R->Gate->bOpen,R->InnerGate->bOpen,R->AirlockTarget);
  if(Step==13)C13Save();
 }
#endif
}
void ABunkerPlayerController::AirlockProbeTick()
{
#if !UE_BUILD_SHIPPING
 auto* R=ABunkerRound::Find(GetWorld());auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();if(!R||!C||!PS||!PS->bSessionReady)return;
 const float Now=GetWorld()->GetGameState()->GetServerWorldTimeSeconds();const bool Host=HasAuthority();
 auto* Infra=ABunkerInfrastructure::Find(GetWorld());if(!Infra)return;
 const bool Load=FParse::Param(FCommandLine::Get(),TEXT("C13AirlockLoad"));
 if(!Load&&Host&&Infra->TestEpoch==0)
 {int Ready=0;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(It->bSessionReady)Ready++;if(Ready>=2&&R->Phase==0)ProbeKey(EKeys::R);if(Ready>=2&&R->Phase==3){Infra->TestEpoch=Now;Infra->ForceNetUpdate();}}
 if(!Load&&Infra->TestEpoch==0)return;
 const float T=Load?Now:Now-Infra->TestEpoch;
 auto Key=[this](EInputEvent Event){InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,EKeys::E,Event,Event==IE_Pressed?1.f:0.f,false,FPlatformTime::Cycles64()));};
 auto Press=[&](){Key(IE_Pressed);Key(IE_Released);};
 if(FParse::Param(FCommandLine::Get(),TEXT("C13AirlockLoad")))
 {if(T>5&&RoundProbeStage==0){RoundProbeStage=1;ServerAirlockProbe(14);FScreenshotRequest::RequestScreenshot(TEXT("airlock_resumed.png"),true,false);}if(T>7)FGenericPlatformMisc::RequestExit(false);return;}
 const double Wall=FPlatformTime::Seconds();if(T>12&&T<28&&ReferenceWall>0)ReferenceFrames.Add((Wall-ReferenceWall)*1000);ReferenceWall=Wall;
 if(T>29&&ReferenceFrames.Num()){ReferenceFrames.Sort();double Sum=0;for(double X:ReferenceFrames)Sum+=X;UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),ReferenceFrames.Num(),1000*ReferenceFrames.Num()/Sum,ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,int(ReferenceFrames.Num()*.95))]);ReferenceFrames.Empty();}
 if(!Host)
 {
  if(T>12&&RoundProbeStage==0){ServerAirlockProbe(1);RoundProbeStage=1;}
  if(T>15&&RoundProbeStage==1){Press();RoundProbeStage=2;}
  if(T>22&&RoundProbeStage==2){Press();ServerAirlockProbe(10);UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_REPLICA outer=%d inner=%d"),R->Gate&&R->Gate->bOpen,R->InnerGate&&R->InnerGate->bOpen);RoundProbeStage=3;FScreenshotRequest::RequestScreenshot(TEXT("airlock_client_blocked.png"),true,false);}
  if(T>115)FGenericPlatformMisc::RequestExit(false);return;
 }
 if(T>10&&RoundProbeStage==0){ServerAirlockProbe(0);RoundProbeStage=1;}
 if(T>12&&RoundProbeStage==1){ServerAirlockProbe(1);RoundProbeStage=2;}
 if(T>14&&RoundProbeStage==2){Press();RoundProbeStage=3;}
 if(T>16&&RoundProbeStage==3){Press();RoundProbeStage=4;}
 if(T>20&&RoundProbeStage==4){Press();RoundProbeStage=5;}
 if(T>22&&T<25)C->AddMovementInput(FVector(0,1,0),.6f);
 if(T>25&&RoundProbeStage==5){ServerAirlockProbe(11);ServerAirlockProbe(2);RoundProbeStage=6;}
 if(T>27&&RoundProbeStage==6){Press();RoundProbeStage=7;}
 if(T>28&&RoundProbeStage==7){ServerAirlockProbe(5);RoundProbeStage=8;}
 if(T>30&&RoundProbeStage==8){Press();RoundProbeStage=9;FScreenshotRequest::RequestScreenshot(TEXT("airlock_manual.png"),true,false);}
 if(T>43&&RoundProbeStage==9){Key(IE_Pressed);RoundProbeStage=10;}
 if(T>57&&RoundProbeStage==10){Key(IE_Released);RoundProbeStage=11;}
 if(T>58&&T<60)C->AddMovementInput(FVector(0,-1,0),.6f);
 if(T>60&&RoundProbeStage==11){ServerAirlockProbe(12);ServerAirlockProbe(3);RoundProbeStage=12;}
 if(T>62&&RoundProbeStage==12){Press();RoundProbeStage=13;}
 if(T>65&&RoundProbeStage==13){ServerAirlockProbe(4);RoundProbeStage=14;}
 if(T>66&&RoundProbeStage==14){Press();RoundProbeStage=15;}
 if(T>79&&RoundProbeStage==15){Press();RoundProbeStage=16;}
 if(T>81&&T<84)C->AddMovementInput(FVector(0,-1,0),.6f);
 if(T>84&&RoundProbeStage==16){ServerAirlockProbe(13);RoundProbeStage=17;FScreenshotRequest::RequestScreenshot(TEXT("airlock_return.png"),true,false);}
 if(T>86&&RoundProbeStage==17){ServerAirlockProbe(4);RoundProbeStage=18;}
 // Position on the bunker side for closing the inner leaf after returning.
 if(T>87&&RoundProbeStage==18){Press();ServerAirlockProbe(6);RoundProbeStage=19;}
 if(T>90&&RoundProbeStage==19){Press();RoundProbeStage=20;}
 if(T>91&&RoundProbeStage==20){ServerAirlockProbe(5);RoundProbeStage=21;}
 if(T>92&&RoundProbeStage==21){ServerAirlockProbe(15);RoundProbeStage=22;}
 if(T>104&&RoundProbeStage==22){Press();RoundProbeStage=23;}
 if(T>107&&RoundProbeStage==23){ServerAirlockProbe(2);RoundProbeStage=24;}
 if(T>109&&RoundProbeStage==24){Press();RoundProbeStage=25;}
 if(T>112&&RoundProbeStage==25){ServerAirlockProbe(16);C13Save();RoundProbeStage=26;}
 if(T>118)FGenericPlatformMisc::RequestExit(false);
#endif
}
