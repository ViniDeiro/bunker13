#include "BunkerNetwork.h"
#include "BunkerReferenceCabinet.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameStateBase.h"
#include "Camera/PlayerCameraManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"
#include "Misc/Paths.h"
#include "Misc/App.h"
#include "AudioMixerBlueprintLibrary.h"

namespace {
ABunkerReferenceCabinet* Cabinet(UWorld* W)
{for(TActorIterator<ABunkerReferenceCabinet> I(W);I;++I)if(I->PersistentKey==TEXT("C13_Bedroom_Cabinet_v002"))return *I;return nullptr;}
const FGuid Water(0xC1300013,0xB002,0,1);
bool Enabled(UWorld* W)
{return W&&W->GetMapName().Contains(TEXT("Bedroom_Study_Cabinet"))&&FParse::Param(FCommandLine::Get(),TEXT("C13BedroomCabinetTest"));}
}

void C13BedroomCabinetServer(ABunkerPlayerController* PC,int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!Enabled(PC->GetWorld())||!PC->HasAuthority())return;
 auto* Box=Cabinet(PC->GetWorld());auto* C=Cast<ACharacter>(PC->GetPawn());auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if(!Box||!C||!PS)return;
 const bool Host=PC->IsLocalController();
 if(Step<=3)
 {
  if(Step==0){PS->Inventory.Empty();PS->ForceNetUpdate();}
  if(Step==0||Step==1)C->SetActorLocation(FVector(Host?373:285,Host?-210:-115,98));
  if(Step==2 && Host)C->SetActorLocation(FVector(373,-330,98));
  if(Step==3)C->SetActorLocation(FVector(360,-330,98));
  FVector Target=(Step==2)?Box->ItemPoint(6):Box->DoorCollision->GetComponentLocation();
  for(int I=0;I<3;I++){FMinimalViewInfo V;C->CalcCamera(0,V);PC->SetControlRotation((Target-V.Location).Rotation());C->SetActorRotation(FRotator(0,PC->GetControlRotation().Yaw,0));}
  PC->ClientSetRotation(PC->GetControlRotation(),true);
  return;
 }
 if(Step==17 && Host)
 {
  const int Rev=Box->Revision;PC->ServerPhysicalTransfer(Box,6,Water,Rev,true);
  UE_LOG(LogTemp,Display,TEXT("C13_REACH_FAR_TEST pass=%d"),Box->Revision==Rev && Box->Contents.Num()==2 && PS->Inventory.IsEmpty());
  return;
 }
 if(Step==16){PC->ServerPhysicalTransfer(Box,6,Water,0,true);return;}
 if(!Host)return;
 int Players=0,Held=0,Count=0;TSet<FGuid> Unique;bool NoDuplicates=true;
 for(const auto& E:Box->Contents){Count+=E.Id==Water;NoDuplicates&=!Unique.Contains(E.Id);Unique.Add(E.Id);}
 for(TActorIterator<ABunkerPlayerState> I(PC->GetWorld());I;++I)
 {Players++;for(const auto& E:I->Inventory){Held++;Count+=E.Id==Water;NoDuplicates&=!Unique.Contains(E.Id);Unique.Add(E.Id);}}
 bool Pass=false;
 if(Step==10)Pass=Box->bDoorOpen&&Box->DoorAngle>109&&Box->Contents.Num()==2&&Box->Revision==0;
 if(Step==11)Pass=Box->Contents.Num()==1&&Held==1&&Box->Revision==1;
 if(Step==12)Pass=Box->Contents.Num()==2&&Held==0&&Box->Revision==2;
 if(Step==13)Pass=Box->bDoorOpen&&Box->DoorAngle>109; // closing was blocked by the real pawn
 if(Step==14)
 {
  const int Rev=Box->Revision;PC->ServerPhysicalTransfer(Box,6,Water,Rev,true);
  Pass=!Box->bDoorOpen&&Box->DoorAngle<1&&Box->Revision==Rev;
 }
 if(Step==15)Pass=Box->Contents.Num()==2&&Held==0&&Box->Revision==4;
 const bool LegacyKey=GetDefault<ABunkerReferenceCabinet>()->PersistentKey==TEXT("C13_Reference_CommonCabinet_v1");
 Pass&=NoDuplicates&&Count==1&&LegacyKey&&Box->WorldKey==Box->PersistentKey;
 UE_LOG(LogTemp,Display,TEXT("C13_BEDCAB_AUDIT step=%d pass=%d players=%d ownership=%d stored=%d held=%d revision=%d door=%.2f key=%s"),Step,Pass,Players,Count,Box->Contents.Num(),Held,Box->Revision,Box->DoorAngle,*Box->WorldKey);
#endif
}

