#include "BunkerInfrastructure.h"
#include "BunkerNetwork.h"
#include "BunkerRound.h"
#include "BunkerDoor.h"
#include "BunkerInteractable.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"
void ABunkerPlayerController::ServerInfrastructureProbe_Implementation(int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("C13InfraTest")))return;
 auto* I=ABunkerInfrastructure::Find(GetWorld());auto* R=ABunkerRound::Find(GetWorld());auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();if(!I||!R||!C||!PS||!PS->bSessionReady)return;
 if(Step==0&&IsLocalController())
 {R->Phase=3;R->Gate->bOpen=false;R->Gate->CurrentAngle=0;I->State.Fuel=(FParse::Param(FCommandLine::Get(),TEXT("C13InfraCircuits"))||FParse::Param(FCommandLine::Get(),TEXT("C13InfraWater")))?2.f:.005f;I->State.Condition=65;if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraWear"))){I->State.Fuel=2;I->State.Condition=.005f;}InfraRawBaseline=I->State.Fuel;InfraCleanBaseline=GetWorld()->GetTimeSeconds();I->State.Running=true;if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraWater"))){I->State.RawWater=2;I->State.CleanWater=1;I->State.Filter=50;PS->Water=40;PS->ForceNetUpdate();}I->ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_INFRA_FIXTURE"));return;}
 if(Step==62&&PS->Inventory.ContainsByPredicate([](const auto& E){return E.ItemType==TEXT("FuelCan");}))return;
 if(Step==61){PS->Water=40;PS->ForceNetUpdate();Step=24;}
 if(Step==7){SetControlRotation(FRotator(0,0,0));ClientSetRotation(GetControlRotation(),true);return;}
 if(Step==46){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK wear_stop=%d"),I->State.Condition<=0&&!I->State.Running&&I->State.Fuel>1.9f);return;}
 if(Step==40){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK filtering=%d"),I->Filtering()&&I->State.RawWater<1.99f&&I->State.CleanWater>1.01f);return;}
 if(Step==41){InfraRawBaseline=I->State.RawWater;InfraCleanBaseline=I->State.CleanWater;return;}
 if(Step==42){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK power_stops_filtering=%d"),!I->Filtering()&&FMath::IsNearlyEqual(InfraRawBaseline,I->State.RawWater,.001f)&&FMath::IsNearlyEqual(InfraCleanBaseline,I->State.CleanWater,.001f));return;}
 if(Step==43){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK drink_consumed=%d"),PS->Water>70&&I->State.CleanWater<InfraCleanBaseline-.34f);return;}
 if(Step==44){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK filter_replaced=%d"),I->State.Filter>99.99f);return;}
 if(Step==45){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK finite_water=%d"),ABunkerInfrastructure::Valid(I->State)&&I->State.RawWater<2&&I->State.CleanWater<2&&I->Filtering());return;}
 if(Step==30){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK lights_off=%d emergency=%d"),!I->LightingPowered()&&I->ControlledLightCount()>0,I->EmergencyCount>=4);return;}
 if(Step==31){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK services_off=%d"),!I->ServicesPowered());return;}
 if(Step==32){UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK restored_power=%d"),I->LightingPowered()&&I->ServicesPowered());UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK fuel_saving=%d"),I->State.Fuel>InfraRawBaseline-PS->Rules->FuelLitersPerMinute*(GetWorld()->GetTimeSeconds()-InfraCleanBaseline)/60.f+.002f);return;}
 if(Step>=10&&Step<20)
 {
  if(Step==10)UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK stop=%d"),I->State.Fuel<=0&&!I->State.Running);
  if(Step==11)UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK refuel=%d fuel=%.3f"),FMath::IsNearlyEqual(I->State.Fuel,2.f,.01f),I->State.Fuel);
  if(Step==12)UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK repair=%d condition=%.3f"),FMath::IsNearlyEqual(I->State.Condition,100.f,.01f),I->State.Condition);
  if(Step==13)UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK running=%d fuel=%.3f"),I->State.Running&&I->State.Fuel<2&&I->State.Fuel>1.9f,I->State.Fuel);
  if(Step==14){int N=0;TSet<FGuid> Ids;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)for(auto& E:It->Inventory){N++;Ids.Add(E.Id);}UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CHECK ownership=%d count=%d"),N==Ids.Num(),N);}
  return;
 }
 ABunkerInteractable* A=nullptr;
 const TCHAR* Keys[]={TEXT(""),TEXT("InfraV1_Fuel0"),TEXT("InfraV1_FuelPort"),TEXT("InfraV1_Parts0"),TEXT("InfraV1_RepairPort")};
 for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)if((Step>=1&&Step<=4&&It->WorldKey==Keys[Step])||(Step==5&&It->WorldKey==TEXT("InfraV1_GeneratorSwitch"))||(Step==20&&It->WorldKey==TEXT("InfraV1_LightSwitch"))||(Step==21&&It->WorldKey==TEXT("InfraV1_ServiceSwitch"))||(Step==22&&It->WorldKey==TEXT("InfraV1_WaterStation"))||(Step==23&&It->WorldKey==TEXT("InfraV1_FilterPort"))||(Step==24&&It->WorldKey==TEXT("InfraV1_DrinkPort"))||(Step==25&&It->WorldKey==TEXT("InfraV1_Filter0"))||(Step==62&&It->WorldKey==TEXT("InfraV1_Fuel1"))){A=*It;break;}
 if(!A)return;
 FVector P=A->GetActorLocation()+FVector(IsLocalController()?0:65,110,0);P.Z=100;if(Step==20&&!IsLocalController())P.X=1850;
 C->SetActorRotation(FRotator(0,(A->Mesh->Bounds.Origin-P).Rotation().Yaw,0));
 C->GetCharacterMovement()->StopMovementImmediately();C->SetActorLocation(P);C->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
 for(int J=0;J<3;J++){FMinimalViewInfo V;C->CalcCamera(0,V);SetControlRotation((A->Mesh->Bounds.Origin-V.Location).Rotation());}ClientSetRotation(GetControlRotation(),true);
 UE_LOG(LogTemp,Display,TEXT("C13_INFRA_AIM step=%d target=%s"),Step,*A->WorldKey);
#endif
}
void ABunkerPlayerController::InfrastructureProbeTick()
{
#if !UE_BUILD_SHIPPING
 if(!IsLocalController()||!GetPawn())return;
 auto* I=ABunkerInfrastructure::Find(GetWorld());if(!I)return;const bool Host=HasAuthority();auto* GS=GetWorld()->GetGameState();float T=GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();
 if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraLoad")))
 {if(T>4&&RoundProbeStage==0){RoundProbeStage++;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_LOAD fuel=%.3f condition=%.3f task=%d"),I->State.Fuel,I->State.Condition,I->Task);}if(T>5)FGenericPlatformMisc::RequestExit(false);return;}
 if(Host&&I->TestEpoch==0)
 {int Ready=0;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(It->bSessionReady)Ready++;int Desired=2;FParse::Value(FCommandLine::Get(),TEXT("C13InfraPlayers="),Desired);if(Ready>=FMath::Clamp(Desired,2,4)){I->TestEpoch=T;I->ForceNetUpdate();}}
 if(I->TestEpoch<=0)return;T-=I->TestEpoch;
 const double Wall=FPlatformTime::Seconds();if(T>12&&T<28&&ReferenceWall>0)ReferenceFrames.Add((Wall-ReferenceWall)*1000);ReferenceWall=Wall;
 if(T>29&&ReferenceFrames.Num()){ReferenceFrames.Sort();double Sum=0;for(double X:ReferenceFrames)Sum+=X;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),ReferenceFrames.Num(),1000*ReferenceFrames.Num()/Sum,ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,int(ReferenceFrames.Num()*.95))]);ReferenceFrames.Empty();}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraWear")))
 {if(Host&&T>4&&RoundProbeStage==0){ServerInfrastructureProbe(0);RoundProbeStage=1;}if(Host&&T>6&&RoundProbeStage==1){ServerInfrastructureProbe(46);RoundProbeStage=2;}if(T>(Host?9.f:8.f))FGenericPlatformMisc::RequestExit(false);return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraWater")))
 {
  const float Times[]={4,6,7,7.7f,9,12,13,13.7f,15,16,16.7f,18,18.7f,20,20.7f,22,22.7f,29,30,30.7f,32};const int Actions[]={0,40,21,100,41,42,24,100,43,21,100,22,100,25,100,23,100,44,22,100,45};
  if(Host&&RoundProbeStage<21&&T>Times[RoundProbeStage]){int A=Actions[RoundProbeStage++];if(A==100)ProbeKey(EKeys::E);else if(A==101){auto* PS=GetPlayerState<ABunkerPlayerState>();if(PS&&!PS->Inventory.ContainsByPredicate([](const auto& E){return E.ItemType==TEXT("FuelCan");}))ProbeKey(EKeys::E);}else ServerInfrastructureProbe(A);}
  if(T>34&&ReferenceStage==0){ReferenceStage=1;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_WATER_FINAL role=%s raw=%.3f clean=%.3f filter=%.3f"),Host?TEXT("host"):TEXT("client"),I->State.RawWater,I->State.CleanWater,I->State.Filter);FScreenshotRequest::RequestScreenshot(Host?TEXT("infra_water_host.png"):TEXT("infra_water_client.png"),true,false);if(Host)C13Save();}
  if(T>(Host?39.f:37.f))FGenericPlatformMisc::RequestExit(false);return;
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("C13InfraCircuits")))
 {
  const float Times[]={4,6,6.7f,8,10,10.7f,12,14,14.7f,16,16.7f,18};const int Actions[]={0,20,100,30,21,100,31,20,100,21,100,32};
  if(Host&&RoundProbeStage<12&&T>Times[RoundProbeStage]){int A=Actions[RoundProbeStage++];if(A==100)ProbeKey(EKeys::E);else if(A==101){auto* PS=GetPlayerState<ABunkerPlayerState>();if(PS&&!PS->Inventory.ContainsByPredicate([](const auto& E){return E.ItemType==TEXT("FuelCan");}))ProbeKey(EKeys::E);}else ServerInfrastructureProbe(A);}
  if(T>8&&ReferenceStage==0){ReferenceStage=1;FScreenshotRequest::RequestScreenshot(Host?TEXT("infra_circuits_off_host.png"):TEXT("infra_circuits_off_client.png"),true,false);}
  if(T>19&&ReferenceStage==1){ReferenceStage=2;FScreenshotRequest::RequestScreenshot(Host?TEXT("infra_circuits_on_host.png"):TEXT("infra_circuits_on_client.png"),true,false);}
  if(T>(Host?23.f:21.f))FGenericPlatformMisc::RequestExit(false);return;
 }
 struct FStep{float Time;int Action;};const FStep Steps[]={{4,0},{6,10},{6.3f,1},{7,100},{7.25f,62},{7.8f,101},{8,2},{8.6f,100},{10,7},{11,2},{11.7f,100},{18,11},{18.3f,3},{19,100},{20,4},{20.7f,100},{27,12},{27.3f,5},{28,100},{32,13},{33,5},{33.7f,100},{34.5f,14}};
 if(Host&&RoundProbeStage<UE_ARRAY_COUNT(Steps)&&T>Steps[RoundProbeStage].Time)
 {const int A=Steps[RoundProbeStage++].Action;if(A==100)ProbeKey(EKeys::E);else if(A==101){auto* PS=GetPlayerState<ABunkerPlayerState>();if(PS&&!PS->Inventory.ContainsByPredicate([](const auto& E){return E.ItemType==TEXT("FuelCan");}))ProbeKey(EKeys::E);}else ServerInfrastructureProbe(A);}
 int Role=Host?0:1;FParse::Value(FCommandLine::Get(),TEXT("C13InfraRole="),Role);
 if(Role>=2)
 {
  if(Role==2&&T>30&&RoundProbeStage==0){ServerInfrastructureProbe(20);RoundProbeStage=1;}
  if(Role==2&&T>31&&RoundProbeStage==1){ProbeKey(EKeys::E);RoundProbeStage=2;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_REMOTE role=2 interacted=1"));}
  if(Role==2&&T>33&&RoundProbeStage==2&&I->State.Lights){ProbeKey(EKeys::E);RoundProbeStage=3;}
  if(Role==3&&T>14&&RoundProbeStage==0){ServerInfrastructureProbe(61);RoundProbeStage=1;}
  if(Role==3&&T>15&&RoundProbeStage==1){ProbeKey(EKeys::E);RoundProbeStage=2;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_REMOTE role=3 interacted=1"));}
 }
 if(!Host&&Role==1&&T>6.3f&&RoundProbeStage==0){ServerInfrastructureProbe(1);RoundProbeStage=1;}
 if(!Host&&Role==1&&T>7.1f&&RoundProbeStage==1){ProbeKey(EKeys::E);RoundProbeStage=2;}
 if(T>35&&ReferenceStage==0&&(Host||(!I->State.Running&&I->State.Condition>90&&I->State.Condition<99.95f&&I->State.Fuel>1.9f)))
 {ReferenceStage=1;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_FINAL role=%s fuel=%.3f condition=%.3f running=%d"),Host?TEXT("host"):TEXT("client"),I->State.Fuel,I->State.Condition,I->State.Running);FScreenshotRequest::RequestScreenshot(Host?TEXT("infra_generator_host.png"):TEXT("infra_generator_client.png"),true,false);if(Host)C13Save();}
 if((Host&&T>45)||(!Host&&T>37&&ReferenceStage>0))FGenericPlatformMisc::RequestExit(false);
#endif
}
