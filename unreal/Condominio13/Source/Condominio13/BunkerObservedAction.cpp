#include "BunkerObservedAction.h"
#include "BunkerNetwork.h"
#include "BunkerReferenceCabinet.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/GameStateBase.h"
#include "Net/UnrealNetwork.h"
ABunkerObservedAction::ABunkerObservedAction()
{
    bReplicates=true;PrimaryActorTick.bCanEverTick=true;SetNetCullDistanceSquared(900.f*900.f);SetNetUpdateFrequency(10);
    Root=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));SetRootComponent(Root);
    Left=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Left"));Right=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Right"));Item=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Item"));Accessory=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Utensil"));
    for(auto* C:{Left.Get(),Right.Get(),Item.Get(),Accessory.Get()}) {C->SetupAttachment(Root);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetLightingChannels(true,false,true);}
}
void ABunkerObservedAction::StartFor(ABunkerPlayerController* PC,const FBunkerInventoryEntry& E,FVector Point,uint8 Action,float Length,AActor* Target)
{
    if (!PC || !PC->HasAuthority() || !PC->GetPawn()) return;
    FActorSpawnParameters P;P.Owner=PC->GetPawn();P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* A=PC->GetWorld()->SpawnActor<ABunkerObservedAction>(PC->GetPawn()->GetActorLocation(),FRotator::ZeroRotator,P);
    if(!A)return;A->Performer=PC->GetPawn();A->Visual=E;A->Visual.Id.Invalidate();A->Visual.StorageSlot=-1;
    A->Contact=Point;A->ContactTarget=Target;A->ContactLocal=Target?Target->GetActorTransform().InverseTransformPosition(Point):FVector::ZeroVector;A->Kind=Action;A->Duration=Length;A->Start=PC->GetWorld()->GetGameState()->GetServerWorldTimeSeconds();A->SetLifeSpan(Length+.5f);A->ForceNetUpdate();
}
void ABunkerObservedAction::Tick(float DT)
{
    Super::Tick(DT);if(!Performer || !GetWorld()->GetGameState())return;
    if (Performer->IsLocallyControlled()) {for(auto* M:{Left.Get(),Right.Get(),Item.Get(),Accessory.Get()}) M->SetVisibility(false);return;}
    const float T=(GetWorld()->GetGameState()->GetServerWorldTimeSeconds()-Start)/FMath::Max(.2f,Duration);
    for(auto* M:{Left.Get(),Right.Get(),Item.Get(),Accessory.Get()}) M->SetVisibility(T>=0 && T<=1);if(T<0 || T>1)return;
    if(!Left->GetStaticMesh()) {Left->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Left.SM_Hands_Left")));Right->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Right.SM_Hands_Right")));}
    UStaticMesh* Desired=Visual.WorldMesh;
    if(Kind==3 && T>.22f && (Visual.ItemType==TEXT("Water") || Visual.ItemType==TEXT("Food")))
        if(auto* Open=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Bunker/Hands/SM_Use_")+Visual.ItemType.ToString()+TEXT(".SM_Use_")+Visual.ItemType.ToString())))Desired=Open;
    if (Item->GetStaticMesh()!=Desired) {Item->SetStaticMesh(Desired);for(int I=0;I<Visual.Materials.Num();I++)Item->SetMaterial(I,Visual.Materials[I]);Item->SetWorldScale3D(Visual.WorldScale);}
    if(!bObservedLogged) {UE_LOG(LogTemp,Display,TEXT("C13_OBSERVED_ACTION kind=%d hands=%d item=%s"),Kind,Left->GetStaticMesh()!=nullptr && Right->GetStaticMesh()!=nullptr,*GetNameSafe(Item->GetStaticMesh()));bObservedLogged=true;}
    const FTransform Body(FRotator(0,Performer->GetActorRotation().Yaw,0),Performer->GetActorLocation());
    const FVector Rest=Body.TransformPosition(FVector(25,0,15));FVector P;
    if(Kind==3) P=FMath::Lerp(Rest,Body.TransformPosition(FVector(18,0,60)),FMath::Sin(T*PI));
    else if(Kind==2)
    {FVector Point=Contact;if(auto* Cabinet=Cast<ABunkerReferenceCabinet>(ContactTarget))Point=Cabinet->Hinge->GetComponentTransform().TransformPosition(FVector(101.8f,7,110));else if(ContactTarget)Point=ContactTarget->GetActorTransform().TransformPosition(ContactLocal);P=FMath::Lerp(Rest,Point,FMath::SmoothStep(0.f,.18f,T)*(1-FMath::SmoothStep(.78f,1.f,T)));}
    else P=FMath::Lerp(Kind==1?Rest:Contact,Kind==1?Contact:Rest,FMath::SmoothStep(0.f,1.f,T));
    SetActorLocation(Performer->GetActorLocation());const FRotator Look=Performer->GetActorRotation();
    const bool Eating=Kind==3 && Visual.ItemType==TEXT("Food");
    if(Eating)P=Body.TransformPosition(FVector(35,-9,22));
    Item->SetWorldLocationAndRotation(P,Look+FRotator(Kind==3 && !Eating?FMath::Sin(T*PI)*55:0,90,0));Item->SetVisibility(Kind!=2 && !(Kind==1 && T>.88f));
    Right->SetWorldLocationAndRotation(P+Body.TransformVectorNoScale(FVector(-11,5,7)),Look+FRotator(15,90,0));
    Left->SetWorldLocationAndRotation(P+Body.TransformVectorNoScale(FVector(-11,-6,7)),Look+FRotator(15,90,0));
    Accessory->SetVisibility(Eating);
    if(Eating)
    {
        if(!Accessory->GetStaticMesh())Accessory->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Bunker/Hands/SM_Hands_Spoon.SM_Hands_Spoon")));
        const float Bite=FMath::Sin(FMath::Clamp((T-.2f)/.6f,0.f,1.f)*PI);
        const FVector Spoon=Body.TransformPosition(FMath::Lerp(FVector(40,5,28),FVector(18,2,61),Bite));
        Accessory->SetWorldLocationAndRotation(Spoon,Look+FRotator(0,-90,0));Right->SetWorldLocationAndRotation(Spoon+Body.TransformVectorNoScale(FVector(-12,0,-3)),Look+FRotator(25,90,0));
    }
}
void ABunkerObservedAction::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ABunkerObservedAction,Performer);DOREPLIFETIME(ABunkerObservedAction,Visual);DOREPLIFETIME(ABunkerObservedAction,Contact);DOREPLIFETIME(ABunkerObservedAction,ContactTarget);DOREPLIFETIME(ABunkerObservedAction,ContactLocal);DOREPLIFETIME(ABunkerObservedAction,Kind);DOREPLIFETIME(ABunkerObservedAction,Start);DOREPLIFETIME(ABunkerObservedAction,Duration);}

bool ABunkerObservedAction::IsNetRelevantFor(const AActor* RealViewer,const AActor* ViewTarget,const FVector& SrcLocation) const
{
    if(!Performer || Performer==ViewTarget || !Super::IsNetRelevantFor(RealViewer,ViewTarget,SrcLocation))return false;
    FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(ObservedActionVisibility),false,Performer);Q.AddIgnoredActor(ViewTarget);
    return !GetWorld()->LineTraceSingleByChannel(Hit,SrcLocation,Performer->GetActorLocation()+FVector(0,0,40),ECC_Visibility,Q);
}
