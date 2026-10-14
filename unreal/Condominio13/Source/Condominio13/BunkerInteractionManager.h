#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerInteractionManager.generated.h"

class ABunkerInteractable;

UCLASS()
class CONDOMINIO13_API ABunkerInteractionManager : public AActor
{
    GENERATED_BODY()

public:
    ABunkerInteractionManager();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    TWeakObjectPtr<ABunkerInteractable> Focused;
    TWeakObjectPtr<ABunkerInteractable> RestingBed;
    TArray<FString> Inventory;
    int32 DartThrows = 0;
    int32 DartScore = 0;
    bool bGeneratorOn = true;

    void Interact();
    void LeaveBed();
    void Show(const FString& Message, FColor Color = FColor(230, 210, 150), float Seconds = 2.5f) const;
};
