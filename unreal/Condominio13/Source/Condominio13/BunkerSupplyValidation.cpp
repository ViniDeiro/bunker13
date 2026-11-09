#include "BunkerNetwork.h"
#include "BunkerInfrastructure.h"
#include "BunkerInteractable.h"
#include "BunkerRound.h"
#include "BunkerDoor.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "InputKeyEventArgs.h"
#include "UnrealClient.h"
#include "HAL/PlatformTime.h"

namespace {
ABunkerInteractable* SupplyActor(UWorld* W,const TCHAR* Key)
{for(TActorIterator<ABunkerInteractable> It(W);It;++It)if(It->WorldKey==Key)return *It;return nullptr;}
void SupplyAim(ABunkerPlayerController* PC,AActor* A)
{
 auto* C=Cast<ACharacter>(PC->GetPawn());if(!C||!A)return;
 FVector Aim=A->GetActorLocation();
 if(auto* D=Cast<ABunkerDoor>(A))Aim=D->GetActorTransform().TransformPosition(FVector(D->Width*.5f,0,D->Height*.5f));
 else if(auto* Item=Cast<ABunkerInteractable>(A))Aim=Item->Mesh->Bounds.Origin;
 for(int J=0;J<3;J++){FMinimalViewInfo V;C->CalcCamera(0,V);PC->SetControlRotation((Aim-V.Location).Rotation());}PC->ClientSetRotation(PC->GetControlRotation(),true);
}
}
void ABunkerPlayerController::ServerSupplyProbe_Implementation(int32 Step)
{
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("C13SupplyTest"))||!FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest")))return;
 auto* I=ABunkerInfrastructure::Find(GetWorld());auto* R=ABunkerRound::Find(GetWorld());auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();if(!I||!R||!C||!PS||!PS->bSessionReady)return;
 if(Step==0&&IsLocalController())
 {
  I->State.Fuel=0;I->State.Condition=20;I->State.Running=false;I->ForceNetUpdate();
  R->Gate->bOpen=false;R->Gate->CurrentAngle=0;R->InnerGate->bOpen=false;R->InnerGate->CurrentAngle=0;
  int N=0;for(TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)if(auto* Pawn=Cast<ACharacter>(It->GetPawn()))
  {Pawn->GetCharacterMovement()->StopMovementImmediately();Pawn->SetActorLocation(*It==this?FVector(2550,-900,100):FVector(1000+N++*140,-950,100));}
  UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_TRIP_START initial_fixture_only=1"));
 }
 if(Step==1)
 {
  int Role=0;FParse::Value(FCommandLine::Get(),TEXT("C13SupplyRole="),Role);
  C->GetCharacterMovement()->StopMovementImmediately();C->SetActorLocation(FVector(2650+Role*110,3020,392));
  SupplyAim(this,SupplyActor(GetWorld(),TEXT("SupplyV1_0")));
 }
 if(Step>=3&&Step<=5&&IsLocalController())
 {
  auto* A=SupplyActor(GetWorld(),TEXT("SupplyV1_0"));if(!A)return;
  const bool Untouched=A->bActive&&!PS->Inventory.ContainsByPredicate([&](const auto& E){return E.Id==A->ItemId;});
  if(Step==4)UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_CAPACITY slots=%d"),Untouched&&PS->Inventory.Num()==PS->Rules->MaxSlots);
  if(Step==5)UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_CAPACITY weight=%d"),Untouched&&PS->Inventory.Num()<PS->Rules->MaxSlots&&PS->Weight()<=PS->Rules->MaxWeightKg&&PS->Weight()+PS->Rules->Find(TEXT("FuelCan"))->WeightKg>PS->Rules->MaxWeightKg);
  PS->Inventory.Reset();
  if(Step!=5)
  {
   const FName Type=Step==3?FName(TEXT("Battery")):FName(TEXT("FuelCan"));const auto* Def=PS->Rules->Find(Type);if(!Def)return;
   const int N=Step==3?PS->Rules->MaxSlots:FMath::FloorToInt((PS->Rules->MaxWeightKg-Def->WeightKg*.5f)/Def->WeightKg);
   for(int J=0;J<N;J++){FBunkerInventoryEntry E;E.Id=FGuid::NewGuid();E.ItemType=Type;E.WeightKg=Def->WeightKg;E.Name=TEXT("Test capacity fixture");E.WorldMesh=A->Mesh->GetStaticMesh();E.WorldScale=FVector::OneVector;PS->Inventory.Add(E);}
  }
  PS->ForceNetUpdate();return;
 }
 if(Step==2)
 {
  auto* A=SupplyActor(GetWorld(),TEXT("SupplyV1_0"));if(!A)return;int Owners=0;
  for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)for(const auto& E:It->Inventory)if(E.Id==A->ItemId)Owners++;
  UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_RACE pass=%d owners=%d active=%d remote_owner=%d id=%s"),Owners==1&&!A->bActive,Owners,A->bActive,!PS->Inventory.ContainsByPredicate([&](const auto& E){return E.Id==A->ItemId;}),*A->ItemId.ToString(EGuidFormats::Digits));
 }
