#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BedroomRestPose.h"
#include "BedroomRestTestClock.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"

namespace {
ABunkerInteractable* FindBed(UWorld* W){for(TActorIterator<ABunkerInteractable>I(W);I;++I)if(I->Interaction==EBunkerInteraction::Bed)return *I;return nullptr;}
bool Enabled(UWorld* W){return W&&W->GetMapName().Contains(TEXT("Bedroom_Study_Rest"))&&FParse::Param(FCommandLine::Get(),TEXT("C13BedroomRestTest"));}
void Aim(ABunkerPlayerController* PC,FVector Target)
{auto* C=Cast<ACharacter>(PC->GetPawn());for(int I=0;I<3;I++){FMinimalViewInfo V;C->CalcCamera(0,V);PC->SetControlRotation((Target-V.Location).Rotation());C->SetActorRotation(FRotator(0,PC->GetControlRotation().Yaw,0));}PC->ClientSetRotation(PC->GetControlRotation(),true);}
}
void C13BedroomRestServer(ABunkerPlayerController* PC,int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!Enabled(PC->GetWorld())||!PC->HasAuthority()||!PC->GetPawn())return;
 auto* B=FindBed(PC->GetWorld());auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if(!B||!PS)return;
 if(Step==90)
 {
  TActorIterator<ABedroomRestTestClock> It(PC->GetWorld());auto* Sync=It?*It:PC->GetWorld()->SpawnActor<ABedroomRestTestClock>();
  Sync->Ready(PC);return;
 }
 if(Step==0||Step==1)
 {
  const bool Acting=Step==0?PC->IsLocalController():!PC->IsLocalController();
  PC->GetPawn()->SetActorLocation(Acting?FVector(245,-235,98):FVector(310,-120,98));
  Aim(PC,Acting?B->GetActorLocation()+FVector(0,0,48):B->GetActorLocation()+FVector(0,-20,80));
  PS->Energy=35;PS->ForceNetUpdate();
 }
 if(Step==2){Aim(PC,B->GetActorLocation()+FVector(49,103,40));}
 if(Step==3)
 {
  int Count=0;for(TActorIterator<ABedroomRestPose>I(PC->GetWorld());I;++I)Count++;
  const bool Pass=!B->Occupant&&Count==0;
  UE_LOG(LogTemp,Display,TEXT("C13_REST_SERVER_RELEASE pass=%d actors=%d"),Pass,Count);
 }