void C13BedroomCabinetTick(ABunkerPlayerController* PC,float DT)
{
#if !UE_BUILD_SHIPPING
 if(!Enabled(PC->GetWorld())||!PC->IsLocalController()||!PC->GetPawn())return;
 auto* GS=PC->GetWorld()->GetGameState();auto* Box=Cabinet(PC->GetWorld());if(!GS||!Box)return;
 static TWeakObjectPtr<UWorld> W;static int Stage=0;static double Previous=0;static TArray<double> Frames;
 static float NextCapture=0;static int CaptureIndex=0;static bool AudioStarted=false,AudioStopped=false;
 if(W.Get()!=PC->GetWorld()){W=PC->GetWorld();Stage=0;Frames.Empty();Previous=0;NextCapture=0;CaptureIndex=0;AudioStarted=false;AudioStopped=false;}
 const bool Host=PC->HasAuthority();const float T=GS->GetServerWorldTimeSeconds();
 const bool Video=Host&&FParse::Param(FCommandLine::Get(),TEXT("C13BedroomCabinetVideo"));
 if(Video&&T>61.5f&&!AudioStarted)
 {FApp::SetUnfocusedVolumeMultiplier(1.f);FApp::SetVolumeMultiplier(1.f);UAudioMixerBlueprintLibrary::StartRecordingOutput(PC,36);AudioStarted=true;}
 if(Video&&T>61.5f&&T<96.f&&T>NextCapture)
 {
  NextCapture=T+.125f;const FString Name=FString::Printf(TEXT("bedcab_video_%05d.png"),CaptureIndex++);
  FScreenshotRequest::RequestScreenshot(Name,true,false);UE_LOG(LogTemp,Display,TEXT("C13_BEDCAB_FRAME time=%.5f file=%s"),T,*Name);
 }
 if(Video&&T>96.f&&!AudioStopped)
 {UAudioMixerBlueprintLibrary::StopRecordingOutput(PC,EAudioRecordingExportType::WavFile,TEXT("bedcab_audio"),FPaths::ProjectSavedDir()/TEXT("BedroomCabinetVideo"));AudioStopped=true;}
 const double Now=FPlatformTime::Seconds();if(Previous&&T>61&&T<96)Frames.Add(Now-Previous);Previous=Now;
 auto Key=[&](FKey K){PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Pressed,1.f,false,FPlatformTime::Cycles64()));PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Released,0.f,false,FPlatformTime::Cycles64()));};
 const float Times[]={60,62,64,65,67,69,70,72,74,75,76,77,78,80,82,83,84,86,87,89,91,92,94,96,98};
 if(Stage<UE_ARRAY_COUNT(Times)&&T>(Stage==24&&!Host?97.f:Times[Stage]+(Host?0:.12f)))
 {
  const int S=Stage++;
  if(S==0)PC->ServerReferenceStep(0);
  if(S==3||S==6||S==18||S==21)PC->ServerReferenceStep(2);
  if(Host&&(S==1||S==4||S==10||S==13||S==16||S==19))Key(EKeys::E);
  if(!Host&&S==4)PC->ServerReferenceStep(16);
  if(Host&&(S==7||S==22))Key(EKeys::X);
  if(Host&&S==9)PC->ServerReferenceStep(3);
  if(S==12||S==15)PC->ServerReferenceStep(1);
  if(Host&&S==2){PC->ServerReferenceStep(10);PC->ServerReferenceStep(17);}
  if(Host&&S==5)PC->ServerReferenceStep(11);
  if(Host&&S==8)PC->ServerReferenceStep(12);
  if(Host&&S==11)PC->ServerReferenceStep(13);
  if(Host&&S==14)PC->ServerReferenceStep(14);
  if(Host&&S==23)PC->ServerReferenceStep(15);
  if(S==2||S==5||S==8||S==17||S==23)
  {
   int Drawn=0;for(auto D:Box->Displays)Drawn+=D->GetStaticMesh()!=nullptr&&D->IsVisible();
   UE_LOG(LogTemp,Display,TEXT("C13_BEDCAB_VIEW role=%s stage=%d revision=%d entries=%d drawn=%d modal=%d door=%.2f"),Host?TEXT("host"):TEXT("client"),S,PC->PhysicalRevision,PC->PhysicalEntries.Num(),Drawn,PC->bInventoryOpen,Box->DoorAngle);
   FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("bedcab_%s_%02d.png"),Host?TEXT("host"):TEXT("client"),S),true,false);
  }
  if(S==24)
  {
   double Sum=0;for(double V:Frames)Sum+=V;Frames.Sort();
   UE_LOG(LogTemp,Display,TEXT("C13_BEDCAB_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),Frames.Num(),Sum>0?Frames.Num()/Sum:0,Frames.Num()?Frames[FMath::Min(Frames.Num()-1,int(Frames.Num()*.95))]*1000:0);
   FGenericPlatformMisc::RequestExit(false);
  }
 }
#endif
}