#endif
}
void ABunkerPlayerController::SupplyProbeTick()
{
#if !UE_BUILD_SHIPPING
 auto* C=Cast<ACharacter>(GetPawn());auto* PS=GetPlayerState<ABunkerPlayerState>();auto* I=ABunkerInfrastructure::Find(GetWorld());auto* R=ABunkerRound::Find(GetWorld());
 if(!C||!PS||!PS->bSessionReady||!I||!R||!R->Gate||!R->InnerGate)return;
 const bool Host=HasAuthority(),Race=FParse::Param(FCommandLine::Get(),TEXT("C13SupplyRace")),Load=FParse::Param(FCommandLine::Get(),TEXT("C13SupplyLoad")),Continue=FParse::Param(FCommandLine::Get(),TEXT("C13SupplyContinue"));
 const float Now=GetWorld()->GetGameState()->GetServerWorldTimeSeconds();
 auto Key=[this](EInputEvent Event){InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,EKeys::E,Event,Event==IE_Pressed?1.f:0.f,false,FPlatformTime::Cycles64()));};
 auto Press=[&](){Key(IE_Pressed);Key(IE_Released);};
 if(Load)
 {
  if(Host&&Now>5&&RoundProbeStage==0)
  {
   RoundProbeStage=1;int Count=0,Dead=0;for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)if(ABunkerInfrastructure::SupplyExtension(*It)){Count++;if(!It->bActive)Dead++;UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_ID key=%s id=%s active=%d"),*It->WorldKey,*It->ItemId.ToString(EGuidFormats::Digits),It->bActive);}
   UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_LOAD pass=%d count=%d inactive=%d fuel=%.3f condition=%.3f"),Count==6&&Dead==2&&I->State.Fuel>1.8f&&I->State.Condition>55,Count,Dead,I->State.Fuel,I->State.Condition);
   GetWorld()->GetAuthGameMode<ABunkerGameMode>()->SupplyPersistenceAudit();FScreenshotRequest::RequestScreenshot(TEXT("supply_resumed.png"),true,false);
  }
  if(Now>8)FGenericPlatformMisc::RequestExit(false);return;
 }
 if(Host&&I->TestEpoch==0)
 {
  int Ready=0;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(It->bSessionReady)Ready++;
  int Desired=1;FParse::Value(FCommandLine::Get(),TEXT("C13SupplyPlayers="),Desired);
  if(Ready>=Desired)
  {if(Race){R->Phase=3;I->TestEpoch=Now;I->ForceNetUpdate();}else if(R->Phase==0)ProbeKey(EKeys::R);else if(R->Phase==3){I->TestEpoch=Now;I->ForceNetUpdate();}}
 }
 if(I->TestEpoch==0)return;const float T=Now-I->TestEpoch;
 if(Race)
 {
  if(T>2&&RoundProbeStage==0){ServerSupplyProbe(1);if(Host)ServerSupplyProbe(3);RoundProbeStage=1;}
  if(Host&&T>3&&RoundProbeStage==1){Press();RoundProbeStage=2;}
  if(Host&&T>4&&RoundProbeStage==2){ServerSupplyProbe(4);RoundProbeStage=3;}
  if(Host&&T>5&&RoundProbeStage==3){Press();RoundProbeStage=4;}
  if(Host&&T>6&&RoundProbeStage==4){ServerSupplyProbe(5);RoundProbeStage=5;}
  if(T>(Host?8.5f:8.f)&&((Host&&RoundProbeStage==5)||(!Host&&RoundProbeStage==1))){Press();RoundProbeStage=6;}
  if(Host&&T>11&&RoundProbeStage==6){ServerSupplyProbe(2);GetWorld()->GetAuthGameMode<ABunkerGameMode>()->SupplyPersistenceAudit();RoundProbeStage=7;}
  if(T>(Host?16.f:14.f))FGenericPlatformMisc::RequestExit(false);return;
 }
 const double Wall=FPlatformTime::Seconds();if(T>2&&T<18&&ReferenceWall>0)ReferenceFrames.Add((Wall-ReferenceWall)*1000);ReferenceWall=Wall;
 if(T>19&&ReferenceFrames.Num()){ReferenceFrames.Sort();double Sum=0;for(double X:ReferenceFrames)Sum+=X;UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_FPS role=%s samples=%d fps=%.2f p95_ms=%.2f"),Host?TEXT("host"):TEXT("client"),ReferenceFrames.Num(),1000*ReferenceFrames.Num()/Sum,ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,int(ReferenceFrames.Num()*.95))]);ReferenceFrames.Empty();}
 if(!Host)
 {
  if(I->Powered()&&I->State.Fuel>1&&I->State.Condition>50&&ReferenceStage==0)
  {ReferenceStage=1;UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_CLIENT_POWER fuel=%.3f condition=%.3f"),I->State.Fuel,I->State.Condition);int Role=1;FParse::Value(FCommandLine::Get(),TEXT("C13SupplyRole="),Role);if(Role==1)FScreenshotRequest::RequestScreenshot(TEXT("supply_bunker_client.png"),true,false);}
  return;
 }
 auto* Fuel=SupplyActor(GetWorld(),TEXT("SupplyV1_0"));auto* Parts=SupplyActor(GetWorld(),TEXT("SupplyV1_2"));if(!Fuel||!Parts)return;
 auto Has=[&](FGuid Id){return PS->Inventory.ContainsByPredicate([&](const auto& E){return E.Id==Id;});};
 if(RoundProbeStage==0&&T>2)
 {
  SupplyFuelId=Fuel->ItemId;SupplyPartsId=Parts->ItemId;
  if(Continue){UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_RESUME_OUTSIDE pass=%d y=%.1f"),Has(SupplyFuelId)&&Has(SupplyPartsId)&&C->GetActorLocation().Y>2500,C->GetActorLocation().Y);RoundProbeStage=11;}
  else{ServerSupplyProbe(0);RoundProbeStage=1;}
 }
 auto Move=[&](const TArray<FVector2D>& Points)->bool
 {
  if(SupplyWalkIndex>=Points.Num()){SupplyWalkIndex=0;return true;}
  const FVector P=C->GetActorLocation();const auto Target=Points[SupplyWalkIndex];FVector D(Target.X-P.X,Target.Y-P.Y,0);
  if(D.Size()<12){UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_WALK stage=%d point=%d x=%.1f y=%.1f z=%.1f"),RoundProbeStage,SupplyWalkIndex,P.X,P.Y,P.Z);SupplyWalkIndex++;}
  else{C->AddMovementInput(D.GetSafeNormal(),.6f);SetControlRotation(D.Rotation());}return false;
 };
 auto Door=[&](ABunkerDoor* D,bool Open)->bool
 {
  SupplyAim(this,D);
  if(D->bOpen==Open&&FMath::Abs(D->CurrentAngle-(Open?D->OpenAngle:0))<.5f){if(SupplyHeld){Key(IE_Released);SupplyHeld=false;}return true;}
  if(D->bOpen==Open||Now<SupplyNextAction)return false;
  if(Open&&R->AirlockDeadline>Now)return false;
  if(SupplyHeld)return false;
  SupplyNextAction=Now+1;
  if(Open&&D==R->Gate&&C->GetActorLocation().Y>D->GetActorLocation().Y+40&&R->AirlockTarget==2&&R->AirlockDeadline>0)
  {Key(IE_Pressed);SupplyHeld=true;}else Press();return false;
 };
 auto Use=[&](const TCHAR* KeyName){auto* A=SupplyActor(GetWorld(),KeyName);if(A){SupplyAim(this,A);if(Now>SupplyNextAction){SupplyNextAction=Now+1;Press();}}};
 if(RoundProbeStage==1&&Door(R->InnerGate,true))RoundProbeStage=2;
 else if(RoundProbeStage==2&&Move({{2550,-330}}))RoundProbeStage=3;
 else if(RoundProbeStage==3&&Door(R->InnerGate,false))RoundProbeStage=4;
 else if(RoundProbeStage==4&&Door(R->Gate,true))RoundProbeStage=5;
 else if(RoundProbeStage==5&&Move({{2550,160}}))RoundProbeStage=6;
 else if(RoundProbeStage==6&&Door(R->Gate,false))RoundProbeStage=7;
 else if(RoundProbeStage==7&&Move({{2550,350},{2550,500},{2550,650},{2550,800},{2550,900},{2650,900},{2650,1800},{2750,1850},{2750,2250},{2750,2600},{2860,3070}}))RoundProbeStage=8;
 else if(RoundProbeStage==8){if(Has(SupplyFuelId))RoundProbeStage=9;else Use(TEXT("SupplyV1_0"));}
 else if(RoundProbeStage==9){if(Has(SupplyPartsId))RoundProbeStage=10;else Use(TEXT("SupplyV1_2"));}
 else if(RoundProbeStage==10)
 {
  UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_COLLECTED fuel=%s parts=%s y=%.1f"),*SupplyFuelId.ToString(EGuidFormats::Digits),*SupplyPartsId.ToString(EGuidFormats::Digits),C->GetActorLocation().Y);
  C13Save();FScreenshotRequest::RequestScreenshot(TEXT("supply_exterior.png"),true,false);RoundProbeStage=11;
  if(FParse::Param(FCommandLine::Get(),TEXT("C13SupplySeedOutside"))){UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_SEED_OUTSIDE"));FGenericPlatformMisc::RequestExit(false);return;}
 }
 else if(RoundProbeStage==11&&Move({{2750,2600},{2750,2250},{2750,1850},{2650,1800},{2650,900},{2550,900},{2550,800},{2550,650},{2550,500},{2550,350},{2550,160}}))RoundProbeStage=12;
 else if(RoundProbeStage==12&&Door(R->Gate,true))RoundProbeStage=13;
 else if(RoundProbeStage==13&&Move({{2550,-330}}))RoundProbeStage=14;
 else if(RoundProbeStage==14&&Door(R->Gate,false))RoundProbeStage=15;
 else if(RoundProbeStage==15&&Door(R->InnerGate,true))RoundProbeStage=16;
 else if(RoundProbeStage==16&&Move({{2550,-900},{2100,-1000},{1900,-1350},{1740,-1390}}))RoundProbeStage=17;
 else if(RoundProbeStage==17){if(!Has(SupplyFuelId)&&I->State.Fuel>1.9f)RoundProbeStage=18;else if(I->Task==0)Use(TEXT("InfraV1_FuelPort"));}
 else if(RoundProbeStage==18){if(!Has(SupplyPartsId)&&I->State.Condition>59)RoundProbeStage=19;else if(I->Task==0)Use(TEXT("InfraV1_RepairPort"));}
 else if(RoundProbeStage==19){if(I->Powered()){SupplyNextAction=Now+4;RoundProbeStage=20;}else Use(TEXT("InfraV1_GeneratorSwitch"));}
 else if(RoundProbeStage==20&&Now>SupplyNextAction)
 {
  const bool OK=!Fuel->bActive&&!Parts->bActive&&!Has(SupplyFuelId)&&!Has(SupplyPartsId)&&I->Powered()&&I->State.Fuel>1.8f&&I->State.Condition>58;
  UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_RESTORED pass=%d fuel_id=%s parts_id=%s fuel=%.3f condition=%.3f"),OK,*SupplyFuelId.ToString(EGuidFormats::Digits),*SupplyPartsId.ToString(EGuidFormats::Digits),I->State.Fuel,I->State.Condition);
  for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)if(ABunkerInfrastructure::SupplyExtension(*It))UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_ID key=%s id=%s active=%d"),*It->WorldKey,*It->ItemId.ToString(EGuidFormats::Digits),It->bActive);
  GetWorld()->GetAuthGameMode<ABunkerGameMode>()->SupplyPersistenceAudit();FScreenshotRequest::RequestScreenshot(TEXT("supply_power_restored.png"),true,false);RoundProbeStage=21;SupplyNextAction=Now+3;
 }
 else if(RoundProbeStage==21&&Now>SupplyNextAction)FGenericPlatformMisc::RequestExit(false);
 if(C->GetActorLocation().Z<-100){UE_LOG(LogTemp,Error,TEXT("C13_SUPPLY_FALL stage=%d point=%d position=%s"),RoundProbeStage,SupplyWalkIndex,*C->GetActorLocation().ToString());FGenericPlatformMisc::RequestExit(false);return;}
 if(T>240){UE_LOG(LogTemp,Error,TEXT("C13_SUPPLY_TIMEOUT stage=%d point=%d position=%s"),RoundProbeStage,SupplyWalkIndex,*C->GetActorLocation().ToString());FGenericPlatformMisc::RequestExit(false);}
#endif
}
