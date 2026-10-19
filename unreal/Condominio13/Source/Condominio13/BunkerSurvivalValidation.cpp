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
        UE_LOG(LogTemp,Display,TEXT("C13_SURVIVAL_CLIENT inventory=%d water=%.2f private=%d"),PS->Inventory.Num(),PS->Water,Private);
        SurvivalProbeStage++;
    }
#endif
}
void ABunkerGameMode::StartSurvivalValidation()
{
#if !UE_BUILD_SHIPPING
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalTest"));
    const bool Visual=FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalVisual"));
    if (!Test && !Visual) return;
    if (Test)
    {
        FActorSpawnParameters P;P.Name=TEXT("NET_Second");P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* Item=GetWorld()->SpawnActor<ABunkerInteractable>(FVector(10000,10500,5000),FRotator::ZeroRotator,P);
        Item->ItemType=TEXT("Water");Item->DisplayName=FText::FromString(TEXT("NET_Second"));Item->bAlwaysRelevant=true;
        Item->SetActorScale3D(FVector(.22,.22,.48));Item->ForceNetUpdate();
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
            const bool Pass=Count==1 && IDs.Num()==1 && Dropped->IsValid() && IDs.Contains(*Dropped) && Active==0;
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
