#include "BunkerRound.h"
#include "BunkerNetwork.h"
#include "BunkerDoor.h"
#include "BunkerInfrastructure.h"
#include "Components/BoxComponent.h"
#include "EngineUtils.h"
#include "GameFramework/GameStateBase.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Sound/SoundBase.h"
#include "GameFramework/Character.h"
ABunkerRound::ABunkerRound(){bReplicates=true;bAlwaysRelevant=true;PrimaryActorTick.bCanEverTick=true;SetNetUpdateFrequency(10);}
ABunkerRound* ABunkerRound::Find(UWorld* W){TActorIterator<ABunkerRound> It(W);return It?*It:nullptr;}
float ABunkerRound::ServerNow() const {auto* S=GetWorld()->GetGameState();return S?S->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();}
double ABunkerRound::ShelterSeconds() const
{return ShelterElapsed+(Phase==3&&ShelterAnchor>=0?FMath::Max(0.f,ServerNow()-ShelterAnchor):0.f);}
int32 ABunkerRound::SurvivalDay() const
{return 1+FMath::FloorToInt(ShelterSeconds()/FMath::Max(1.f,DaySeconds));}
int32 ABunkerRound::DayMinute() const
{return FMath::FloorToInt(FMath::Fmod(ShelterSeconds(),double(FMath::Max(1.f,DaySeconds)))/FMath::Max(1.f,DaySeconds)*1440.0);}
float ABunkerRound::Remaining() const{return FMath::Max(0.f,Deadline-ServerNow());}
void ABunkerRound::BeginPlay()
{
 Super::BeginPlay();
 if(HasAuthority())
 {
  bAirlockEnabled=FParse::Param(FCommandLine::Get(),TEXT("C13Expedition"));
  // Locate the existing inner leaf without renaming any authored persistence key.
  for(TActorIterator<ABunkerDoor> It(GetWorld());It;++It)
   if(FVector::DistSquared(It->GetActorLocation(),FVector(2462,-640,0))<FMath::Square(10.f))InnerGate=*It;
  if(bAirlockEnabled&&!InnerGate)UE_LOG(LogTemp,Error,TEXT("C13_AIRLOCK_MISSING_INNER"));
 }
 if(HasAuthority())for(TActorIterator<ABunkerDoor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("C13_CollectionGate"))){Gate=*It;break;}
}
void ABunkerRound::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ABunkerRound,bAirlockManual);DOREPLIFETIME(ABunkerRound,InnerGate);DOREPLIFETIME(ABunkerRound,bAirlockEnabled);DOREPLIFETIME(ABunkerRound,AirlockTarget);DOREPLIFETIME(ABunkerRound,AirlockDeadline);DOREPLIFETIME(ABunkerRound,ShelterElapsed);DOREPLIFETIME(ABunkerRound,ShelterAnchor);DOREPLIFETIME(ABunkerRound,DaySeconds);DOREPLIFETIME(ABunkerRound,Phase);DOREPLIFETIME(ABunkerRound,Deadline);DOREPLIFETIME(ABunkerRound,Gate);DOREPLIFETIME(ABunkerRound,ReleaseDeadline);DOREPLIFETIME(ABunkerRound,bRecoveryOpen);}
bool ABunkerRound::Start(ABunkerPlayerController* PC)
{
 auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
 if(!HasAuthority()||!PC||!PC->IsLocalController()||!GM||!GM->bPersistenceReady||GM->bPersistenceBlocked||!PS||!PS->Rules||!Gate||Phase!=0){UE_LOG(LogTemp,Display,TEXT("C13_ROUND_START_REJECT"));return false;}
 for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(!It->bSessionReady||It->Health<=0)return false;
 for(TActorIterator<ABunkerPlayerController> It(GetWorld());It;++It)if(It->GetPawn())
 {const FVector P=It->GetPawn()->GetActorLocation();if(P.Z<350||P.X<550||P.X>4550||P.Y<-600||P.Y>2400){PC->ClientNotice(TEXT("Reúna os participantes no supermercado antes de iniciar."));return false;}}
 if(!FMath::IsFinite(PS->Rules->CollectionSeconds))return false;
 float Duration=FMath::Clamp(PS->Rules->CollectionSeconds,60.f,120.f);
#if !UE_BUILD_SHIPPING
 if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest")))Duration=35;
#endif
 Phase=1;Deadline=ServerNow()+Duration;LastRemaining=Duration;Alerts=0;Gate->bOpen=true;Gate->ForceNetUpdate();
 UE_LOG(LogTemp,Display,TEXT("C13_ROUND_STARTED duration=%.0f"),Duration);Alert(0);Commit();return true;
}
void ABunkerRound::Commit(){ForceNetUpdate();if(auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>())GM->SaveCheckpoint();}
bool ABunkerRound::Accessible(ABunkerPlayerController* PC) const{return AccessibleDoor(PC,Gate);}
bool ABunkerRound::AccessibleDoor(ABunkerPlayerController* PC,ABunkerDoor* Door) const
{
 auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;if(!Door||!PS||!PS->bSessionReady||PS->Health<=0||PS->RestingBed||!PC->GetPawn())return false;
 auto* C=Cast<ACharacter>(PC->GetPawn());if(!C)return false;FMinimalViewInfo V;C->CalcCamera(0,V);const FVector Eye=V.Location;const FRotator Rot=PC->GetControlRotation();FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(RoundCrank),false,PC->GetPawn());
 return GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+Rot.Vector()*350,ECC_Visibility,Q)&&Hit.GetActor()==Door;
}
bool ABunkerRound::Operate(ABunkerPlayerController* PC)
{
 if(!HasAuthority()||!Accessible(PC))return false;
 if(Phase<2)return Gate->TryToggle();
 if(Phase==2){PC->ClientNotice(TEXT("Fechamento em curso. Afaste-se da folha; a porta não esmaga jogadores."));return false;}
 if(!AirlockAllows(PC,Gate))return false;
 if(bAirlockEnabled&&Gate->bOpen)
 {
  Gate->bRoundLocked=false;const bool OK=Gate->TryToggle();Gate->bRoundLocked=true;
  if(OK){bRecoveryOpen=false;ResetAirlock();Commit();}return OK;
 }
 const bool Inside=PC->GetPawn()->GetActorLocation().Y<Gate->GetActorLocation().Y-40;
 if(Inside){Gate->bRoundLocked=false;const bool OK=Gate->TryToggle();Gate->bRoundLocked=true;if(OK){bRecoveryOpen=Gate->bOpen;ResetAirlock();UE_LOG(LogTemp,Display,TEXT("C13_ROUND_INSIDE_OPEN open=%d"),Gate->bOpen);Commit();}return OK;}
 if(Gate->bOpen)return false;
 if(Cranking.IsValid()){PC->ClientNotice(TEXT("Outra pessoa já está usando a liberação."));return false;}
 auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if(!PS->Rules||!FMath::IsFinite(PS->Rules->EmergencyReleaseEnergy)||!FMath::IsFinite(PS->Rules->EmergencyReleaseSeconds))return false;
 // Exhaustion makes the fallback slower; it must never lock a solo survivor out.
 const float Cost=FMath::Clamp(PS->Rules->EmergencyReleaseEnergy,0.f,100.f);
 const float Penalty=PS->Energy<Cost?FMath::Clamp(PS->Rules->TiredActionInterval/FMath::Max(.01f,PS->Rules->ActionInterval),1.f,5.f):1.f;
 Cranking=PC;ReleaseDeadline=ServerNow()+FMath::Clamp(PS->Rules->EmergencyReleaseSeconds,3.f,60.f)*Penalty;ForceNetUpdate();
 PC->ClientNotice(TEXT("Mantenha E pressionado e olhe para a porta para operar a liberação manual."));UE_LOG(LogTemp,Display,TEXT("C13_ROUND_CRANK_STARTED"));return true;
}
void ABunkerRound::Cancel(ABunkerPlayerController* PC)
{if(HasAuthority()&&Cranking.Get()==PC){Cranking.Reset();ReleaseDeadline=0;ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_ROUND_CRANK_CANCEL"));}}
void ABunkerRound::Tick(float DT)
{
 Super::Tick(DT);if(!HasAuthority()||!Gate)return;
 auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();
 if(!GM||!GM->bPersistenceReady||GM->bPersistenceBlocked)return;
 // The shared clock starts only in shelter, never during preparation or loading.
 if(Phase==3&&ShelterAnchor<0)
 {
  if(ShelterElapsed==0)for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(It->Rules)
  {DaySeconds=FMath::IsFinite(It->Rules->DaySeconds)?FMath::Clamp(It->Rules->DaySeconds,30.f,3600.f):240.f;break;}
#if !UE_BUILD_SHIPPING
  if(FParse::Param(FCommandLine::Get(),TEXT("C13RoundTest"))&&FParse::Param(FCommandLine::Get(),TEXT("C13ClockFast")))DaySeconds=8;
#endif
  ShelterAnchor=ServerNow();ForceNetUpdate();
  UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_STARTED elapsed=%.3f day_seconds=%.1f"),ShelterElapsed,DaySeconds);
 }

 if(bAirlockEnabled)
 {
  if(Phase!=3||!InnerGate||InnerGate->bOpen||Gate->bOpen)ResetAirlock();
  // A power loss restarts a running pump cycle as a slower manual procedure.
  if(AirlockTarget&&ServerNow()<AirlockDeadline)
  {
   auto* Infra=ABunkerInfrastructure::Find(GetWorld());
   if(AirlockDeadline>0&&Infra&&!Infra->ServicesPowered()&&!bAirlockManual)
   {bAirlockManual=true;AirlockDeadline=ServerNow()+AirlockManualDuration;ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_MANUAL_FALLBACK"));}
  }
 }
 Gate->bRoundLocked=Phase>=2;
 if(Phase==1)
 {
  const float R=Remaining();int I=0;for(float Limit:{30.f,15.f,5.f}){if(!(Alerts&(1<<I))&&LastRemaining>Limit&&R<=Limit){Alerts|=1<<I;Alert(int(Limit));}I++;}LastRemaining=R;
  if(R<=0){Phase=2;Gate->bRoundLocked=true;Gate->bOpen=false;Gate->PlayFoley(false);Gate->ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_ROUND_CLOSING"));Commit();}
 }
 if(Phase==2&&FMath::Abs(Gate->CurrentAngle)<.5f){Phase=3;UE_LOG(LogTemp,Display,TEXT("C13_ROUND_SHELTER"));Alert(-1);Commit();}
 if(Cranking.IsValid())
 {
  auto* PC=Cranking.Get();if(!Accessible(PC)||Phase!=3||Gate->bOpen||(bAirlockEnabled&&(!InnerGate||InnerGate->bOpen||FMath::Abs(InnerGate->CurrentAngle)>.5f))){Cancel(PC);return;}
  if(ServerNow()>=ReleaseDeadline)
  {
   auto* PS=PC->GetPlayerState<ABunkerPlayerState>();const float Cost=FMath::Clamp(PS->Rules->EmergencyReleaseEnergy,0.f,100.f);
   Gate->bRoundLocked=false;const bool OK=Gate->TryToggle();Gate->bRoundLocked=true;
   if(OK){PS->Energy=FMath::Max(0.f,PS->Energy-Cost);PS->ForceNetUpdate();bRecoveryOpen=true;ResetAirlock();Cancel(PC);UE_LOG(LogTemp,Display,TEXT("C13_ROUND_RECOVERY_OPEN energy=%.1f"),PS->Energy);Commit();}
  }
 }
 else if(ReleaseDeadline>0){ReleaseDeadline=0;ForceNetUpdate();}
}
void ABunkerRound::Store(UBunkerSaveGame* S)const{S->bRoundMode=true;S->RoundPhase=Phase;S->RoundRemaining=Phase==1?Remaining():0;S->bRoundRecoveryOpen=bRecoveryOpen;S->ShelterSeconds=ShelterSeconds();S->ShelterDaySeconds=DaySeconds;UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_SAVED elapsed=%.3f phase=%d day_seconds=%.1f"),S->ShelterSeconds,Phase,DaySeconds);}
void ABunkerRound::Restore(const UBunkerSaveGame* S)
{ResetAirlock();ShelterElapsed=S->ShelterSeconds;ShelterAnchor=-1;DaySeconds=S->ShelterDaySeconds;UE_LOG(LogTemp,Display,TEXT("C13_CLOCK_RESTORED elapsed=%.3f day_seconds=%.1f"),ShelterElapsed,DaySeconds);Phase=S->RoundPhase;Deadline=ServerNow()+S->RoundRemaining;LastRemaining=S->RoundRemaining;bRecoveryOpen=S->bRoundRecoveryOpen;Cranking.Reset();ReleaseDeadline=0;if(Gate)Gate->bRoundLocked=Phase>=2;ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_ROUND_RESTORED phase=%d remaining=%.2f"),Phase,Remaining());}
void ABunkerRound::Alert_Implementation(int32 Seconds)
{
 UE_LOG(LogTemp,Display,TEXT("C13_ROUND_ALERT seconds=%d"),Seconds);
 auto* Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/Bunker/Round/Audio/S_CollectionAlert.S_CollectionAlert"));if(Sound)UGameplayStatics::PlaySoundAtLocation(this,Sound,FVector(2550,200,450),.7f,Seconds==5?1.3f:1.f);
}

void ABunkerRound::ResetAirlock()
{if(AirlockTarget||AirlockDeadline){AirlockTarget=0;AirlockDeadline=0;ForceNetUpdate();}}
FString ABunkerRound::AirlockStatus() const
{
 if(!bAirlockEnabled||Phase!=3)return FString();
 if(!InnerGate||!Gate)return TEXT("ANTECÂMARA — falha de identificação das portas");
 if(InnerGate->bOpen||Gate->bOpen||FMath::Abs(InnerGate->CurrentAngle)>.5f||FMath::Abs(Gate->CurrentAngle)>.5f)return TEXT("ANTECÂMARA — feche as duas portas antes de equalizar");
 if(!AirlockTarget)return TEXT("ANTECÂMARA — E na porta de destino inicia a equalização");
 if(ServerNow()<AirlockDeadline)return FString::Printf(TEXT("ANTECÂMARA — %s: %.0f s"),bAirlockManual?TEXT("equalização manual"):TEXT("equalização"),AirlockDeadline-ServerNow());
 return TEXT("ANTECÂMARA — pressão pronta; E abre a porta escolhida");
}
bool ABunkerRound::AirlockAllows(ABunkerPlayerController* PC,ABunkerDoor* Door)
{
 if(!bAirlockEnabled||Phase!=3)return true;
 auto* Other=Door==Gate?InnerGate.Get():Gate.Get();
 if(!Other)return false;
 // Closing is always allowed, including legacy checkpoints with both leaves open.
 if(Door->bOpen)return true;
 if(Cranking.IsValid()&&Door==InnerGate){PC->ClientNotice(TEXT("A liberação externa está em uso; aguarde."));return false;}
 // A legacy checkpoint can leave the inner leaf open with a solo survivor outside.
 // The external mechanical release may close it safely, never move it through a pawn.
 if(Door==Gate&&Other->bOpen&&PC->GetPawn()->GetActorLocation().Y>Gate->GetActorLocation().Y+40)
 {Other->TryToggle();PC->ClientNotice(TEXT("Liberação solicita fechamento interno. Aguarde e pressione E novamente."));UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_RECOVERY_CLOSE_REQUEST"));return false;}
 if(Other->bOpen||FMath::Abs(Other->CurrentAngle)>.5f||FMath::Abs(Door->CurrentAngle)>.5f)
 {PC->ClientNotice(TEXT("Feche a outra porta e aguarde o fechamento físico."));UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_REJECT other_open"));return false;}
 const uint8 Target=Door==InnerGate?1:2;
 if(AirlockTarget&&AirlockTarget!=Target&&ServerNow()>=AirlockDeadline)ResetAirlock();
 if(AirlockTarget&&AirlockTarget!=Target){UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_REJECT other_cycle"));PC->ClientNotice(TEXT("Aguarde e use a porta escolhida para este ciclo."));return false;}
 if(!AirlockTarget)
 {
  auto* PS=PC->GetPlayerState<ABunkerPlayerState>();if(!PS||!PS->Rules)return false;
  const float Fast=PS->Rules->AirlockPoweredSeconds,Slow=PS->Rules->AirlockManualSeconds;
  if(!FMath::IsFinite(Fast)||!FMath::IsFinite(Slow)||Fast<1||Slow<Fast||Slow>60)return false;
  auto* Infra=ABunkerInfrastructure::Find(GetWorld());bAirlockManual=!Infra||!Infra->ServicesPowered();AirlockManualDuration=Slow;
  AirlockTarget=Target;AirlockDeadline=ServerNow()+(bAirlockManual?Slow:Fast);ForceNetUpdate();
  PC->ClientNotice(TEXT("Equalizando. Aguarde e pressione E novamente na mesma porta."));
  UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_CYCLE target=%d manual=%d seconds=%.1f"),Target,bAirlockManual,AirlockDeadline-ServerNow());return false;
 }
 if(ServerNow()<AirlockDeadline){PC->ClientNotice(TEXT("Equalização em andamento."));return false;}
 return true;
}
bool ABunkerRound::OperateInner(ABunkerPlayerController* PC)
{
 if(!HasAuthority()||!AccessibleDoor(PC,InnerGate)||!AirlockAllows(PC,InnerGate))return false;
 if(!InnerGate->TryToggle())return false;
 ResetAirlock();Commit();UE_LOG(LogTemp,Display,TEXT("C13_AIRLOCK_INNER open=%d"),InnerGate->bOpen);return true;
}
