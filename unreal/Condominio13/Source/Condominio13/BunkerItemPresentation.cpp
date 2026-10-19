#include "BunkerItemPresentation.h"
#include "BunkerNetwork.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/StaticMesh.h"
#include "Components/PointLightComponent.h"

namespace { FRotator GripRotation(float Pitch,float Yaw,float Roll=0)
{ return (FRotator(Pitch,0,Roll).Quaternion()*FRotator(0,Yaw,0).Quaternion()).Rotator(); } }

ABunkerItemPresentation::ABunkerItemPresentation()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickGroup=TG_PostUpdateWork;
    bReplicates=false;
    Root=CreateDefaultSubobject<USceneComponent>(TEXT("PresentationRoot"));SetRootComponent(Root);
    Left=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftGlove"));
    Right=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightGlove"));
    Item=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PhysicalItem"));
    Accessory=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Utensil"));
    for (auto* M:{Left.Get(),Right.Get(),Item.Get(),Accessory.Get()})
    {
        M->SetupAttachment(Root);M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        M->SetCastShadow(false);M->bReceivesDecals=false;M->SetLightingChannels(false,true,false);
    }
    KeyLight=CreateDefaultSubobject<UPointLightComponent>(TEXT("HandKey"));
    FillLight=CreateDefaultSubobject<UPointLightComponent>(TEXT("HandFill"));
    for (auto* Light:{KeyLight.Get(),FillLight.Get()})
    {
        Light->SetupAttachment(Root);Light->SetMobility(EComponentMobility::Movable);
        Light->SetLightingChannels(false,true,false);Light->SetCastShadows(false);
        Light->SetIntensityUnits(ELightUnits::Lumens);Light->SetAttenuationRadius(90);Light->SetVisibility(false);
    }
    KeyLight->SetRelativeLocation(FVector(12,-28,10));KeyLight->SetIntensity(250);KeyLight->SetLightColor(FLinearColor(1,.87f,.7f));
    FillLight->SetRelativeLocation(FVector(30,28,0));FillLight->SetIntensity(100);FillLight->SetLightColor(FLinearColor(.65f,.78f,1));
    SetActorHiddenInGame(true);
}
void ABunkerItemPresentation::Play(ABunkerPlayerController* PC,FName Type,UStaticMesh* Mesh,const TArray<TObjectPtr<UMaterialInterface>>& Materials,FVector Scale,bool bConsume,float Duration)
{
    if (!PC || !PC->IsLocalController() || !Mesh) return;
    Viewer=PC;ItemType=Type;bUsing=bConsume;Elapsed=0;Length=FMath::Max(.2f,Duration);bPlaying=true;
    Left->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Left.SM_Hands_Left")));
    Right->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Right.SM_Hands_Right")));
    ClosedMesh=Mesh;OpenMesh=nullptr;
    if (bConsume && (Type==TEXT("Water") || Type==TEXT("Food")))
        OpenMesh=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Bunker/Hands/SM_Use_")+Type.ToString()+TEXT(".SM_Use_")+Type.ToString()));
    Item->SetStaticMesh(Mesh);Item->SetRelativeScale3D(Scale);Item->SetVisibility(true);
    Item->EmptyOverrideMaterials();for (int32 I=0;I<Materials.Num();I++) Item->SetMaterial(I,Materials[I]);
    Accessory->SetVisibility(bConsume && (Type==TEXT("Food") || Type==TEXT("Medkit")));
    if (Type==TEXT("Food")) Accessory->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Spoon.SM_Hands_Spoon")));
    if (Type==TEXT("Medkit")) Accessory->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Bandage.SM_Hands_Bandage")));
    SetActorHiddenInGame(false);KeyLight->SetVisibility(true);FillLight->SetVisibility(true);
    UE_LOG(LogTemp,Display,TEXT("C13_HAND_ACTION type=%s consume=%d mesh=%s hands=%d local=%d"),*Type.ToString(),bConsume,*GetNameSafe(Mesh),Left->GetStaticMesh()!=nullptr && Right->GetStaticMesh()!=nullptr,PC->IsLocalController());
    Tick(0);
}
void ABunkerItemPresentation::Tick(float DT)
{
    Super::Tick(DT);
    if (!bPlaying) return;
    auto* PS=Viewer?Viewer->GetPlayerState<ABunkerPlayerState>():nullptr;
    if (!Viewer || !Viewer->GetPawn() || !PS || PS->Health<=0 || PS->RestingBed || Viewer->bInventoryOpen)
    {bPlaying=false;SetActorHiddenInGame(true);KeyLight->SetVisibility(false);FillLight->SetVisibility(false);return;}
    Elapsed+=DT;const float T=Elapsed/Length;
    if (T>=1) {bPlaying=false;SetActorHiddenInGame(true);KeyLight->SetVisibility(false);FillLight->SetVisibility(false);return;}
    UStaticMesh* Desired=(bUsing && T>.22f && OpenMesh)?OpenMesh.Get():ClosedMesh.Get();
    if (Item->GetStaticMesh()!=Desired) Item->SetStaticMesh(Desired);
    FVector Eye;FRotator Look;Viewer->GetPlayerViewPoint(Eye,Look);SetActorLocationAndRotation(Eye,Look);
    const float Enter=FMath::SmoothStep(0.f,.23f,T),Exit=FMath::SmoothStep(.78f,1.f,T);
    const float Lift=Enter*(1-Exit);
    FVector L(26,-7,-45+28*Lift),R(26,7,-45+28*Lift),P(46,0,-45+24*Lift);
    FRotator LR(20*Lift,90,0),RR(20*Lift,90,0),IR(0,90,0);
    if (!bUsing)
    {
        P=FMath::Lerp(FVector(62,0,-8),FVector(34,0,-43),FMath::SmoothStep(0.f,1.f,T));
        L.X+=12*(1-T);R.X+=12*(1-T);L.Z+=7*(1-T);R.Z+=7*(1-T);
    }
    else if (ItemType==TEXT("Water"))
    {
        const float Sip=FMath::SmoothStep(.25f,.45f,T)*(1-FMath::SmoothStep(.65f,.8f,T));
        P+=FVector(-9,0,15)*Sip;IR.Pitch=62*Sip;L+=FVector(-9,0,5)*Sip;R+=FVector(-9,0,5)*Sip;LR.Pitch+=25*Sip;RR.Pitch+=25*Sip;
    }
    else if (ItemType==TEXT("Food"))
    {
        P=FVector(40,-7,-45+23*Lift);
        L.Z=-45+27*Lift;LR.Pitch=25*Lift;R.Z-=2*Lift;
        const float Bite=FMath::Sin(FMath::Clamp((T-.25f)/.5f,0.f,1.f)*PI);
        R+=FVector(-5,-1,12)*Bite;
        Accessory->SetRelativeLocation(FVector(45,5,-25+12*Lift)+FVector(-10,-2,10)*Bite);
        Accessory->SetRelativeRotation(GripRotation(-12,-90,-15));
    }
    else if (ItemType==TEXT("Medkit"))
    {
        P=FVector(49,-5,-55+19*Lift);L=FVector(30,-9,-43+26*Lift);LR.Pitch=25*Lift;RR.Pitch=35*Lift;
        R=FVector(22,0,-43+27*Lift);const float Wrap=FMath::Sin(T*PI*5)*Lift;
        R.Y-=2*Lift;R.Z+=2*Wrap;
        Accessory->SetRelativeLocation(FVector(32,-8,-42+31*Lift+2*Wrap));
        Accessory->SetRelativeRotation(FRotator(90,0,T*360));
    }
    Left->SetRelativeLocationAndRotation(L,GripRotation(LR.Pitch,LR.Yaw,LR.Roll));
    Right->SetRelativeLocationAndRotation(R,GripRotation(RR.Pitch,RR.Yaw,RR.Roll));
    Item->SetRelativeLocationAndRotation(P,GripRotation(IR.Pitch,IR.Yaw,IR.Roll));
    Item->SetVisibility(!(bUsing && ItemType==TEXT("Medkit") && T>.22f));
}

void ABunkerPlayerController::ClientPlayItemAction_Implementation(const FBunkerInventoryEntry& Entry,bool bConsume)
{
    if (!IsLocalController()) return;
    if (bInventoryOpen) ToggleInventory();
    if (!ItemPresentation)
    {
        FActorSpawnParameters P;P.Owner=this;P.ObjectFlags|=RF_Transient;
        ItemPresentation=GetWorld()->SpawnActor<ABunkerItemPresentation>(P);
    }
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (ItemPresentation && PS && PS->Rules)
        ItemPresentation->Play(this,Entry.ItemType,Entry.WorldMesh,Entry.Materials,Entry.WorldScale,bConsume,bConsume?PS->Rules->ItemUseDuration:PS->Rules->ItemPickupDuration);
}
