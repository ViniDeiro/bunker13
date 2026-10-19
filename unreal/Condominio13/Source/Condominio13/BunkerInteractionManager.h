#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BunkerInteractionManager.generated.h"

// Compatibility shell for older saved maps. The owning player controller handles interactions.
UCLASS()
class CONDOMINIO13_API ABunkerInteractionManager : public AActor
{
    GENERATED_BODY()
public:
    ABunkerInteractionManager();
};
