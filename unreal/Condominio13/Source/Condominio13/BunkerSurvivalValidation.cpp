#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/GameStateBase.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UnrealClient.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/HUD.h"

void ABunkerPlayerController::SurvivalProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    if (!FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalTest")) || !IsLocalController() || !GetPawn()) return;
    auto* PS=GetPlayerState<ABunkerPlayerState>();if (!PS || !GetWorld()->GetGameState()) return;
    const float T=GetWorld()->GetGameState()->GetServerWorldTimeSeconds();
    if (T>=60 && SurvivalProbeStage==0) { ProbeKey(EKeys::I);if (!PS->Inventory.IsEmpty()) UsedProbeId=PS->Inventory[0].Id;SurvivalProbeStage++; }
    if (T>=61 && SurvivalProbeStage==1) { ProbeKey(EKeys::U);SurvivalProbeStage++; }
    if (T>=62 && SurvivalProbeStage==2) { if (UsedProbeId.IsValid()) ServerUseItem(UsedProbeId);SurvivalProbeStage++; }
    if (T>=63 && SurvivalProbeStage==3) { ProbeKey(EKeys::I);SurvivalProbeStage++; }
    if (T>=74 && SurvivalProbeStage==4) { ProbeKey(EKeys::I);UsedProbeId.Invalidate();if (!PS->Inventory.IsEmpty()) UsedProbeId=PS->Inventory[0].Id;SurvivalProbeStage++; }
    if (T>=75 && SurvivalProbeStage==5) { ProbeKey(EKeys::G);SurvivalProbeStage++; }
    if (T>=76 && SurvivalProbeStage==6) { if (UsedProbeId.IsValid()) ServerDropItem(UsedProbeId);SurvivalProbeStage++; }
    if (T>=77 && SurvivalProbeStage==7) { ProbeKey(EKeys::I);SurvivalProbeStage++; }
    if (T>=83 && SurvivalProbeStage==8)
    {
        bool Private=true;
        if (!HasAuthority())
            for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)
                if (*It!=PS && (!It->Inventory.IsEmpty() || It->Water!=100)) Private=false;
        bool MeshValid=true;
        for (const auto& E:PS->Inventory) MeshValid &= GetNameSafe(E.WorldMesh)==TEXT("SM_Item_Water") && E.WorldScale.Equals(FVector::OneVector);
        UE_LOG(LogTemp,Display,TEXT("C13_SURVIVAL_CLIENT inventory=%d water=%.2f private=%d mesh=%d"),PS->Inventory.Num(),PS->Water,Private,MeshValid);
        SurvivalProbeStage++;
    }
