#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BunkerItemPresentation.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/GameStateBase.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UnrealClient.h"

void ABunkerGameMode::StartHandsValidation()
{
#if !UE_BUILD_SHIPPING
    if (!FParse::Param(FCommandLine::Get(),TEXT("C13HandsVisual"))) return;
    FTimerHandle Setup;
    GetWorldTimerManager().SetTimer(Setup,FTimerDelegate::CreateWeakLambda(this,[this]() {
        auto* PC=Cast<ABunkerPlayerController>(UGameplayStatics::GetPlayerController(this,0));
        auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;if (!PS || !PS->Rules) return;
        PS->Inventory.Empty();PS->Health=40;PS->Food=40;PS->Water=40;
        for (const FName Type:{FName(TEXT("Water")),FName(TEXT("Food")),FName(TEXT("Medkit"))})
        {
            FBunkerInventoryEntry E;E.Id=FGuid::NewGuid();E.ItemType=Type;E.WeightKg=PS->Rules->Find(Type)->WeightKg;E.Name=Type.ToString();
            E.WorldMesh=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Bunker/Items/")+Type.ToString()+TEXT("/SM_Item_")+Type.ToString()+TEXT(".SM_Item_")+Type.ToString()));
            PS->Inventory.Add(E);
        }
    }),2,false);
#endif
}
void ABunkerPlayerController::HandsProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    if (!FParse::Param(FCommandLine::Get(),TEXT("C13HandsVisual")) || !IsLocalController()) return;
    auto* PS=GetPlayerState<ABunkerPlayerState>();if (!PS || !PS->Rules) return;
    const float T=GetWorld()->GetTimeSeconds();
    const float Times[]={3.f,3.12f,3.55f,4.f,6.f,6.12f,7.f,9.f,9.12f,10.f,11.3f,12.f,12.25f,12.5f,14.f,15.f};
    if (HandsProbeStage>=UE_ARRAY_COUNT(Times) || T<Times[HandsProbeStage]) return;
    const int32 Stage=HandsProbeStage++;
    if (Stage==0 || Stage==4 || Stage==7) {if (!bInventoryOpen) ProbeKey(EKeys::I);SelectedItem=0;}
    if (Stage==1 || Stage==5 || Stage==8)
    { if (!PS->Inventory.IsEmpty()) HandsUsedId=PS->Inventory[0].Id;ProbeKey(EKeys::U); }
    if (Stage==10) ServerUseItem(HandsUsedId);
    if (Stage==2 || Stage==3 || Stage==6 || Stage==9 || Stage==13)
    {
        const FString Name=Stage==2?TEXT("hands_water_raise"):Stage==3?TEXT("hands_water_drink"):Stage==6?TEXT("hands_food"):Stage==9?TEXT("hands_medkit"):TEXT("hands_pickup");
        FScreenshotRequest::RequestScreenshot(Name+TEXT(".png"),true,false);
        UE_LOG(LogTemp,Display,TEXT("C13_HAND_FRAME %s playing=%d using=%d"),*Name,ItemPresentation && ItemPresentation->bPlaying,ItemPresentation && ItemPresentation->bUsing);
    }
    if (Stage==11)
    {
        FVector Eye;FRotator Rot;GetPlayerViewPoint(Eye,Rot);
        FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* A=GetWorld()->SpawnActor<ABunkerInteractable>(Eye+Rot.Vector()*120-FVector(0,0,10),FRotator::ZeroRotator,P);
        A->ActionText=FText::FromString(TEXT("pegar"));A->ItemType=TEXT("Water");A->DisplayName=FText::FromString(TEXT("teste de coleta"));A->PickupMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Items/Water/SM_Item_Water.SM_Item_Water"));A->OnRep_Visual();
    }
    if (Stage==12) ProbeKey(EKeys::E);
    if (Stage==14)
    {
        const bool Pass=PS->Inventory.Num()==1 && PS->Food>70 && PS->Water>70 && PS->Health>70 && !bInventoryOpen && !IsLookInputIgnored();
        UE_LOG(LogTemp,Display,TEXT("C13_HANDS_AUDIT %s items=%d food=%.2f water=%.2f health=%.2f lookFree=%d"),Pass?TEXT("PASS"):TEXT("FAIL"),PS->Inventory.Num(),PS->Food,PS->Water,PS->Health,!IsLookInputIgnored());
    }
    if (Stage==15) FGenericPlatformMisc::RequestExit(false);
#endif
}