#endif
}
void C13BedroomRestTick(ABunkerPlayerController* PC,float DT)
{
#if !UE_BUILD_SHIPPING
 if(!Enabled(PC->GetWorld())||!PC->IsLocalController()||!PC->GetPawn()||!PC->GetWorld()->GetGameState())return;
 static TWeakObjectPtr<UWorld> W;static int Stage=0;static double Last=0;static TArray<double> Frames;static bool MidEnter=false,MidLeave=false,ReadySent=false;
 if(W.Get()!=PC->GetWorld()){W=PC->GetWorld();Stage=0;Last=0;Frames.Empty();MidEnter=false;MidLeave=false;ReadySent=false;}
 if(!ReadySent&&PC->GetWorld()->GetTimeSeconds()>2){PC->ServerReferenceStep(90);ReadySent=true;}
 TActorIterator<ABedroomRestTestClock> Sync(PC->GetWorld());if(!Sync||Sync->Epoch<0)return;
 const bool Host=PC->HasAuthority();const float T=PC->GetWorld()->GetGameState()->GetServerWorldTimeSeconds()-Sync->Epoch+60;
 const double Now=FPlatformTime::Seconds();if(Last&&T>61&&T<84)Frames.Add(Now-Last);Last=Now;
 auto Key=[&](FKey K){PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Pressed,1.f,false,FPlatformTime::Cycles64()));PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Released,0.f,false,FPlatformTime::Cycles64()));};
 // Observe actual replicated animation state; transport arrival is not a fixed wall-clock instant.
 if(!Host&&Stage>=2&&Stage<=6)
 {
  TActorIterator<ABedroomRestPose> I(PC->GetWorld());auto* P=I?*I:nullptr;
  if(P&&P->Performer)
  {
   const bool Leaving=P->LeaveAt>=0;const float Progress=P->PoseProgress();
   const float HeadZ=P->Performer->GetMesh()->GetBoneLocation(TEXT("head")).Z;
   const bool Waiting=Leaving?!MidLeave:!MidEnter;
   if(Waiting&&Progress>.45f&&Progress<.85f&&HeadZ>105&&HeadZ<155)
   {
    UE_LOG(LogTemp,Display,TEXT("C13_REST_MID leaving=%d pass=1 progress=%.3f head_z=%.2f"),Leaving,Progress,HeadZ);
    FScreenshotRequest::RequestScreenshot(Leaving?TEXT("restpose_client_leave_mid.png"):TEXT("restpose_client_enter_mid.png"),true,false);
    if(Leaving)MidLeave=true;else MidEnter=true;
   }
  }
 }
 const float Times[]={60,62,63,64,66,68,71,72,74,76,78,81,82,82.45f,84,86};
 if(Stage>=UE_ARRAY_COUNT(Times)||T<(Stage==15&&!Host?85.f:Times[Stage]+(Host?0:.12f)))return;
 const int S=Stage++;auto* B=FindBed(PC->GetWorld());if(!B)return;
 if(S==0)PC->ServerReferenceStep(0);
 if(S==7)PC->ServerReferenceStep(1);
 if(Host&&S==1)Key(EKeys::E);
 if(!Host&&S==2)PC->ServerReferenceStep(2);
 if(!Host&&S==3)Key(EKeys::E); // same occupied bed
 if(Host&&S==5)Key(EKeys::F);
 if(!Host&&(S==8||S==12))Key(EKeys::E);
 if(!Host&&(S==10||S==13))Key(EKeys::F);
 if(S==4||S==9)
 {
  TActorIterator<ABedroomRestPose> PoseIt(PC->GetWorld());ABedroomRestPose* P=PoseIt?*PoseIt:nullptr;
  bool Pass=P&&P->Performer&&P->Bed==B&&P->PoseProgress()>.99f&&B->Occupant;
  FVector Head=FVector::ZeroVector,Foot=Head;
  if(P&&P->Performer)
  {
   auto* M=P->Performer->GetMesh();Head=M->GetBoneLocation(TEXT("head"));Foot=(M->GetBoneLocation(TEXT("foot_l"))+M->GetBoneLocation(TEXT("foot_r")))*.5;
   Pass&=Head.Z>60&&Head.Z<110&&Foot.Z>55&&Foot.Z<110&&Head.Y<-345&&Foot.Y>-280&&FMath::Abs(Head.X-117)<45;
  }
  UE_LOG(LogTemp,Display,TEXT("C13_REST_BODY role=%s stage=%d pass=%d head=%s foot=%s"),Host?TEXT("host"):TEXT("client"),S,Pass,*Head.ToString(),*Foot.ToString());
  auto* Own=PC->GetPlayerState<ABunkerPlayerState>();
  UE_LOG(LogTemp,Display,TEXT("C13_REST_STATE role=%s stage=%d acting=%d resting=%d energy=%.3f inventory=%d"),Host?TEXT("host"):TEXT("client"),S,S==4?Host:!Host,Own->RestingBed!=nullptr,Own->Energy,Own->Inventory.Num());
  if(!Host&&S==4)Aim(PC,B->GetActorLocation()+FVector(0,-20,80));
  FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("restpose_%s_%02d.png"),Host?TEXT("host"):TEXT("client"),S),true,false);
 }
 if(S==6||S==11||S==14)
 {
  auto* C=Cast<ACharacter>(PC->GetPawn());auto* PS=PC->GetPlayerState<ABunkerPlayerState>();
  const bool Pass=!PS->RestingBed&&!B->Occupant&&C->GetCharacterMovement()->MovementMode==MOVE_Walking&&C->GetMesh()->GetAnimationMode()==EAnimationMode::AnimationBlueprint&&C->GetMesh()->GetRelativeLocation().Equals(FVector(-20,0,-96),1.f);
  UE_LOG(LogTemp,Display,TEXT("C13_REST_RESTORE role=%s stage=%d pass=%d"),Host?TEXT("host"):TEXT("client"),S,Pass);
  if(Host)PC->ServerReferenceStep(3);
  if(S==6)FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("restpose_%s_standing.png"),Host?TEXT("host"):TEXT("client")),true,false);
 }
 if(S==15)
 {
  double Sum=0;for(double V:Frames)Sum+=V;Frames.Sort();
  UE_LOG(LogTemp,Display,TEXT("C13_REST_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),Frames.Num(),Sum>0?Frames.Num()/Sum:0,Frames.Num()?Frames[FMath::Min(Frames.Num()-1,int(Frames.Num()*.95))]*1000:0);
  FGenericPlatformMisc::RequestExit(false);
 }
#endif
}
