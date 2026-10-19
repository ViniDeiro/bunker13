// Development-only checks against the authored level and actual player capsule.
#include "BunkerNetwork.h"
#include "BunkerDoor.h"
#include "Camera/CameraTypes.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UnrealClient.h"

void ABunkerGameMode::StartDoorValidation()
{
#if !UE_BUILD_SHIPPING
    const bool Visual=FParse::Param(FCommandLine::Get(),TEXT("C13DoorVisual"));
    if (!Visual && !FParse::Param(FCommandLine::Get(),TEXT("C13DoorAudit"))) return;
    FString Root;
    if (!FParse::Value(FCommandLine::Get(),TEXT("C13ArtifactRoot="),Root)) return;
    FTimerHandle Audit;
    GetWorldTimerManager().SetTimer(Audit,FTimerDelegate::CreateWeakLambda(this,[this,Root,Visual]() {
        if (Visual) return;
        auto* PC=UGameplayStatics::GetPlayerController(this,0);
        auto* C=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
        if (!C) { UE_LOG(LogTemp,Error,TEXT("C13_CAPSULE_AUDIT NO_CHARACTER")); return; }
        const float R=C->GetCapsuleComponent()->GetScaledCapsuleRadius();
        const float H=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
        TArray<FString> Entries; int Count=0,Clear=0;
        FCollisionQueryParams Q(SCENE_QUERY_STAT(BunkerDoorCapsule),false,C);
        for (TActorIterator<ABunkerDoor> It(GetWorld());It;++It)
        {
            auto* D=*It;
            const FQuat Rot=FRotator(0,D->ClosedYaw,0).Quaternion();
            const FVector Center=D->GetActorLocation()+Rot.RotateVector(FVector(D->Width*.5f,0,H+4));
            FHitResult Hit;
            const bool Blocked=GetWorld()->SweepSingleByChannel(Hit,Center+Rot.RotateVector(FVector(0,-100,0)),
                Center+Rot.RotateVector(FVector(0,100,0)),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(R,H),Q);
            Count++;Clear+=!Blocked;
            Entries.Add(FString::Printf(TEXT("{\"actor\":\"%s\",\"x\":%.2f,\"y\":%.2f,\"width_cm\":%.2f,\"clear\":%s,\"hit\":\"%s\"}"),
                *D->GetName(),D->GetActorLocation().X,D->GetActorLocation().Y,D->Width,Blocked?TEXT("false"):TEXT("true"),*GetNameSafe(Hit.GetActor())));
        }
        bool Guard=false;
        TActorIterator<ABunkerDoor> GuardDoor(GetWorld());
        if (GuardDoor)
        {
            auto* It=*GuardDoor;
            const FVector Previous=C->GetActorLocation();
            const FQuat Rot=FRotator(0,It->ClosedYaw,0).Quaternion();
            const FVector Inside=It->GetActorLocation()+Rot.RotateVector(FVector(It->Width*.5f,FMath::Sign(It->OpenAngle)*It->Width*.4f,H+4));
            C->SetActorLocation(Inside,false,nullptr,ETeleportType::TeleportPhysics);
            Guard=!It->TryToggle() && It->bOpen;
            C->SetActorLocation(Previous,false,nullptr,ETeleportType::TeleportPhysics);
        }
        UE_LOG(LogTemp,Display,TEXT("C13_DOOR_PAWN_GUARD %s"),Guard?TEXT("PASS"):TEXT("FAIL"));
        const FString Report=FString::Printf(TEXT("{\"radius_cm\":%.2f,\"half_height_cm\":%.2f,\"doors\":%d,\"clear\":%d,\"pawn_guard_passed\":%s,\"passed\":%s,\"entries\":[%s]}"),
            R,H,Count,Clear,Guard?TEXT("true"):TEXT("false"),Count==13 && Clear==Count && Guard?TEXT("true"):TEXT("false"),*FString::Join(Entries,TEXT(",")));
        const bool Saved=FFileHelper::SaveStringToFile(Report,*FPaths::Combine(Root,TEXT("logs/door_capsule_audit.json")));
        UE_LOG(LogTemp,Display,TEXT("C13_CAPSULE_REPORT %s"),*Report);
        UE_LOG(LogTemp,Display,TEXT("C13_CAPSULE_FILE saved=%d"),Saved);
        UE_LOG(LogTemp,Display,TEXT("C13_CAPSULE_AUDIT %s clear=%d/%d radius=%.1f halfHeight=%.1f"),Count==13 && Clear==Count?TEXT("PASS"):TEXT("FAIL"),Clear,Count,R,H);
        if (!Visual) FGenericPlatformMisc::RequestExit(false);
    }),2,false);
    if (!Visual) return;
    TWeakObjectPtr<ABunkerDoor> Selected;
    for (TActorIterator<ABunkerDoor> It(GetWorld());It;++It)
        if (It->GetActorLocation().X>2400 && It->GetActorLocation().Y < -500 && It->Width>170) {Selected=*It;break;}
    if (!Selected.IsValid()) { UE_LOG(LogTemp,Error,TEXT("C13_VISUAL NO_DOOR"));return; }
    Selected->bOpen=false;
    FTimerHandle View;
    GetWorldTimerManager().SetTimer(View,FTimerDelegate::CreateWeakLambda(this,[this,Selected]() {
        auto* PC=UGameplayStatics::GetPlayerController(this,0);
        auto* C=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
        if (!C || !Selected.IsValid()) return;
        PC->SetIgnoreLookInput(true);PC->SetIgnoreMoveInput(true);
        C->SetActorLocation(Selected->GetActorLocation()+FVector(Selected->Width*.6f,-280,100),false,nullptr,ETeleportType::TeleportPhysics);
        C->GetCharacterMovement()->DisableMovement();
        FMinimalViewInfo V; C->CalcCamera(0,V);
        const FRotator Rot=(Selected->Mesh->Bounds.Origin-V.Location).Rotation();
        PC->SetControlRotation(Rot);PC->ClientSetRotation(Rot,true);
    }),3.5f,false);
    FTimerHandle Closed;
    GetWorldTimerManager().SetTimer(Closed,FTimerDelegate::CreateWeakLambda(this,[Root,Selected]() {
        FScreenshotRequest::RequestScreenshot(TEXT("door_closed.png"),false,false);
        UE_LOG(LogTemp,Display,TEXT("C13_SCREENSHOT_FILE %s"),*FScreenshotRequest::GetFilename());
        UE_LOG(LogTemp,Display,TEXT("C13_VISUAL_CLOSED angle=%.1f"),Selected.IsValid()?Selected->CurrentAngle:-999.f);
    }),6,false);
    FTimerHandle Open;
    GetWorldTimerManager().SetTimer(Open,FTimerDelegate::CreateWeakLambda(this,[this,Selected]() {
        if (Selected.IsValid()) if (auto* PC=Cast<ABunkerPlayerController>(UGameplayStatics::GetPlayerController(this,0))) PC->ServerInteract(Selected.Get());
    }),7,false);
    FTimerHandle Picture;
    GetWorldTimerManager().SetTimer(Picture,FTimerDelegate::CreateWeakLambda(this,[Root,Selected]() {
        FScreenshotRequest::RequestScreenshot(TEXT("door_open.png"),false,false);
        UE_LOG(LogTemp,Display,TEXT("C13_SCREENSHOT_FILE %s"),*FScreenshotRequest::GetFilename());
        UE_LOG(LogTemp,Display,TEXT("C13_VISUAL_OPEN angle=%.1f"),Selected.IsValid()?Selected->CurrentAngle:-999.f);
    }),10,false);
    FTimerHandle Quit;
    GetWorldTimerManager().SetTimer(Quit,FTimerDelegate::CreateWeakLambda(this,[](){FGenericPlatformMisc::RequestExit(false);}),12,false);
#endif
}
