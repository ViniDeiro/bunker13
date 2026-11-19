#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "GameFramework/Character.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "InputKeyEventArgs.h"
#include "Camera/PlayerCameraManager.h"

void C13BedroomStudy(ABunkerPlayerController* PC,float DT)
{
#if !UE_BUILD_SHIPPING
    if(!FParse::Param(FCommandLine::Get(),TEXT("C13RoomStudyTest")) ||
       !PC->GetWorld()->GetMapName().Contains(TEXT("Bedroom_Study")) || !PC->IsLocalController() || !PC->GetPawn())return;
    static int32 BedroomStudyStage=0;
    static float BedroomStudyEnergy=0;
    static bool BlendChecked=false;
    static float RestStartedAt=0;
    static TArray<double> BedroomStudyFrames;
    static TWeakObjectPtr<UWorld> LastWorld;
    if(LastWorld.Get()!=PC->GetWorld()){LastWorld=PC->GetWorld();BedroomStudyStage=0;BedroomStudyFrames.Empty();BlendChecked=false;}
    auto Key=[&](FKey K){PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Pressed,1.f,false,FPlatformTime::Cycles64()));PC->InputKey(FInputKeyEventArgs(nullptr,INPUTDEVICEID_NONE,K,IE_Released,0.f,false,FPlatformTime::Cycles64()));};
    auto* PS=PC->GetPlayerState<ABunkerPlayerState>(); if(!PS||!PS->Rules)return;
    const float T=PC->GetWorld()->GetTimeSeconds();
    if(T>3&&T<23&&DT>0)BedroomStudyFrames.Add(DT);
    auto Pose=[&](FVector P,FVector Target){PC->GetPawn()->SetActorLocation(P);PC->SetControlRotation((Target-(P+FVector(0,0,64))).Rotation());};
    const bool Secondary=FParse::Param(FCommandLine::Get(),TEXT("C13RoomStudyBed02"));
    const FVector BedOrigin=Secondary?FVector(113,-59,0):FVector(117,-314,0);
    ABunkerInteractable* Bed=nullptr;
    for(TActorIterator<ABunkerInteractable> It(PC->GetWorld());It;++It)if(It->Interaction==EBunkerInteraction::Bed && FVector::DistSquared(It->GetActorLocation(),BedOrigin)<25){Bed=*It;break;}
    if(T>2&&BedroomStudyStage==0){PS->Energy=35;Pose(FVector(375,-80,98),FVector(150,-330,125));BedroomStudyStage=1;}
    if(T>8&&BedroomStudyStage==1){FScreenshotRequest::RequestScreenshot(TEXT("bedroom_unreal_overview.png"),true,false);BedroomStudyStage=2;}
    if(T>10&&BedroomStudyStage==2){Pose(Secondary?FVector(279,-65,98):FVector(245,-235,98),BedOrigin+FVector(0,0,48));BedroomStudyStage=3;}
    if(T>12&&BedroomStudyStage==3){BedroomStudyEnergy=PS->Energy;RestStartedAt=T;Key(EKeys::E);BedroomStudyStage=4;}
    if(T-RestStartedAt>.4f&&T-RestStartedAt<1.f&&BedroomStudyStage==4&&!BlendChecked&&Bed&&PC->PlayerCameraManager)
    {
        const FVector Expected=Bed->GetActorTransform().TransformPosition(FVector(0,-72,79));
        const float Distance=FVector::Dist(PC->PlayerCameraManager->GetCameraLocation(),Expected);
        UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_CAMERA_BLEND pass=%d remaining_cm=%.2f"),PS->RestingBed==Bed&&Distance>5.f&&Distance<250.f,Distance);
        BlendChecked=true;
    }
    if(T>15&&BedroomStudyStage==4)
    {
        const bool Pass=Bed&&PS->RestingBed==Bed&&Bed->Occupant==PS&&PS->Energy>BedroomStudyEnergy+.2f;
        UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_REST pass=%d energy_before=%.3f energy_after=%.3f"),Pass,BedroomStudyEnergy,PS->Energy);
        const FVector Expected=Bed?Bed->GetActorTransform().TransformPosition(FVector(0,-72,79)):FVector::ZeroVector;
        const bool CameraPass=Bed&&PC->PlayerCameraManager&&FVector::Dist(PC->PlayerCameraManager->GetCameraLocation(),Expected)<2.f;
        UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_REST_CAMERA pass=%d"),CameraPass);
        FScreenshotRequest::RequestScreenshot(TEXT("bedroom_unreal_rest.png"),true,false);BedroomStudyStage=5;
    }
    if(T>16&&BedroomStudyStage==5){Key(EKeys::F);BedroomStudyStage=6;}
    if(T>17&&BedroomStudyStage==6)
    {
        UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_RELEASE pass=%d"),Bed&&PS->RestingBed==nullptr&&Bed->Occupant==nullptr);BedroomStudyStage=7;
    }
    if(T>17&&T<23&&BedroomStudyStage==7)
    {
        FVector Dir=FVector(285,-90,0)-PC->GetPawn()->GetActorLocation();Dir.Z=0;
        if(Dir.Size()>25)Cast<ACharacter>(PC->GetPawn())->AddMovementInput(Dir.GetSafeNormal(),.5f);
        else {BedroomStudyStage=8;UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_WALK pass=1 location=%s"),*PC->GetPawn()->GetActorLocation().ToString());}
    }
    if(T>24&&BedroomStudyStage<9)
    {
        double Sum=0;for(double V:BedroomStudyFrames)Sum+=V;BedroomStudyFrames.Sort();
        const double P95=BedroomStudyFrames.Num()?BedroomStudyFrames[FMath::Clamp(FMath::FloorToInt(BedroomStudyFrames.Num()*.95),0,BedroomStudyFrames.Num()-1)]*1000:0;
        UE_LOG(LogTemp,Display,TEXT("C13_BEDROOM_FPS samples=%d fps=%.2f p95_ms=%.2f stage=%d"),BedroomStudyFrames.Num(),Sum>0?BedroomStudyFrames.Num()/Sum:0,P95,BedroomStudyStage);
        BedroomStudyStage=9;
    }
    if(T>26)FGenericPlatformMisc::RequestExit(false);
#endif
}
