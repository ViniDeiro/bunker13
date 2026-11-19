#include "BedroomRestCamera.h"
#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Pawn.h"

bool UBedroomRestCamera::ModifyCamera(float DT, FMinimalViewInfo& POV)
{
    if (!CameraOwner || !CameraOwner->PCOwner || !GetWorld() ||
        !GetWorld()->GetMapName().Contains(TEXT("Bedroom_Study"))) return false;
    const auto* PS = CameraOwner->PCOwner->GetPlayerState<ABunkerPlayerState>();
    const bool Rest = PS && PS->RestingBed;
    if (!bInitialized) { Previous = POV; bInitialized = true; }
    if (Rest != bResting)
    {
        From = Previous;
        Elapsed = 0;
        bResting = Rest;
        if (Rest && CameraOwner->PCOwner->GetPawn())
        {
            TArray<USkeletalMeshComponent*> Meshes;
            CameraOwner->PCOwner->GetPawn()->GetComponents(Meshes);
            for (auto* Mesh : Meshes)
            {
                OwnerVisibility.FindOrAdd(Mesh, Mesh->bOwnerNoSee);
                Mesh->SetOwnerNoSee(true);
            }
        }
    }
    FMinimalViewInfo Target = POV;
    if (Rest)
    {
        // Pillow at the head of this reference bed; eye clears bedding and headboard.
        Target.Location = PS->RestingBed->GetActorTransform().TransformPosition(FVector(0,-72,79));
        Target.Rotation = (PS->RestingBed->GetActorQuat()*FRotator(57,90,0).Quaternion()).Rotator();
    }
    Elapsed += FMath::Max(0.f, DT);
    const float T = FMath::Clamp(Elapsed / 1.15f, 0.f, 1.f);
    const float Blend = T*T*(3.f-2.f*T);
    if (!Rest && T >= 1.f && OwnerVisibility.Num())
    {
        for (const auto& Entry : OwnerVisibility)
            if (Entry.Key.IsValid()) Entry.Key->SetOwnerNoSee(Entry.Value);
        OwnerVisibility.Empty();
    }
    if (T < 1.f)
    {
        Target.Location = FMath::Lerp(From.Location,Target.Location,Blend);
        Target.Rotation = FQuat::Slerp(From.Rotation.Quaternion(),Target.Rotation.Quaternion(),Blend).Rotator();
    }
    POV.Location = Target.Location;
    POV.Rotation = Target.Rotation;
    Previous = POV;
    return false;
}