#endif
}
void ABunkerGameMode::StartSurvivalValidation()
{
#if !UE_BUILD_SHIPPING
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalTest"));
    const bool Visual=FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalVisual"));
    if (FParse::Param(FCommandLine::Get(),TEXT("C13ItemVisual")))
    {
        const TArray<FString> Labels={TEXT("garrafa de água"),TEXT("lata de alimento"),TEXT("kit médico"),TEXT("pilhas"),TEXT("ferramenta")};
        const TArray<FString> Keys={TEXT("Water"),TEXT("Food"),TEXT("Medkit"),TEXT("Battery"),TEXT("Tool")};
        for (int32 I=0;I<Labels.Num();I++)
        {
            FTimerHandle Frame;
            GetWorldTimerManager().SetTimer(Frame,FTimerDelegate::CreateWeakLambda(this,[this,Label=Labels[I],Key=Keys[I]]() {
                auto* PC=UGameplayStatics::GetPlayerController(this,0);if (!PC) return;
                PC->SetInputMode(FInputModeUIOnly());if (PC->GetHUD()) PC->GetHUD()->bShowHUD=false;
                for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
                {
                    if (It->DisplayName.ToString()!=Label) continue;
                    auto* Cam=GetWorld()->SpawnActor<ACameraActor>();
                    const FVector Center=It->Mesh->Bounds.Origin;
                    const float Size=It->Mesh->Bounds.BoxExtent.GetMax()*2;
                    Cam->SetActorLocation(Center+FVector(Size*.9f,FMath::Max(45.f,Size*2.5f),FMath::Max(20.f,Size)));
                    Cam->SetActorRotation((Center-Cam->GetActorLocation()).Rotation());Cam->GetCameraComponent()->SetFieldOfView(50);
                    PC->SetViewTarget(Cam);
                    UE_LOG(LogTemp,Display,TEXT("C13_ITEM_VISUAL %s mesh=%s scale=%s"),*Key,*GetNameSafe(It->Mesh->GetStaticMesh()),*It->GetActorScale3D().ToString());
                    break;
                }
            }),3.f+I*4.f,false);
            FTimerHandle Picture;
            GetWorldTimerManager().SetTimer(Picture,FTimerDelegate::CreateWeakLambda(this,[Key=Keys[I]]() {FScreenshotRequest::RequestScreenshot(TEXT("item_game_")+Key+TEXT(".png"),true,false);}),5.f+I*4.f,false);
        }
        FTimerHandle Quit;GetWorldTimerManager().SetTimer(Quit,FTimerDelegate::CreateWeakLambda(this,[](){FGenericPlatformMisc::RequestExit(false);}),24,false);
    }
    if (!Test && !Visual) return;
    if (Test)
    {
        FActorSpawnParameters P;P.Name=TEXT("NET_Second");P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* Item=GetWorld()->SpawnActor<ABunkerInteractable>(FVector(10000,10500,5000),FRotator::ZeroRotator,P);
        Item->ItemType=TEXT("Water");Item->DisplayName=FText::FromString(TEXT("NET_Second"));Item->bAlwaysRelevant=true;
        Item->PickupMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Items/Water/SM_Item_Water.SM_Item_Water"));
        if (Item->PickupMesh) {Item->PickupScale=FVector::OneVector;Item->OnRep_Visual();}
        else Item->SetActorScale3D(FVector(.22,.22,.48));
        Item->ForceNetUpdate();
        FTimerHandle Used;
        GetWorldTimerManager().SetTimer(Used,FTimerDelegate::CreateWeakLambda(this,[this]() {
            int Count=0,Hydrated=0;
            for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It) {Count+=It->Inventory.Num();Hydrated+=It->Water>60;}
            UE_LOG(LogTemp,Display,TEXT("C13_CONSUME_AUDIT %s items=%d hydrated=%d"),Count==0 && Hydrated==1?TEXT("PASS"):TEXT("FAIL"),Count,Hydrated);
        }),64,false);
        auto Dropped=MakeShared<FGuid>();
        FTimerHandle Remember;
        GetWorldTimerManager().SetTimer(Remember,FTimerDelegate::CreateWeakLambda(this,[this,Dropped]() {
            for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
                if (It->DisplayName.ToString()==TEXT("NET_Second") && It->bActive) *Dropped=It->ItemId;
        }),77,false);
        FTimerHandle Final;
        GetWorldTimerManager().SetTimer(Final,FTimerDelegate::CreateWeakLambda(this,[this,Dropped]() {
            int Count=0,Active=0;TSet<FGuid> IDs;
            for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)
                for (const auto& E:It->Inventory) {Count++;IDs.Add(E.Id);}
            for (TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
                if (It->DisplayName.ToString()==TEXT("NET_Second") && It->bActive) Active++;
            bool MeshPreserved=false;
            for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)
                for (const auto& E:It->Inventory) MeshPreserved=GetNameSafe(E.WorldMesh)==TEXT("SM_Item_Water") && E.WorldScale.Equals(FVector::OneVector);
            const bool Pass=Count==1 && IDs.Num()==1 && Dropped->IsValid() && IDs.Contains(*Dropped) && Active==0 && MeshPreserved;
            UE_LOG(LogTemp,Display,TEXT("C13_ITEM_MESH_AUDIT %s"),MeshPreserved?TEXT("PASS"):TEXT("FAIL"));
            UE_LOG(LogTemp,Display,TEXT("C13_SURVIVAL_AUDIT %s items=%d active=%d sameGuid=%d"),Pass?TEXT("PASS"):TEXT("FAIL"),Count,Active,Dropped->IsValid() && IDs.Contains(*Dropped));
        }),85,false);
    }
    if (Visual)
    {
        FTimerHandle Setup;
        GetWorldTimerManager().SetTimer(Setup,FTimerDelegate::CreateWeakLambda(this,[this]() {
            auto* PC=Cast<ABunkerPlayerController>(UGameplayStatics::GetPlayerController(this,0));
            auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;if (!PS || !PS->Rules) return;
            PS->Health=85;PS->Food=65;PS->Water=40;PS->Energy=35;
            for (const FName Type:{FName(TEXT("Water")),FName(TEXT("Food")),FName(TEXT("Medkit"))})
            {
                FBunkerInventoryEntry E;E.Id=FGuid::NewGuid();E.ItemType=Type;E.WeightKg=PS->Rules->Find(Type)->WeightKg;
                E.Name=Type==TEXT("Water")?TEXT("garrafa de água"):Type==TEXT("Food")?TEXT("lata de alimento"):TEXT("kit médico");PS->Inventory.Add(E);
            }
            PC->bInventoryOpen=true;PC->SetInputMode(FInputModeUIOnly());
        }),2,false);
        FTimerHandle Picture;
        GetWorldTimerManager().SetTimer(Picture,FTimerDelegate::CreateWeakLambda(this,[]() {
            FScreenshotRequest::RequestScreenshot(TEXT("inventory.png"),true,false);
            UE_LOG(LogTemp,Display,TEXT("C13_INVENTORY_SCREENSHOT %s"),*FScreenshotRequest::GetFilename());
        }),6,false);
        FTimerHandle Quit;
        GetWorldTimerManager().SetTimer(Quit,FTimerDelegate::CreateWeakLambda(this,[](){FGenericPlatformMisc::RequestExit(false);}),9,false);
    }
#endif
}
