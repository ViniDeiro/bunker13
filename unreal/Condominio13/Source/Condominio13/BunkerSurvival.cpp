#include "BunkerSurvival.h"
#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "BunkerContainer.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

const FBunkerItemDefinition* UBunkerSurvivalRules::Find(FName Type) const
{
    return Items.FindByPredicate([Type](const FBunkerItemDefinition& D){return D.ItemType==Type;});
}
ABunkerPlayerState::ABunkerPlayerState()
{
    PrimaryActorTick.bCanEverTick=true;
    PrimaryActorTick.TickInterval=1.f;
}
void ABunkerPlayerState::BeginPlay()
{
    Super::BeginPlay();
    Rules=LoadObject<UBunkerSurvivalRules>(nullptr,TEXT("/Game/Bunker/Data/DA_SurvivalRules.DA_SurvivalRules"));
    if (HasAuthority() && FParse::Param(FCommandLine::Get(),TEXT("C13SurvivalTest"))) {Health=60;Food=40;Water=40;Energy=30;}
    if (!Rules) UE_LOG(LogTemp,Error,TEXT("C13_MISSING_SURVIVAL_RULES"));
}
float ABunkerPlayerState::Weight() const
{
    float Sum=0;for (const auto& E:Inventory) Sum+=E.WeightKg;return Sum;
}
void ABunkerPlayerState::Tick(float DT)
{
    Super::Tick(DT);
    if (!HasAuthority() || !Rules || Health<=0) return;
    const float Minutes=DT/60.f;
    Food=FMath::Clamp(Food-Rules->FoodLossPerMinute*Minutes,0.f,100.f);
    Water=FMath::Clamp(Water-Rules->WaterLossPerMinute*Minutes,0.f,100.f);
    Energy=FMath::Clamp(Energy+(RestingBed?Rules->RestGainPerMinute:-Rules->EnergyLossPerMinute)*Minutes,0.f,100.f);
    if (Food<=0 || Water<=0) Health=FMath::Max(0.f,Health-Rules->StarvationDamagePerMinute*Minutes);
    if (Health<=0)
        if (auto* C=Cast<ACharacter>(GetPawn())) C->GetCharacterMovement()->DisableMovement();
}
void ABunkerPlayerController::ToggleInventory()
{
    if (ViewedContainer) {ServerCloseContainer();CloseContainerView();return;}
    bInventoryOpen=!bInventoryOpen;
    SetIgnoreLookInput(bInventoryOpen);
    SetIgnoreMoveInput(bInventoryOpen);
}
void ABunkerPlayerController::InventoryUp() { if (bInventoryOpen) SelectedItem=FMath::Max(0,SelectedItem-1); }
void ABunkerPlayerController::InventoryDown()
{
    if (auto* PS=GetPlayerState<ABunkerPlayerState>())
        if (bInventoryOpen) SelectedItem=FMath::Min((ViewedContainer && bContainerSide?ContainerEntries.Num():PS->Inventory.Num())-1,SelectedItem+1);
}
void ABunkerPlayerController::UseSelected()
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (ViewedContainer || !bInventoryOpen || !PS || !PS->Inventory.IsValidIndex(SelectedItem)) return;
    ServerUseItem(PS->Inventory[SelectedItem].Id);
}
void ABunkerPlayerController::DropSelected()
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (ViewedContainer || !bInventoryOpen || !PS || !PS->Inventory.IsValidIndex(SelectedItem)) return;
    ServerDropItem(PS->Inventory[SelectedItem].Id);
}
void ABunkerPlayerController::ServerUseItem_Implementation(FGuid Id)
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();
    if (ServerContainer || !PS || !PS->Rules || PS->Health<=0 || !GetPawn() || GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
    NextInventoryTime=GetWorld()->GetTimeSeconds()+PS->Rules->InventoryActionInterval;
    const int32 I=PS->Inventory.IndexOfByPredicate([Id](const FBunkerInventoryEntry& E){return E.Id==Id;});
    if (I==INDEX_NONE) return;
    const auto* Def=PS->Rules->Find(PS->Inventory[I].ItemType);
    if (!Def || (Def->FoodGain<=0 && Def->WaterGain<=0 && Def->HealthGain<=0))
    { ClientNotice(TEXT("Este item não pode ser consumido.")); return; }
    const float Food=FMath::Clamp(PS->Food+Def->FoodGain,0.f,100.f);
    const float Water=FMath::Clamp(PS->Water+Def->WaterGain,0.f,100.f);
    const float Health=FMath::Clamp(PS->Health+Def->HealthGain,0.f,100.f);
    if (Food==PS->Food && Water==PS->Water && Health==PS->Health)
    { ClientNotice(TEXT("Você não precisa usar este recurso agora."));return; }
    const FBunkerInventoryEntry Used=PS->Inventory[I];
    const FString Name=Used.Name;
    NextInventoryTime=GetWorld()->GetTimeSeconds()+FMath::Max(PS->Rules->InventoryActionInterval,PS->Rules->ItemUseDuration);
    NextActionTime=NextInventoryTime;
    PS->Inventory.RemoveAt(I);PS->Food=Food;PS->Water=Water;PS->Health=Health;PS->ForceNetUpdate();
    ClientPlayItemAction(Used,true);
    ClientNotice(TEXT("Usado: ")+Name);
    UE_LOG(LogTemp,Display,TEXT("C13_CONSUME id=%s water=%.2f food=%.2f health=%.2f"),*Id.ToString(),Water,Food,Health);
}
void ABunkerPlayerController::ServerDropItem_Implementation(FGuid Id)
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();auto* C=Cast<ACharacter>(GetPawn());
    if (ServerContainer || !PS || !PS->Rules || !C || PS->RestingBed || PS->Health<=0 || GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
    NextInventoryTime=GetWorld()->GetTimeSeconds()+PS->Rules->InventoryActionInterval;
    const int32 I=PS->Inventory.IndexOfByPredicate([Id](const FBunkerInventoryEntry& E){return E.Id==Id;});
    if (I==INDEX_NONE) return;
    const FBunkerInventoryEntry Entry=PS->Inventory[I];
    if (!Entry.WorldMesh) return;
    const FVector Ahead=FRotator(0,GetControlRotation().Yaw,0).Vector();
    const FVector Spot=C->GetActorLocation()+Ahead*100;
    FHitResult Floor;FCollisionQueryParams Q(SCENE_QUERY_STAT(BunkerDrop),false,C);
    if (!GetWorld()->LineTraceSingleByChannel(Floor,Spot+FVector(0,0,60),Spot-FVector(0,0,250),ECC_Visibility,Q) || Floor.ImpactNormal.Z<.7f)
    { ClientNotice(TEXT("Não há piso seguro para largar o item."));return; }
    const FBoxSphereBounds Bounds=Entry.WorldMesh->GetBounds();
    const FVector Extent=Bounds.BoxExtent*Entry.WorldScale.GetAbs();
    const FVector Center=Floor.ImpactPoint+FVector(0,0,Extent.Z+2);
    const FVector Position=Center-Bounds.Origin*Entry.WorldScale;
    FHitResult Wall;FVector Eye;FRotator R;C->GetActorEyesViewPoint(Eye,R);
    if (GetWorld()->LineTraceSingleByChannel(Wall,Eye,Center,ECC_Visibility,Q) ||
        GetWorld()->OverlapBlockingTestByChannel(Center,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeBox(Extent),Q))
    { ClientNotice(TEXT("O espaço à frente está ocupado."));return; }
    FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Item=GetWorld()->SpawnActor<ABunkerInteractable>(Position,FRotator::ZeroRotator,P);
    if (!Item) return;
    Item->ItemId=Entry.Id;Item->ItemType=Entry.ItemType;Item->DisplayName=FText::FromString(Entry.Name);
    Item->ActionText=FText::FromString(TEXT("pegar"));Item->PickupMesh=Entry.WorldMesh;
    Item->PickupScale=Entry.WorldScale;Item->PickupMaterials=Entry.Materials;Item->OnRep_Visual();Item->ForceNetUpdate();
    PS->Inventory.RemoveAt(I);PS->ForceNetUpdate();
    ClientNotice(TEXT("Largado: ")+Entry.Name);
    UE_LOG(LogTemp,Display,TEXT("C13_DROP id=%s"),*Id.ToString());
}
void ABunkerHUD::DrawHUD()
{
    Super::DrawHUD();
    auto* PC=Cast<ABunkerPlayerController>(PlayerOwner);auto* PS=PC?PC->GetPlayerState<ABunkerPlayerState>():nullptr;
    if (!Canvas || !PS || !PS->Rules) return;
    const float S=FMath::Max(.65f,Canvas->ClipY/720.f);
    auto Text=[this,S](const FString& V,float X,float Y,FLinearColor Color=FLinearColor(.88f,.9f,.85f)) {
        DrawText(V,Color,X,Y,GEngine->GetSmallFont(),1.15f*S,false);
    };
    DrawRect(FLinearColor(.015f,.025f,.025f,.8f),20*S,Canvas->ClipY-70*S,650*S,50*S);
    Text(FString::Printf(TEXT("Saúde %.0f   Alimentação %.0f   Hidratação %.0f   Energia %.0f"),PS->Health,PS->Food,PS->Water,PS->Energy),30*S,Canvas->ClipY-60*S);
    Text(PS->RestingBed?TEXT("Descansando — F levantar | I mochila"):(GetNetMode()==NM_Standalone?TEXT("E interagir | I mochila | F5 salvar"):TEXT("E interagir | I mochila")),30*S,Canvas->ClipY-39*S);
    if (PS->Health<=0) Text(TEXT("Sem condições de continuar. Resgate e morte ainda em desenvolvimento."),30*S,35*S,FLinearColor(1,.3f,.2f));
    if (!PC->bInventoryOpen) return;
    if (PC->ViewedContainer)
    {
        const float X=(Canvas->ClipX-900*S)/2,Y=(Canvas->ClipY-450*S)/2;
        DrawRect(FLinearColor(.025f,.045f,.04f,.97f),X,Y,900*S,450*S);
        Text(PC->ViewedContainer->DisplayName.ToString(),X+24*S,Y+16*S,FLinearColor(.95f,.73f,.4f));
        for (int32 Side=0;Side<2;Side++)
        {
            const bool Storage=Side==0,Active=Storage==PC->bContainerSide;
            const auto& Entries=Storage?PC->ContainerEntries:PS->Inventory;
            float Weight=0;for (const auto& E:Entries) Weight+=E.WeightKg;
            const float C=X+(24+Side*448)*S;
            Text(FString::Printf(TEXT("%s %s %d/%d | %.1f/%.1f kg"),Active?TEXT(">"):TEXT(" "),Storage?TEXT("ARMÁRIO"):TEXT("MOCHILA"),Entries.Num(),Storage?PC->ViewedContainer->MaxSlots:PS->Rules->MaxSlots,Weight,Storage?PC->ViewedContainer->MaxWeightKg:PS->Rules->MaxWeightKg),C,Y+52*S);
            if (Active) PC->SelectedItem=FMath::Clamp(PC->SelectedItem,0,FMath::Max(0,Entries.Num()-1));
            if (Entries.IsEmpty()) Text(TEXT("Vazio"),C,Y+100*S);
            const int32 First=Active?FMath::Max(0,PC->SelectedItem-9):0;
            for (int32 I=First;I<FMath::Min(Entries.Num(),First+10);I++)
            {
                if (Active && I==PC->SelectedItem) DrawRect(FLinearColor(.22f,.26f,.16f,1),C-4*S,Y+(94+(I-First)*28)*S,416*S,26*S);
                Text(Entries[I].Name.Left(32),C,Y+(98+(I-First)*28)*S);
            }
        }
        Text(TEXT("TAB trocar lado  |  ↑ ↓ selecionar  |  X guardar/retirar  |  E ou I fechar"),X+24*S,Y+414*S,FLinearColor(.95f,.73f,.4f));
        return;
    }
    const float X=(Canvas->ClipX-600*S)/2,Y=(Canvas->ClipY-480*S)/2;
    DrawRect(FLinearColor(.025f,.045f,.04f,.96f),X,Y,600*S,480*S);
    Text(TEXT("DEFESA CIVIL  /  EQUIPAMENTO PESSOAL"),X+24*S,Y+20*S,FLinearColor(.95f,.73f,.4f));
    Text(FString::Printf(TEXT("Mochila: %d/%d espaços   %.2f/%.1f kg"),PS->Inventory.Num(),PS->Rules?PS->Rules->MaxSlots:0,PS->Weight(),PS->Rules?PS->Rules->MaxWeightKg:0),X+24*S,Y+52*S);
    PC->SelectedItem=FMath::Clamp(PC->SelectedItem,0,FMath::Max(0,PS->Inventory.Num()-1));
    if (PS->Inventory.IsEmpty()) Text(TEXT("Mochila vazia. Explore o bunker e recolha recursos."),X+24*S,Y+100*S);
    for (int32 I=0;I<PS->Inventory.Num();I++)
    {
        if (I==PC->SelectedItem) DrawRect(FLinearColor(.22f,.26f,.16f,1),X+16*S,Y+(92+I*25)*S,568*S,24*S);
        Text(FString::Printf(TEXT("%s  %s   (%.2f kg)"),I==PC->SelectedItem?TEXT(">"):TEXT(" "),*PS->Inventory[I].Name,PS->Inventory[I].WeightKg),X+24*S,Y+(95+I*25)*S);
    }
    Text(TEXT("↑ ↓ selecionar    U usar    G largar    I fechar"),X+24*S,Y+438*S,FLinearColor(.95f,.73f,.4f));
}
