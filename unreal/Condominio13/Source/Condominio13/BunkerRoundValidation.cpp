#include "BunkerRound.h"
#include "BunkerNetwork.h"
#include "BunkerDoor.h"
#include "BunkerInteractable.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"
void ABunkerPlayerController::ServerStartRound_Implementation(){if(auto* R=ABunkerRound::Find(GetWorld()))R->Start(this);}
void ABunkerPlayerController::ServerCancelRoundRelease_Implementation(){if(auto* R=ABunkerRound::Find(GetWorld()))R->Cancel(this);}
AActor* ABunkerGameMode::ChoosePlayerStart_Implementation(AController* Player)
{
 if(FParse::Param(FCommandLine::Get(),TEXT("C13Round")))
 {
  TArray<APlayerStart*> Starts;for(TActorIterator<APlayerStart> It(GetWorld());It;++It)if(It->PlayerStartTag==TEXT("C13_RoundMarket"))Starts.Add(*It);
  Starts.Sort([](const APlayerStart& A,const APlayerStart& B){return A.GetName()<B.GetName();});
  if(Starts.Num())return Starts[(FMath::Max(1,GetNumPlayers())-1)%Starts.Num()];
 }
 return Super::ChoosePlayerStart_Implementation(Player);
}
void ABunkerPlayerController::ServerRoundProbe_Implementation(int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest")))return;
 auto* C=Cast<ACharacter>(GetPawn());auto* R=ABunkerRound::Find(GetWorld());auto* PS=GetPlayerState<ABunkerPlayerState>();if(!C||!R||!R->Gate||!PS)return;
 if(Step==0||Step==1||Step==5)
 {
  FVector P,Aim;
  if(Step==0||Step==5){ABunkerInteractable* Item=nullptr;for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("C13_RoundLootFirst"))){Item=*It;break;}if(!Item||!Item->Mesh->GetStaticMesh())return;Aim=Item->Mesh->GetComponentTransform().TransformPosition(Item->Mesh->GetStaticMesh()->GetBounds().Origin);P=Step==5?C->GetActorLocation():Item->GetActorLocation()+FVector(IsLocalController()?0:80,120,0);if(Step==0)P.Z=410;}
  else{P=FVector(2550,IsLocalController()?-300:120,100);Aim=FVector(2550,-20,110);if(!IsLocalController()){PS->Energy=0;PS->ForceNetUpdate();}}
  C->GetCharacterMovement()->StopMovementImmediately();C->SetActorLocation(P);C->SetActorRotation(FRotator(0,(Aim-P).Rotation().Yaw,0));
  for(int I=0;I<3;I++){FMinimalViewInfo V;C->CalcCamera(0,V);SetControlRotation((Aim-V.Location).Rotation());}ClientSetRotation(GetControlRotation(),true);
  UE_LOG(LogTemp,Display,TEXT("C13_ROUND_AIM step=%d pawn=%s target=%s rotation=%s"),Step,*P.ToString(),*Aim.ToString(),*GetControlRotation().ToString());
 }
 if(Step==2)
 {
  int Count=0;TSet<FGuid> Ids;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)for(auto& E:It->Inventory){Count++;Ids.Add(E.Id);}
  UE_LOG(LogTemp,Display,TEXT("C13_ROUND_PICKUP_AUDIT count=%d unique=%d id=%s"),Count,Ids.Num(),Ids.Num()==1?*Ids.Array()[0].ToString(EGuidFormats::Digits):TEXT("none"));
 }
 if(Step==3)UE_LOG(LogTemp,Display,TEXT("C13_ROUND_OUTSIDE_ALIVE phase=%d angle=%.1f health=%.1f outside=%d"),R->Phase,R->Gate->CurrentAngle,PS->Health,C->GetActorLocation().Y>0);
 if(Step==4){const bool OK=R->Phase==3&&C->GetActorLocation().Y<-80&&PS->Health>0;UE_LOG(LogTemp,Display,TEXT("C13_ROUND_RETURN pass=%d y=%.1f energy=%.1f"),OK,C->GetActorLocation().Y,PS->Energy);}
