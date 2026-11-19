#include "BedroomDrawingBoard.h"
#include "BunkerNetwork.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UObject/ConstructorHelpers.h"
#include "UnrealClient.h"

namespace
{
constexpr float SurfaceX=3.5f;
constexpr int32 MaxMarks=1200;
constexpr float Range=145.f;
}

ABedroomDrawingBoard::ABedroomDrawingBoard()
{
    PrimaryActorTick.bCanEverTick=true;
    PrimaryActorTick.TickGroup=TG_PostUpdateWork;
    RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("BoardRoot"));
    Frame=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Frame"));
    Surface=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Surface"));
    Pen=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Pen"));
    Ink=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Ink"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    for(auto* Mesh:{Frame.Get(),Surface.Get(),Pen.Get(),static_cast<UStaticMeshComponent*>(Ink.Get())})
    {
        Mesh->SetupAttachment(RootComponent);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Mesh->SetCastShadow(false);
        Mesh->SetStaticMesh(Mesh==Pen.Get()?Cylinder.Object:Cube.Object);
    }
    Frame->SetRelativeScale3D(FVector(.05,1.14,.74));
    Surface->SetRelativeLocation(FVector(3,0,0));
    Surface->SetRelativeScale3D(FVector(.01,1.08,.68));
    Pen->SetRelativeTransform(PenRest());
    Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("Instructions"));
    Label->SetupAttachment(RootComponent);
    Label->SetRelativeLocation(FVector(4,-52,44));
    Label->SetWorldSize(5);
    Label->SetText(FText::FromString(TEXT("QUADRO DE TURNO  /  E: CANETA")));
}

FTransform ABedroomDrawingBoard::PenRest() const
{
    return FTransform(FRotator(0,0,90),FVector(8,-39,-34),FVector(.026,.026,.145));
}

void ABedroomDrawingBoard::UpdateBoard(APlayerController& PC,bool Use,bool Draw,bool Clear,FVector Eye,FRotator Look)
{
    const FTransform World=GetActorTransform();
    const FVector Origin=World.InverseTransformPosition(Eye);
    const FVector Direction=World.InverseTransformVectorNoScale(Look.Vector());
    const float Distance=Direction.X<-.001f?(SurfaceX-Origin.X)/Direction.X:-1;
    const FVector Hit=Origin+Direction*Distance;
    FHitResult Block;
    const bool InReach=Distance>=0 && Distance<=Range && FMath::Abs(Hit.Y)<=53 && FMath::Abs(Hit.Z)<=33;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(BedroomDrawing),false,PC.GetPawn());
    Query.AddIgnoredActor(this);
    const bool Contact=InReach && !GetWorld()->LineTraceSingleByChannel(Block,Eye,World.TransformPosition(Hit+FVector(.3,0,0)),ECC_Visibility,Query);
    if(Use && (bHolding||Contact))
    {
        bHolding=!bHolding;
        Label->SetText(FText::FromString(bHolding?TEXT("MOUSE: DESENHAR   E: DEVOLVER   R: LIMPAR"):TEXT("QUADRO DE TURNO  /  E: CANETA")));
    }
    if(!bHolding)
    {
        Pen->SetRelativeTransform(PenRest());
        PreviousPoint.Reset();
        return;
    }
    const FVector Tip=Contact?World.TransformPosition(Hit+FVector(.8,0,0)):Eye+Look.RotateVector(FVector(38,13,-17));
    // Cylinder's negative Z points to the writing surface. Its center trails the tip.
    const FVector Axis=Contact
        ? (World.GetUnitAxis(EAxis::X)*.56f + World.GetUnitAxis(EAxis::Z)*.78f + World.GetUnitAxis(EAxis::Y)*.24f).GetSafeNormal()
        : Look.RotateVector(FVector(-.4,.2,.9)).GetSafeNormal();
    Pen->SetWorldLocationAndRotation(Tip+Axis*7.25f,FRotationMatrix::MakeFromZ(Axis).Rotator());
    if(Clear && Contact){Ink->ClearInstances();PreviousPoint.Reset();return;}
    if(!Draw||!Contact){PreviousPoint.Reset();return;}
    const FVector Point(SurfaceX+.3f,Hit.Y,Hit.Z);
    if(Ink->GetInstanceCount()>=MaxMarks)return;
    const FVector Start=PreviousPoint.Get(Point);
    const FVector Along=Point-Start;
    if(PreviousPoint.IsSet() && Along.SizeSquared()<.25f)return;
    // Break rather than bridge a rapid sweep across the whole board.
    const bool Join=PreviousPoint.IsSet() && Along.SizeSquared()<35.f*35.f;
    const FVector Center=Join?(Point+Start)*.5f:Point;
    const FQuat Rotation=Join?FRotationMatrix::MakeFromXY(FVector::ForwardVector,Along).ToQuat():FQuat::Identity;
    Ink->AddInstance(FTransform(Rotation,Center,FVector(.0025f,(Join?Along.Size()+.9f:.9f)*.01f,.009f)));
    PreviousPoint=Point;
}

