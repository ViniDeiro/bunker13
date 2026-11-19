#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BedroomRestTestClock.generated.h"
UCLASS()
class CONDOMINIO13_API ABedroomRestTestClock : public AActor
{
 GENERATED_BODY()
public:
 ABedroomRestTestClock();
 UPROPERTY(Replicated) float Epoch=-1;
 void Ready(class APlayerController* PC);
 virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
private:
 TSet<TWeakObjectPtr<APlayerController>> Participants;
};
