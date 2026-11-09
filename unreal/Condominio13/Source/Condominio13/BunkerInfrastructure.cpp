#include "BunkerInfrastructure.h"
#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BunkerRound.h"
#include "BunkerSaveGame.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "Engine/PointLight.h"
#include "Engine/StaticMeshActor.h"
#include "Components/LightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/MeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/Character.h"
#include "Net/UnrealNetwork.h"
ABunkerInfrastructure::ABunkerInfrastructure(){bReplicates=true;bAlwaysRelevant=true;PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=.1f;SetNetUpdateFrequency(5);}
ABunkerInfrastructure* ABunkerInfrastructure::Find(UWorld* W){TActorIterator<ABunkerInfrastructure> It(W);return It?*It:nullptr;}
bool ABunkerInfrastructure::Extension(const ABunkerInteractable* A){return A&&A->WorldKey.StartsWith(TEXT("InfraV1_"));}
bool ABunkerInfrastructure::SupplyExtension(const ABunkerInteractable* A){return A&&A->WorldKey.StartsWith(TEXT("SupplyV1_"));}
void ABunkerInfrastructure::BeginPlay(){Super::BeginPlay();Rules=LoadObject<UBunkerSurvivalRules>(nullptr,TEXT("/Game/Bunker/Data/DA_SurvivalRules.DA_SurvivalRules"));if(HasAuthority())
 {if(Rules){State.Fuel=Rules->FuelInitialLiters;State.Condition=Rules->GeneratorInitialCondition;State.RawWater=Rules->RawWaterInitialLiters;State.CleanWater=Rules->CleanWaterInitialLiters;}BuildFixtures();}
 auto* Stand=GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(),FVector(1760,-1553,0),FRotator::ZeroRotator);
 if(Stand){Stand->GetStaticMeshComponent()->SetLightingChannels(true,true,true);Stand->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);Stand->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Infrastructure/Meshes/SM_Infra_ServiceStand.SM_Infra_ServiceStand")));}
 // Repair the existing entrance connection: market floor ends at Y=2400,
 // parking starts at Y=2500. The lower apron provides a supported 18.45 cm step.
 auto* Apron=GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(),FVector(2770,2450,285.05f),FRotator::ZeroRotator);
 if(Apron){auto* M=Apron->GetStaticMeshComponent();M->SetMobility(EComponentMobility::Movable);M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));M->SetWorldScale3D(FVector(12.4f,3.f,.18f));M->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Bunker/Materials/M_EXT_Asphalt.M_EXT_Asphalt")));M->SetLightingChannels(true,true,true);}
 // Open-plan styling classified meshes by root height; the parking root is
 // below 290 cm although it is outdoors. Restore its existing exterior channel.
 int ParkingFixed=0;
 for(TActorIterator<AActor> It(GetWorld());It;++It)
 {
  TArray<UMeshComponent*> Meshes;It->GetComponents(Meshes);
  for(auto* M:Meshes)if(FVector::DistSquared(M->GetComponentLocation(),FVector(2550,3900,285))<25)
   if(auto* Mat=M->GetMaterial(0))if(Mat->GetName()==TEXT("M_EXT_Asphalt"))
   {UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_PARKING_LIGHTING old=%d%d%d new=010"),M->LightingChannels.bChannel0,M->LightingChannels.bChannel1,M->LightingChannels.bChannel2);M->SetLightingChannels(false,true,false);ParkingFixed++;}
 }
 UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_PARKING_FIXED count=%d"),ParkingFixed);
 CapturePowerConsumers();ApplyPower();}
