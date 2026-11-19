#include "BedroomRestPose.h"
#include "BunkerInteractable.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameStateBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimInstance.h"
#include "EngineUtils.h"
#include "Net/UnrealNetwork.h"

namespace {
constexpr float Duration=1.15f;
float Clock(UWorld* W){return W->GetGameState()?W->GetGameState()->GetServerWorldTimeSeconds():W->GetTimeSeconds();}
float Ease(float V){V=FMath::Clamp(V,0.f,1.f);return V*V*(3.f-2.f*V);}
}
ABedroomRestPose::ABedroomRestPose()
{bReplicates=true;bAlwaysRelevant=true;SetReplicateMovement(false);PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostPhysics;SetNetUpdateFrequency(20);}
void ABedroomRestPose::StartFor(ACharacter* C,ABunkerInteractable* B,const FTransform& Standing)
{
 if(!C||!C->HasAuthority()||!B||!C->GetWorld()->GetMapName().Contains(TEXT("Bedroom_Study_Rest")))return;
 for(TActorIterator<ABedroomRestPose> I(C->GetWorld());I;++I)if(I->Performer==C){if(I->LeaveAt<0)return;I->Destroy();}
 auto* A=C->GetWorld()->SpawnActor<ABedroomRestPose>();if(!A)return;
 A->Performer=C;A->Bed=B;A->StandingWorld=Standing;A->DefaultRelative=C->GetMesh()->GetRelativeTransform();A->StartedAt=Clock(C->GetWorld());A->ForceNetUpdate();
}
FTransform ABedroomRestPose::RestWorld() const
{return FTransform(Bed->GetActorQuat(),Bed->GetActorTransform().TransformPosition(FVector(0,88,72)),StandingWorld.GetScale3D());}
float ABedroomRestPose::PoseProgress() const
{
 if(LeaveAt>=0)return ReverseFrom*(1-Ease((Clock(GetWorld())-LeaveAt)/Duration));
 return Ease((Clock(GetWorld())-StartedAt)/Duration);
}
void ABedroomRestPose::LeaveFor(ACharacter* C,const FVector& Exit)
{
 if(!C||!C->HasAuthority())return;
 for(TActorIterator<ABedroomRestPose> I(C->GetWorld());I;++I)if(I->Performer==C&&I->LeaveAt<0)
 {
  I->ReverseFrom=I->PoseProgress();I->ExitStartWorld=C->GetMesh()->GetComponentTransform();
  I->ExitWorld=I->DefaultRelative*FTransform(C->GetActorQuat(),Exit,C->GetActorScale3D());I->LeaveAt=Clock(C->GetWorld());I->ForceNetUpdate();
 }
}
void ABedroomRestPose::Tick(float DT)
{
 Super::Tick(DT);
 if(HasAuthority()&&(!Performer||Performer->IsActorBeingDestroyed())){Destroy();return;}
 if(!Performer||!Bed||!Performer->GetMesh())return;
 auto* Mesh=Performer->GetMesh();
 if(!bInitialized)
 {
  Sequence=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Bunker/BedroomRest/A_Bedroom_Rest.A_Bedroom_Rest"));
  if(!Sequence)return;
  OriginalClass=Mesh->GetAnimClass();OriginalMode=uint8(Mesh->GetAnimationMode());
  Mesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);Mesh->SetAnimation(Sequence);Mesh->SetPlayRate(0);bInitialized=true;
 }
 FTransform World;
 if(LeaveAt>=0)World.Blend(ExitStartWorld,DefaultRelative*Performer->GetActorTransform(),Ease((Clock(GetWorld())-LeaveAt)/Duration));
 else World.Blend(StandingWorld,RestWorld(),Ease((Clock(GetWorld())-StartedAt)/Duration));
 if(!Mesh->GetComponentTransform().Equals(World,.001f))Mesh->SetWorldTransform(World);
 const float SampleTime=Sequence->GetPlayLength()*PoseProgress();
 // SetPosition does not evaluate bones. Evaluate only when the sampled pose changes.
 if(LastSampleTime<0 || !FMath::IsNearlyEqual(SampleTime,LastSampleTime,1.e-6f))
 {
  Mesh->SetPosition(SampleTime,false);Mesh->TickAnimation(0,false);Mesh->RefreshBoneTransforms();LastSampleTime=SampleTime;
 }
 if(HasAuthority()&&LeaveAt>=0&&Clock(GetWorld())-LeaveAt>Duration+.2f)Destroy();
}
void ABedroomRestPose::Restore()
{
 if(!bInitialized||!Performer||!Performer->GetMesh())return;
 auto* Mesh=Performer->GetMesh();Mesh->SetRelativeTransform(DefaultRelative);
 Mesh->SetAnimationMode(EAnimationMode::Type(OriginalMode));
 if(OriginalClass)Mesh->SetAnimInstanceClass(OriginalClass);
 bInitialized=false;
}
void ABedroomRestPose::EndPlay(const EEndPlayReason::Type Reason)
{Restore();Super::EndPlay(Reason);}
void ABedroomRestPose::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
 Super::GetLifetimeReplicatedProps(OutLifetimeProps);
 DOREPLIFETIME(ABedroomRestPose,Performer);DOREPLIFETIME(ABedroomRestPose,Bed);DOREPLIFETIME(ABedroomRestPose,StandingWorld);DOREPLIFETIME(ABedroomRestPose,DefaultRelative);
 DOREPLIFETIME(ABedroomRestPose,ExitStartWorld);DOREPLIFETIME(ABedroomRestPose,ExitWorld);DOREPLIFETIME(ABedroomRestPose,StartedAt);DOREPLIFETIME(ABedroomRestPose,LeaveAt);DOREPLIFETIME(ABedroomRestPose,ReverseFrom);
}
