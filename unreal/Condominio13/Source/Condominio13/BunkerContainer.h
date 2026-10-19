#pragma once
#include "BunkerInteractable.h"
#include "BunkerInventoryTypes.h"
#include "BunkerContainer.generated.h"
UCLASS()
class CONDOMINIO13_API ABunkerContainer : public ABunkerInteractable
{
    GENERATED_BODY()
public:
    ABunkerContainer();
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Storage") int32 MaxSlots=24;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Storage") float MaxWeightKg=60;
    // Server only. Contents are sent as owner-RPC snapshots to authorized viewers.
    UPROPERTY() TArray<FBunkerInventoryEntry> Contents;
    int32 Revision=0;
    void RefreshViewers();
};