void ABedroomDrawingBoard::Tick(float DT)
{
    Super::Tick(DT);
    // Preview is deliberately standalone; never produce inconsistent shared sketches in multiplayer.
    if(GetNetMode()!=NM_Standalone)return;
    auto* PC=Cast<ABunkerPlayerController>(GetWorld()->GetFirstPlayerController());
    if(!PC||!PC->GetPawn())return;
#if !UE_BUILD_SHIPPING
    if(FParse::Param(FCommandLine::Get(),TEXT("C13DrawingTest"))){Probe(*PC,DT);return;}
#endif
    const bool Use=PC->IsInputKeyDown(EKeys::E), Clear=PC->IsInputKeyDown(EKeys::R);
    const auto* State=PC->GetPlayerState<ABunkerPlayerState>();
    if(PC->bInventoryOpen || !State || State->Health<=0 || State->RestingBed)
    {
        PreviousPoint.Reset();bPreviousUse=Use;bPreviousClear=Clear;return;
    }
    FVector Eye;FRotator Look;
    PC->GetPlayerViewPoint(Eye,Look);
    UpdateBoard(*PC,Use&&!bPreviousUse,PC->IsInputKeyDown(EKeys::LeftMouseButton),Clear&&!bPreviousClear,Eye,Look);
    bPreviousUse=Use;bPreviousClear=Clear;
}

#if !UE_BUILD_SHIPPING
void ABedroomDrawingBoard::Probe(APlayerController& PC,float DT)
{
    TestSeconds+=DT;
    if(TestSeconds<3)return;
    auto Aim=[&](float Y,float Z,bool Use=false,bool Draw=false,bool Clear=false)
    {
        const auto World=GetActorTransform();
        const FVector P=World.TransformPosition(FVector(90,0,0));
        const FRotator Look=(World.TransformPosition(FVector(SurfaceX,Y,Z))-P).Rotation();
        PC.GetPawn()->SetActorLocation(FVector(P.X,P.Y,98));
        PC.SetControlRotation(Look);
        UpdateBoard(PC,Use,Draw,Clear,P,Look);
    };
    if(TestStage==0)
    {
        Aim(-36,12,true);
        UE_LOG(LogTemp,Display,TEXT("C13_DRAW_PICKUP pass=%d"),bHolding);
        TestStage=1;
    }
    if(TestSeconds<7 && TestStage==1)
    {
        const float A=(TestSeconds-3)*1.55f;
        Aim(36*FMath::Cos(A),21*FMath::Sin(A),false,true);
        TestFrames.Add(DT);
    }
    else if(TestStage==1)
    {
        const int32 Before=Ink->GetInstanceCount();
        Aim(0,90,false,true);
        Aim(0,0,false,false);
        bTestReleased=Ink->GetInstanceCount()==Before && !PreviousPoint.IsSet();
        UE_LOG(LogTemp,Display,TEXT("C13_DRAW_TRACE pass=%d instances=%d release=%d"),Before>30 && bTestReleased,Before,bTestReleased);
        FScreenshotRequest::RequestScreenshot(TEXT("bedroom_board_game.png"),true,false);
        TestStage=2;
    }
    if(TestSeconds>9 && TestStage==2)
    {
        Aim(0,0,false,false,true);
        Aim(0,0,true);
        float Sum=0;for(float FrameTime:TestFrames)Sum+=FrameTime;
        TestFrames.Sort();
        UE_LOG(LogTemp,Display,TEXT("C13_DRAW_RETURN pass=%d cleared=%d fps=%.2f p95_ms=%.2f samples=%d"),!bHolding && Pen->GetRelativeTransform().Equals(PenRest()),Ink->GetInstanceCount()==0,Sum>0?TestFrames.Num()/Sum:0,TestFrames.IsEmpty()?0:1000*TestFrames[FMath::Min(TestFrames.Num()-1,int(TestFrames.Num()*.95))],TestFrames.Num());
        FGenericPlatformMisc::RequestExit(false);
        TestStage=3;
    }
}
#endif