void ABunkerInfrastructure::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ABunkerInfrastructure,TestEpoch);DOREPLIFETIME(ABunkerInfrastructure,State);DOREPLIFETIME(ABunkerInfrastructure,Task);DOREPLIFETIME(ABunkerInfrastructure,TaskDeadline);}
bool ABunkerInfrastructure::Powered()const{auto* R=ABunkerRound::Find(GetWorld());return (R&&R->Phase<3)||(State.Running&&State.Fuel>0&&State.Condition>0);}
bool ABunkerInfrastructure::Valid(const FBunkerInfrastructureState& S)
{return FMath::IsFinite(S.Fuel)&&S.Fuel>=0&&S.Fuel<=100&&FMath::IsFinite(S.Condition)&&S.Condition>=0&&S.Condition<=100&&FMath::IsFinite(S.RawWater)&&S.RawWater>=0&&S.RawWater<=1000&&FMath::IsFinite(S.CleanWater)&&S.CleanWater>=0&&S.CleanWater<=1000&&FMath::IsFinite(S.Filter)&&S.Filter>=0&&S.Filter<=100;}
FString ABunkerInfrastructure::Status()const{return FString::Printf(TEXT("Gerador %s | %.2f L | condição %.0f%%"),Powered()?TEXT("energizado"):TEXT("sem energia"),State.Fuel,State.Condition);}
FString ABunkerInfrastructure::WaterStatus()const{return FString::Printf(TEXT("Água bruta %.2f L | tratada %.2f L | filtro %.0f%% | %s"),State.RawWater,State.CleanWater,State.Filter,Filtering()?TEXT("filtrando"):TEXT("parado"));}
bool ABunkerInfrastructure::Filtering()const{return ServicesPowered()&&State.Pump&&State.RawWater>0&&State.CleanWater< (Rules?Rules->CleanWaterCapacityLiters:12.f)&&State.Filter>0&&Task!=6;}
void ABunkerInfrastructure::OnRep_State(){ApplyPower();}
void ABunkerInfrastructure::Commit(){ForceNetUpdate();OnRep_State();if(auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>())GM->SaveCheckpoint();}
bool ABunkerInfrastructure::SettingsValid()const
{
 if(!Rules)return false;
 for(float V:{Rules->FuelCapacityLiters,Rules->FuelCanLiters,Rules->FuelLitersPerMinute,Rules->GeneratorWearPerMinute,Rules->GeneratorRepairGain,Rules->InfrastructureWorkSeconds,Rules->CleanWaterCapacityLiters,Rules->FilterLitersPerMinute,Rules->FilterWearPerLiter,Rules->DrinkLiters,Rules->HydrationPerLiter,Rules->RawWaterCapacityLiters})if(!FMath::IsFinite(V)||V<=0||V>1000)return false;
 return Rules->FuelCapacityLiters<=100&&Rules->FuelCanLiters<=Rules->FuelCapacityLiters&&Rules->GeneratorRepairGain<=100&&Rules->InfrastructureWorkSeconds<=60;
}
bool ABunkerInfrastructure::Accessible(ABunkerPlayerController* PC,ABunkerInteractable* Target)const
{
 auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;auto* C=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
 if(!PS||!PS->bSessionReady||!PS->Rules||PS->Health<=0||PS->RestingBed||!C||!Target)return false;
 FMinimalViewInfo V;C->CalcCamera(0,V);FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(InfraUse),false,C);
 return GetWorld()->LineTraceSingleByChannel(H,V.Location,V.Location+PC->GetControlRotation().Vector()*350,ECC_Visibility,Q)&&H.GetActor()==Target;
}
void ABunkerInfrastructure::CancelTask(){Task=0;TaskDeadline=0;Worker.Reset();TaskTerminal=nullptr;ReservedItem.Invalidate();ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CANCEL"));}
bool ABunkerInfrastructure::Operate(ABunkerPlayerController* PC,ABunkerInteractable* Target,uint8 Action)
{
 if(!HasAuthority()||!Accessible(PC,Target))return false;
 if(Action==10)Action=0;
 auto* PS=PC->GetPlayerState<ABunkerPlayerState>();Rules=PS->Rules;if(!SettingsValid())return false;
 if(Action==8){PC->ClientNotice(WaterStatus());return true;}
 if(Action==9){PC->ClientNotice(Status());return true;}
 auto* R=ABunkerRound::Find(GetWorld());if(!R||R->Phase!=3){PC->ClientNotice(TEXT("Manutenção disponível após o fechamento do abrigo."));return false;}
 if(Action==0)
 {if(State.Running){State.Running=false;}else if(State.Fuel>0&&State.Condition>0){State.Running=true;}else{PC->ClientNotice(TEXT("Reponha combustível ou faça manutenção antes de ligar."));return false;}UE_LOG(LogTemp,Display,TEXT("C13_INFRA_TOGGLE running=%d"),State.Running);Commit();return true;}
 if(Action==7)
 {
  const float L=FMath::Min3(Rules->DrinkLiters,State.CleanWater,(100.f-PS->Water)/FMath::Max(.01f,Rules->HydrationPerLiter));
  if(L<=.00001f){PC->ClientNotice(State.CleanWater<=0?TEXT("Reservatório tratado vazio."):TEXT("Você já está hidratado."));return false;}
  State.CleanWater=FMath::Max(0.f,State.CleanWater-L);PS->Water=FMath::Min(100.f,PS->Water+L*Rules->HydrationPerLiter);PS->ForceNetUpdate();PC->ClientNotice(FString::Printf(TEXT("Bebeu %.2f L de água tratada."),L));UE_LOG(LogTemp,Display,TEXT("C13_INFRA_DRINK liters=%.3f clean=%.3f hydration=%.3f"),L,State.CleanWater,PS->Water);Commit();return true;
 }
 if(Action==5){State.Pump=!State.Pump;Commit();return true;}
 if(Action==3||Action==4){if(Action==3)State.Lights=!State.Lights;else State.Services=!State.Services;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CIRCUIT action=%d lights=%d services=%d"),Action,State.Lights,State.Services);Commit();return true;}
 if(Action!=1&&Action!=2&&Action!=6)return false;
 if(Task){if(Worker.Get()==PC)CancelTask();else PC->ClientNotice(TEXT("Equipamento em manutenção por outra pessoa."));return false;}
 if(Action<=2&&State.Running){PC->ClientNotice(TEXT("Desligue o gerador antes de abastecer ou reparar."));return false;}
 if(Action==1&&State.Fuel+Rules->FuelCanLiters>Rules->FuelCapacityLiters+.001f){PC->ClientNotice(TEXT("Tanque sem espaço para o galão inteiro."));return false;}
 if(Action==2&&State.Condition>=100){PC->ClientNotice(TEXT("Gerador não precisa de reparo."));return false;}
 if(Action==6&&(State.Pump||State.Filter>=100)){PC->ClientNotice(TEXT("Desligue a bomba e confira se o filtro precisa de troca."));return false;}
 const FName Type=Action==1?TEXT("FuelCan"):Action==2?TEXT("RepairParts"):TEXT("FilterCartridge");
 const auto* E=PS->Inventory.FindByPredicate([Type](const auto& I){return I.ItemType==Type;});if(!E){PC->ClientNotice(Action==1?TEXT("Pegue um galão de combustível na mochila."):Action==2?TEXT("Pegue peças de manutenção na mochila."):TEXT("Pegue um cartucho de filtro na mochila."));return false;}
 ReservedItem=E->Id;Task=Action;Worker=PC;TaskTerminal=Target;TaskDeadline=GetWorld()->GetTimeSeconds()+Rules->InfrastructureWorkSeconds;ForceNetUpdate();PC->ClientNotice(TEXT("Trabalhando: mantenha o olhar no equipamento. Afastar cancela sem gastar o item; E cancela."));return true;
}
void ABunkerInfrastructure::Tick(float DT)
{
 Super::Tick(DT);ApplyPower();if(!HasAuthority())return;auto* GM=GetWorld()->GetAuthGameMode<ABunkerGameMode>();if(!GM||!GM->bPersistenceReady||GM->bPersistenceBlocked)return;
 if(!Rules)for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)if(It->Rules){Rules=It->Rules;break;}
 auto* R=ABunkerRound::Find(GetWorld());if(!Rules||!R)return;
 if(!SettingsValid()||!Valid(State)||State.Fuel>Rules->FuelCapacityLiters+.001f||State.RawWater>Rules->RawWaterCapacityLiters+.001f||State.CleanWater>Rules->CleanWaterCapacityLiters+.001f){GM->bPersistenceBlocked=true;UE_LOG(LogTemp,Error,TEXT("C13_INFRA_INVALID_STATE"));return;}
 if(R->Phase==3&&Filtering())
 {
  const float L=FMath::Min(FMath::Min(State.RawWater,Rules->CleanWaterCapacityLiters-State.CleanWater),FMath::Min(Rules->FilterLitersPerMinute*DT/60.f,State.Filter/FMath::Max(.001f,Rules->FilterWearPerLiter)));
  State.RawWater=FMath::Max(0.f,State.RawWater-L);State.CleanWater+=L;State.Filter=FMath::Max(0.f,State.Filter-L*Rules->FilterWearPerLiter);
 }
 if(R->Phase==3&&State.Running)
 {
  State.Fuel=FMath::Max(0.f,State.Fuel-Rules->FuelLitersPerMinute*(.4f+(State.Lights?.35f:0.f)+(State.Services?.25f:0.f))*DT/60.f);State.Condition=FMath::Max(0.f,State.Condition-Rules->GeneratorWearPerMinute*DT/60.f);
  if(State.Fuel<=0||State.Condition<=0){State.Running=false;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_STOP fuel=%.3f condition=%.3f"),State.Fuel,State.Condition);Commit();}
 }
 if(Task)
 {
  auto* PC=Worker.Get();auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;const int I=PS?PS->Inventory.IndexOfByPredicate([this](const auto& E){return E.Id==ReservedItem;}):INDEX_NONE;
  if(!PS||I==INDEX_NONE||(I!=INDEX_NONE&&PS->Inventory[I].ItemType!=(Task==1?FName(TEXT("FuelCan")):Task==2?FName(TEXT("RepairParts")):FName(TEXT("FilterCartridge"))))||!Accessible(PC,TaskTerminal)||(Task<=2&&State.Running)||(Task==6&&State.Pump)){CancelTask();return;}
  if(GetWorld()->GetTimeSeconds()>=TaskDeadline)
  {
   if(Task==1&&State.Fuel+Rules->FuelCanLiters>Rules->FuelCapacityLiters+.001f){CancelTask();return;}
   const auto E=PS->Inventory[I];if(Task==1)State.Fuel+=Rules->FuelCanLiters;else if(Task==2)State.Condition=FMath::Min(100.f,State.Condition+Rules->GeneratorRepairGain);else State.Filter=100;
   PS->Inventory.RemoveAt(I);PS->ForceNetUpdate();PC->ClientPlayItemAction(E,false);UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CONSUMED action=%d id=%s fuel=%.3f condition=%.3f"),Task,*E.Id.ToString(EGuidFormats::Digits),State.Fuel,State.Condition);CancelTask();Commit();
  }
 }
}
void ABunkerInfrastructure::Store(UBunkerSaveGame* S)const{S->bInfrastructure=true;S->bExternalSupplies=true;S->Infrastructure=State;UE_LOG(LogTemp,Display,TEXT("C13_INFRA_SAVED fuel=%.3f condition=%.3f raw=%.3f clean=%.3f filter=%.3f running=%d lights=%d services=%d pump=%d"),State.Fuel,State.Condition,State.RawWater,State.CleanWater,State.Filter,State.Running,State.Lights,State.Services,State.Pump);}
void ABunkerInfrastructure::Restore(const UBunkerSaveGame* S){if(S->bInfrastructure)State=S->Infrastructure;CancelTask();ForceNetUpdate();OnRep_State();UE_LOG(LogTemp,Display,TEXT("C13_INFRA_RESTORED legacy=%d fuel=%.3f condition=%.3f raw=%.3f clean=%.3f filter=%.3f running=%d lights=%d services=%d pump=%d"),!S->bInfrastructure,State.Fuel,State.Condition,State.RawWater,State.CleanWater,State.Filter,State.Running,State.Lights,State.Services,State.Pump);}
void ABunkerInfrastructure::BuildFixtures()
{
 auto Spawn=[this](const TCHAR* Key,FVector Pos,uint8 Action,const TCHAR* Name,const TCHAR* Mesh,const TCHAR* Type)
 {
  auto* A=GetWorld()->SpawnActor<ABunkerInteractable>(ABunkerInteractable::StaticClass(),Pos,FRotator::ZeroRotator);if(!A)return;
  A->WorldKey=FString(TEXT("InfraV1_"))+Key;A->InfraAction=Action;A->Interaction=Action?EBunkerInteraction::Panel:EBunkerInteraction::Pickup;A->DisplayName=FText::FromString(Name);A->ActionText=FText::FromString(Action?TEXT("operar"):TEXT("pegar"));A->ItemType=Type;A->PickupMesh=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Bunker/Infrastructure/Meshes/%s.%s"),Mesh,Mesh));A->PickupScale=FVector::OneVector;A->OnRep_Visual();A->Mesh->SetLightingChannels(true,true,true);A->ForceNetUpdate();Terminals.Add(A);
 };
 Spawn(TEXT("FuelPort"),FVector(1720,-1540,110),1,TEXT("Abastecer gerador (2 L)"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("RepairPort"),FVector(1760,-1540,110),2,TEXT("Reparar gerador"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("Status"),FVector(1800,-1540,110),9,TEXT("Estado da infraestrutura"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("GeneratorSwitch"),FVector(1720,-1540,145),10,TEXT("Ligar / desligar gerador"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("LightSwitch"),FVector(1760,-1540,145),3,TEXT("Circuito iluminação"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("ServiceSwitch"),FVector(1800,-1540,145),4,TEXT("Circuito serviços"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("WaterStation"),FVector(2050,-500,0),5,TEXT("Ligar / desligar bomba de filtragem"),TEXT("SM_Infra_WaterStation"),TEXT("Generic"));
 Spawn(TEXT("FilterPort"),FVector(2010,-480,72),6,TEXT("Trocar cartucho do filtro"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("DrinkPort"),FVector(2090,-480,60),7,TEXT("Beber água tratada"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("WaterStatus"),FVector(2010,-480,110),8,TEXT("Ler reservatórios"),TEXT("SM_Infra_Control"),TEXT("Generic"));
 Spawn(TEXT("Filter0"),FVector(2130,-500,0),0,TEXT("Cartucho de filtragem"),TEXT("SM_Infra_Filter"),TEXT("FilterCartridge"));
 Spawn(TEXT("Filter1"),FVector(2180,-500,0),0,TEXT("Cartucho de filtragem"),TEXT("SM_Infra_Filter"),TEXT("FilterCartridge"));
 Spawn(TEXT("Fuel0"),FVector(2130,-1700,0),0,TEXT("Galão de combustível - 2 L"),TEXT("SM_Infra_FuelCan"),TEXT("FuelCan"));
 Spawn(TEXT("Fuel1"),FVector(2130,-1740,0),0,TEXT("Galão de combustível - 2 L"),TEXT("SM_Infra_FuelCan"),TEXT("FuelCan"));
 Spawn(TEXT("Parts0"),FVector(2130,-1780,0),0,TEXT("Peças de manutenção"),TEXT("SM_Infra_RepairParts"),TEXT("RepairParts"));
 Spawn(TEXT("Parts1"),FVector(2130,-1810,0),0,TEXT("Peças de manutenção"),TEXT("SM_Infra_RepairParts"),TEXT("RepairParts"));
 // One finite cache in the existing parking area. These are keyed world objects,
 // not rewards generated when someone departs or reloads.
 const TCHAR* Types[]={TEXT("FuelCan"),TEXT("FuelCan"),TEXT("RepairParts"),TEXT("RepairParts"),TEXT("FilterCartridge"),TEXT("FilterCartridge")};
 const TCHAR* Meshes[]={TEXT("SM_Infra_FuelCan"),TEXT("SM_Infra_FuelCan"),TEXT("SM_Infra_RepairParts"),TEXT("SM_Infra_RepairParts"),TEXT("SM_Infra_Filter"),TEXT("SM_Infra_Filter")};
 const TCHAR* Names[]={TEXT("Galão de combustível - 2 L"),TEXT("Galão de combustível - 2 L"),TEXT("Peças de manutenção"),TEXT("Peças de manutenção"),TEXT("Cartucho de filtragem"),TEXT("Cartucho de filtragem")};
 for(int N=0;N<6;N++)
 {
  const FString Key=FString::Printf(TEXT("SupplyV1_%d"),N);
  const FVector Pos(2800+N*65,3200,294.05f);
  auto* A=GetWorld()->SpawnActor<ABunkerInteractable>(ABunkerInteractable::StaticClass(),Pos,FRotator::ZeroRotator);
  if(!A){UE_LOG(LogTemp,Error,TEXT("C13_SUPPLY_SPAWN_FAILED"));continue;}
  A->WorldKey=Key;A->Interaction=EBunkerInteraction::Pickup;A->DisplayName=FText::FromString(Names[N]);A->ActionText=FText::FromString(TEXT("pegar"));A->ItemType=Types[N];
  A->PickupMesh=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Bunker/Infrastructure/Meshes/%s.%s"),Meshes[N],Meshes[N]));A->PickupScale=FVector::OneVector;A->OnRep_Visual();A->Mesh->SetLightingChannels(true,true,true);A->ForceNetUpdate();
  UE_LOG(LogTemp,Display,TEXT("C13_SUPPLY_SPAWN key=%s id=%s"),*Key,*A->ItemId.ToString(EGuidFormats::Digits));
 }

}

void ABunkerInfrastructure::CapturePowerConsumers()
{
 for(TActorIterator<AActor> It(GetWorld());It;++It)
 {
  TArray<ULightComponent*> Components;It->GetComponents(Components);
  for(auto* L:Components){const auto P=L->GetComponentLocation();if(P.Z>305||(P.X>2400&&P.Y>0))continue;ControlledLights.Add(L);OriginalIntensities.Add(L->Intensity);}
  TArray<UMeshComponent*> Meshes;It->GetComponents(Meshes);
  for(auto* M:Meshes)if(M->GetComponentLocation().Z<305)for(int Slot=0;Slot<M->GetNumMaterials();Slot++)if(auto* Mat=M->GetMaterial(Slot))if(Mat->GetName()==TEXT("M_Ref_Light"))
  {EmissiveMeshes.Add(M);EmissiveSlots.Add(Slot);OriginalMaterials.Add(Mat);}
 }
 // Local visual actors on every instance. Never saved or replicated as resources.
 for(FVector P:{FVector(600,-700,220),FVector(1200,-1000,220),FVector(1900,-1500,220),FVector(1900,-1650,220),FVector(2050,-500,220)})
 {auto* L=GetWorld()->SpawnActor<APointLight>(APointLight::StaticClass(),P,FRotator::ZeroRotator);if(!L)continue;auto* C=Cast<UPointLightComponent>(L->GetLightComponent());C->SetMobility(EComponentMobility::Movable);C->IntensityUnits=ELightUnits::Lumens;C->LightingChannels.bChannel0=true;C->LightingChannels.bChannel1=true;C->LightingChannels.bChannel2=true;C->SetIntensity(0);EmergencyLights.Add(C);C->SetLightColor(FLinearColor(1.f,.32f,.07f));C->SetAttenuationRadius(550);C->SetCastShadows(false);EmergencyCount++;
 auto* Body=GetWorld()->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(),P+FVector(0,0,25),FRotator::ZeroRotator);
 if(Body){auto* M=Body->GetStaticMeshComponent();M->SetLightingChannels(true,true,true);M->SetMobility(EComponentMobility::Movable);M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Infrastructure/Meshes/SM_Infra_Emergency.SM_Infra_Emergency")));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 }
 AppliedPower=-1;
 UE_LOG(LogTemp,Display,TEXT("C13_INFRA_CONSUMERS lights=%d emergency=%d"),ControlledLights.Num(),EmergencyCount);
}
void ABunkerInfrastructure::ApplyPower()
{
 const int Mask=(LightingPowered()?1:0)|(ServicesPowered()?2:0);if(Mask==AppliedPower)return;AppliedPower=Mask;
 for(auto L:EmergencyLights)if(L.IsValid())L->SetIntensity((Mask&1)?0.f:220.f);
 for(int I=0;I<ControlledLights.Num();I++)if(auto* L=ControlledLights[I].Get())L->SetIntensity((Mask&1)?OriginalIntensities[I]:0.f);
 auto* Off=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Bunker/ReferenceRoom/Materials/M_Ref_Rubber.M_Ref_Rubber"));
 for(int I=0;I<EmissiveMeshes.Num();I++)if(auto* M=EmissiveMeshes[I].Get())M->SetMaterial(EmissiveSlots[I],(Mask&1)?OriginalMaterials[I].Get():Off);
 UE_LOG(LogTemp,Display,TEXT("C13_INFRA_POWER light=%d services=%d"),bool(Mask&1),bool(Mask&2));
}
