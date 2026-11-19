#include "BedroomRestTestClock.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameStateBase.h"
#include "Net/UnrealNetwork.h"
ABedroomRestTestClock::ABedroomRestTestClock(){bReplicates=true;bAlwaysRelevant=true;SetReplicateMovement(false);}
void ABedroomRestTestClock::Ready(APlayerController* PC)
{
 if(!HasAuthority()||!PC||Epoch>=0)return;
 Participants.Add(PC);
 if(Participants.Num()==2){Epoch=GetWorld()->GetGameState()->GetServerWorldTimeSeconds()+3;ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("C13_REST_BARRIER players=2 epoch=%.3f"),Epoch);}
}
void ABedroomRestTestClock::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ABedroomRestTestClock,Epoch);}