#endif
}
void ABunkerPlayerController::RoundProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
 if(!IsLocalController()||!FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest"))||!GetPawn())return;
 if(FParse::Param(FCommandLine::Get(),TEXT("C13SupplyTest"))){SupplyProbeTick();return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13AirlockTest"))){AirlockProbeTick();return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraTest"))){InfrastructureProbeTick();return;}
 auto* R=ABunkerRound::Find(GetWorld());if(!R)return;const float T=GetWorld()->GetGameState()?GetWorld()->GetGameState()->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();const bool Host=HasAuthority();
 if(FParse::Param(FCommandLine::Get(),TEXT("C13ClockLoad")))
 {if(T>4&&RoundProbeStage==0){RoundProbeStage=1;UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_LOAD_CHECK elapsed=%.3f day=%d day_seconds=%.1f phase=%d"),R->ShelterSeconds(),R->SurvivalDay(),R->DaySeconds,R->Phase);FScreenshotRequest::RequestScreenshot(TEXT("clock_resumed.png"),true,false);}if(T>5)FGenericPlatformMisc::RequestExit(false);return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13ClockSave"))&&T>52)
 {UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_SEED elapsed=%.3f day=%d"),R->ShelterSeconds(),R->SurvivalDay());C13Save();FGenericPlatformMisc::RequestExit(false);return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundWalkTest")))
 {
  if(T<4)return;
  auto* C=Cast<ACharacter>(GetPawn());if(!C)return;
  const FVector2D Targets[]={{2550,900},{2550,800},{2550,650},{2550,500},{2550,350},{2550,210},{2550,80},{2550,-150},{2550,-450},{2550,-800},{2100,-1000},{1500,-1000},{1150,-800}};
  if(RoundProbeStage==0){C->SetActorLocation(FVector(2550,1000,410));C->GetCharacterMovement()->SetMovementMode(MOVE_Walking);RoundProbeStage=1;FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(RoundOpening),true,C);const bool Hit=GetWorld()->LineTraceSingleByChannel(H,FVector(2550,500,400),FVector(2550,500,-50),ECC_Visibility,Q);UE_LOG(LogTemp,Display,TEXT("C13_ROUND_FLOOR_HOLE pass=%d height=%.1f"),Hit&&H.ImpactPoint.Z<250,H.ImpactPoint.Z);}
  const int I=RoundProbeStage-1;
  if(I<UE_ARRAY_COUNT(Targets))
  {const FVector P=C->GetActorLocation();FVector Dir(Targets[I].X-P.X,Targets[I].Y-P.Y,0);if(Dir.Size()<35){UE_LOG(LogTemp,Display,TEXT("C13_ROUND_WALK_STEP step=%d z=%.1f"),I,P.Z);RoundProbeStage++;if(I==4)FScreenshotRequest::RequestScreenshot(TEXT("round_stair_walk.png"),true,false);}else{C->AddMovementInput(Dir.GetSafeNormal(),.6f);SetControlRotation(Dir.Rotation());}}
  else{UE_LOG(LogTemp,Display,TEXT("C13_ROUND_WALK_PASS y=%.1f z=%.1f"),C->GetActorLocation().Y,C->GetActorLocation().Z);FScreenshotRequest::RequestScreenshot(TEXT("round_walk_arrival.png"),true,false);if(T>20)FGenericPlatformMisc::RequestExit(false);}
  if(T>40){UE_LOG(LogTemp,Display,TEXT("C13_ROUND_WALK_TIMEOUT step=%d position=%s"),I,*C->GetActorLocation().ToString());FGenericPlatformMisc::RequestExit(false);}return;
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundLoadCheck")))
 {if(T>4&&RoundProbeStage==0){auto* PS=GetPlayerState<ABunkerPlayerState>();UE_LOG(LogTemp,Display,TEXT("C13_ROUND_LOAD_CHECK phase=%d remaining=%.1f inventory=%d id=%s"),R->Phase,R->Remaining(),PS?PS->Inventory.Num():-1,PS&&PS->Inventory.Num()?*PS->Inventory[0].Id.ToString(EGuidFormats::Digits):TEXT("none"));RoundProbeStage=1;}if(T>5)FGenericPlatformMisc::RequestExit(false);return;}
 if(T>5&&RoundProbeStage==0){ProbeKey(EKeys::R);RoundProbeStage=1;}
 if(T>7&&RoundProbeStage==1){ServerRoundProbe(0);RoundProbeStage=2;}
 if(T>7.5&&RoundProbeStage==2&&ReferenceNextFrame==0){ReferenceNextFrame=1;ServerRoundProbe(5);}
 if(T>(Host?8.f:8.1f)&&RoundProbeStage==2){ProbeKey(EKeys::E);RoundProbeStage=3;}
 if(T>10&&RoundProbeStage==3){ServerRoundProbe(2);RoundProbeStage=4;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundSaveEarly"))){if(T>12){C13Save();FGenericPlatformMisc::RequestExit(false);}return;}
 const double Wall=FPlatformTime::Seconds();if(T>12&&T<28&&ReferenceWall>0)ReferenceFrames.Add((Wall-ReferenceWall)*1000);ReferenceWall=Wall;
 if(T>20&&ReferenceStage==0){ReferenceStage=1;FVector Eye;FRotator View;GetPlayerViewPoint(Eye,View);FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(RoundCamera),true,GetPawn());GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+View.Vector()*1000,ECC_Visibility,Q);UE_LOG(LogTemp,Display,TEXT("C13_ROUND_CAMERA pawn=%s eye=%s view=%s control=%s hit=%s point=%s"),*GetPawn()->GetActorLocation().ToString(),*Eye.ToString(),*View.ToString(),*GetControlRotation().ToString(),*GetNameSafe(Hit.GetActor()),*Hit.ImpactPoint.ToString());FScreenshotRequest::RequestScreenshot(Host?TEXT("round_host_collection.png"):TEXT("round_client_collection.png"),true,false);}
 if(T>29&&ReferenceFrames.Num()){ReferenceFrames.Sort();double Sum=0;for(double X:ReferenceFrames)Sum+=X;UE_LOG(LogTemp,Display,TEXT("C13_ROUND_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),ReferenceFrames.Num(),1000*ReferenceFrames.Num()/Sum,ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,int(ReferenceFrames.Num()*.95))]);ReferenceFrames.Empty();}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundVisualOnly"))){if(T>22)FGenericPlatformMisc::RequestExit(false);return;}
 if(T>37&&RoundProbeStage==4){ServerRoundProbe(1);RoundProbeStage=5;}
 if(T>43&&RoundProbeStage==5){ServerRoundProbe(3);FScreenshotRequest::RequestScreenshot(Host?TEXT("round_host_closed.png"):TEXT("round_client_closed.png"),true,false);RoundProbeStage=6;}
 auto Key=[this](FKey K,EInputEvent Event){InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,Event,Event==IE_Pressed?1.f:0.f,false,FPlatformTime::Cycles64()));};
 if(!Host&&T>44&&RoundProbeStage==6){Key(EKeys::E,IE_Pressed);RoundProbeStage=7;}
 if(!Host&&T>46&&RoundProbeStage==7){Key(EKeys::E,IE_Released);RoundProbeStage=8;}
 if(!Host&&T>48&&RoundProbeStage==8){Key(EKeys::E,IE_Pressed);RoundProbeStage=9;}
 if(!Host&&T>85&&RoundProbeStage==9){Key(EKeys::E,IE_Released);Key(EKeys::W,IE_Pressed);RoundProbeStage=10;}
 if(!Host&&T>86.5&&RoundProbeStage==10){Key(EKeys::W,IE_Released);ServerRoundProbe(4);RoundProbeStage=11;}
 if(T>88&&RoundProbeStage!=12){RoundProbeStage=12;UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_FINAL role=%s elapsed=%.3f day=%d day_seconds=%.1f"),Host?TEXT("host"):TEXT("client"),R->ShelterSeconds(),R->SurvivalDay(),R->DaySeconds);UE_LOG(LogTemp,Display,TEXT("C13_ROUND_CLIENT_FINAL role=%s phase=%d open=%d"),Host?TEXT("host"):TEXT("client"),R->Phase,R->Gate?R->Gate->bOpen:0);FScreenshotRequest::RequestScreenshot(Host?TEXT("round_host_final.png"):TEXT("round_client_final.png"),true,false);}
 if(T>(Host?94.f:89.f))FGenericPlatformMisc::RequestExit(false);
#endif
}
