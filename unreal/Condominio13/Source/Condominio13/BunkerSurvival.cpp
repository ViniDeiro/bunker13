#include "BunkerSurvival.h"
#include "Survival/BunkerRadiationModel.h"
#include "BunkerNetwork.h"
#include "BunkerObservedAction.h"
#include "BunkerInteractable.h"
#include "BunkerContainer.h"
#include "BunkerRound.h"
#include "BunkerDoor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameStateBase.h"
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
    if (!HasAuthority() || !bSessionReady || !Rules || Health<=0) return;
    const auto* Round=ABunkerRound::Find(GetWorld());
    if(Round && Round->Phase==0)return;
    const float Minutes=DT/60.f;
    Food=FMath::Clamp(Food-Rules->FoodLossPerMinute*Minutes,0.f,100.f);
    Water=FMath::Clamp(Water-Rules->WaterLossPerMinute*Minutes,0.f,100.f);
    Energy=FMath::Clamp(Energy+(RestingBed?Rules->RestGainPerMinute:-Rules->EnergyLossPerMinute)*Minutes,0.f,100.f);
    if (Food<=0 || Water<=0) Health=FMath::Max(0.f,Health-Rules->StarvationDamagePerMinute*Minutes);
    if (const APawn* Pawn=GetPawn())
    {
        const bool Exposed=Round && Round->bAirlockEnabled && Round->Phase==3 && Rules->RadiationZone.IsInsideOrOn(Pawn->GetActorLocation());
        const auto Result=C13::Radiation::Advance({RadiationBurden,0},
            {0,0,Rules->RadiationSymptomThreshold,Rules->RadiationDamagePerSecond},
            DT,Exposed?Rules->RadiationPerSecond:0,false);
        if(Result.Accepted)
        {
            RadiationBurden=Result.Next.Burden;
            Health=FMath::Max(0.f,Health-static_cast<float>(Result.Damage));
        }
    }
    if (Health<=0)
        if (auto* C=Cast<ACharacter>(GetPawn())) C->GetCharacterMovement()->DisableMovement();
}
void ABunkerPlayerController::ToggleInventory()
{
    auto* State=GetPlayerState<ABunkerPlayerState>();if (!State || !State->bSessionReady) return;
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
    if (ServerContainer || !PS || !PS->bSessionReady || !PS->Rules || PS->Health<=0 || !GetPawn() || GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
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
    ABunkerObservedAction::StartFor(this,Used,FVector::ZeroVector,3,PS->Rules->ItemUseDuration);
    ClientNotice(TEXT("Usado: ")+Name);
    UE_LOG(LogTemp,Display,TEXT("C13_CONSUME id=%s water=%.2f food=%.2f health=%.2f"),*Id.ToString(),Water,Food,Health);
}
void ABunkerPlayerController::ServerDropItem_Implementation(FGuid Id)
{
    auto* PS=GetPlayerState<ABunkerPlayerState>();auto* C=Cast<ACharacter>(GetPawn());
    if (ServerContainer || !PS || !PS->bSessionReady || !PS->Rules || !C || PS->RestingBed || PS->Health<=0 || GetWorld()->GetTimeSeconds()<NextInventoryTime) return;
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
    const auto* LobbyRound=ABunkerRound::Find(GetWorld());
    const bool Lobby=LobbyRound&&LobbyRound->Phase==0&&PC->HasAuthority()&&PS->bSessionReady&&
        FParse::Param(FCommandLine::Get(),TEXT("C13MainLobby"));
    if(bLobbyInput!=Lobby)
    {
        bLobbyInput=Lobby;
        PC->bShowMouseCursor=Lobby;
        PC->SetIgnoreMoveInput(Lobby);
        PC->SetIgnoreLookInput(Lobby);
        if(Lobby)
        {
            FInputModeGameAndUI Mode;
            Mode.SetHideCursorDuringCapture(false);
            Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
            PC->SetInputMode(Mode);
        }
        else PC->SetInputMode(FInputModeGameOnly());
    }
    if(Lobby){DrawLobby(*PC);return;}
    if (!PS->bSessionReady) {DrawText(TEXT("Restaurando participante e recursos…"),FLinearColor::White,30,40);return;}
    const float S=FMath::Max(.65f,Canvas->ClipY/720.f);
    auto Text=[this,S](const FString& V,float X,float Y,FLinearColor Color=FLinearColor(.88f,.9f,.85f)) {
        DrawText(V,Color,X,Y,GEngine->GetSmallFont(),1.15f*S,false);
    };
    if(auto* Round=ABunkerRound::Find(GetWorld()))
    {
        FString Label=Round->Phase==0?TEXT("PREPARAÇÃO — host: R inicia a coleta"):
            Round->Phase==1?FString::Printf(TEXT("COLETA — %02d:%02d | recolha suprimentos e desça ao abrigo"),FMath::CeilToInt(Round->Remaining())/60,FMath::CeilToInt(Round->Remaining())%60):
            Round->Phase==2?TEXT("FECHANDO — afaste-se da folha para liberar a passagem"):
            TEXT("ABRIGO — organize os recursos | fora: segure E na porta para liberar");
        FString Objective;
        if(Round->Phase==3)
        {
            const int32 M=Round->DayMinute();
            Label=FString::Printf(TEXT("DIA %d — %02d:%02d"),Round->SurvivalDay(),M/60,M%60);
            if(const auto* Infra=ABunkerInfrastructure::Find(GetWorld()))
            {
                const auto& State=Infra->State;
                const auto Has=[&](FName Type){return PS->Inventory.ContainsByPredicate([&](const auto& Item){return Item.ItemType==Type;});};
                const bool NeedsFuel=State.Fuel<=0.f, NeedsParts=State.Condition<=25.f;
                const bool HasFuel=NeedsFuel&&Has(TEXT("FuelCan")), HasParts=NeedsParts&&Has(TEXT("RepairParts"));
                const bool Outside=PC->GetPawn()&&Round->Gate&&PC->GetPawn()->GetActorLocation().Y>Round->Gate->GetActorLocation().Y;
                if(Outside&&(HasFuel||HasParts))
                    Objective=HasFuel&&HasParts?TEXT("Galão e peças na mochila: volte pela antecâmara."):
                        HasFuel?TEXT("Galão na mochila: volte pela antecâmara para abastecer."):
                                TEXT("Peças na mochila: volte pela antecâmara para fazer a manutenção.");
                else if(HasFuel) Objective=State.Running?TEXT("Desligue o gerador antes de abastecer."):TEXT("Galão na mochila: use o bocal de abastecimento.");
                else if(NeedsFuel) Objective=TEXT("Sem combustível: confira o estoque ou procure galões no estacionamento.");
                else if(HasParts) Objective=State.Running?TEXT("Desligue o gerador antes da manutenção."):TEXT("Peças na mochila: use o ponto de manutenção do gerador.");
                else if(NeedsParts) Objective=TEXT("Gerador desgastado: procure peças no estoque ou no estacionamento.");
                else if(!Infra->Powered()) Objective=TEXT("Gerador pronto: acione o interruptor.");
                else if(!Infra->ServicesPowered()) Objective=TEXT("Energia disponível: ligue o circuito de serviços para filtrar água.");
                else if(State.Filter<=0.f)
                    Objective=Has(TEXT("FilterCartridge"))?TEXT("Desligue a bomba e use o cartucho no filtro."):TEXT("Filtro esgotado: procure um cartucho de reposição.");
                else if(!State.Pump&&State.RawWater>0) Objective=TEXT("Bomba parada: ligue-a para filtrar água.");
                else if(State.CleanWater>=PS->Rules->DrinkLiters&&PS->Water<50.f) Objective=TEXT("Você está com sede: beba água tratada no terminal.");
                else Objective=TEXT("Energia ativa: organize comida, água e suprimentos para o próximo turno.");
            }
            else Objective=TEXT("Organize comida, água e suprimentos.");
        }
        DrawRect(FLinearColor(.025f,.035f,.035f,.85f),20*S,65*S,820*S,42*S);Text(Label,30*S,Objective.IsEmpty()?77*S:68*S);
        if(!Objective.IsEmpty())Text(Objective,30*S,87*S,FLinearColor(.94f,.84f,.58f));
        if(Round->ReleaseDeadline>0 && PC->GetPawn() && Round->Gate && FVector::DistSquared(PC->GetPawn()->GetActorLocation(),Round->Gate->GetActorLocation())<FMath::Square(600.f)){auto* GS=GetWorld()->GetGameState();const float Now=GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();Text(FString::Printf(TEXT("Liberação manual: %.0f s"),FMath::Max(0.f,Round->ReleaseDeadline-Now)),30*S,112*S);}
    }
    if(auto* Round=ABunkerRound::Find(GetWorld()))if(Round->bAirlockEnabled&&Round->Phase==3&&PC->GetPawn()&&Round->Gate&&FVector::DistSquared(PC->GetPawn()->GetActorLocation(),FVector(2550,-330,100))<FMath::Square(700.f))Text(Round->AirlockStatus(),30*S,140*S);
    if(auto* Infra=ABunkerInfrastructure::Find(GetWorld()))for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)if((It->InfraAction==9||It->InfraAction==8)&&PC->GetPawn()&&FVector::DistSquared(PC->GetPawn()->GetActorLocation(),It->GetActorLocation())<90000){Text(It->InfraAction==8?Infra->WaterStatus():Infra->Status(),30*S,112*S);break;}
    const float Bottom=Canvas->ClipY;
    const float Top=Bottom-83*S;
    auto Meter=[&](int Index,const TCHAR* Name,float Value,FLinearColor Color)
    {
        const float X=(20+Index*127)*S;
        DrawRect(FLinearColor(.018f,.027f,.031f,.92f),X,Top,120*S,46*S);
        // Five tiny pictograms drawn on the same canvas as the meters.
        static constexpr uint8 Icons[5][5]={
            {4,4,31,4,4}, {0,14,31,17,14}, {4,4,14,31,14},
            {6,12,31,6,12}, {4,10,17,31,4}
        };
        for(int Row=0;Row<5;++Row)
        {
            const uint8 Bits=Icons[Index][Row];
            for(int Col=0;Col<5;++Col)
                if(Bits&(1<<(4-Col)))DrawRect(Color,X+(8+Col*2.6f)*S,Top+(10+Row*2.6f)*S,2.6f*S,2.6f*S);
        }
        Text(Name,X+25*S,Top+8*S);
        Text(FString::Printf(TEXT("%d"),FMath::RoundToInt(Value)),X+91*S,Top+8*S);
        DrawRect(FLinearColor(.13f,.17f,.19f,.9f),X+9*S,Top+31*S,102*S,6*S);
        DrawRect(Color,X+9*S,Top+31*S,102*S*FMath::Clamp(Value*.01f,0.f,1.f),6*S);
    };
    Meter(0,TEXT("SAÚDE"),PS->Health,FLinearColor(.91f,.29f,.32f));
    Meter(1,TEXT("COMIDA"),PS->Food,FLinearColor(.95f,.65f,.24f));
    Meter(2,TEXT("ÁGUA"),PS->Water,FLinearColor(.28f,.69f,.95f));
    Meter(3,TEXT("ENERGIA"),PS->Energy,FLinearColor(.45f,.83f,.55f));
    if(PS->RadiationBurden>0)
        Meter(4,TEXT("DOSE"),PS->RadiationBurden,FLinearColor(1,.73f,.31f));
    DrawRect(FLinearColor(.015f,.025f,.025f,.85f),20*S,Bottom-32*S,501*S,22*S);
    Text(PS->RestingBed?TEXT("Descansando — F levantar | I mochila"):(GetNetMode()!=NM_Client&&!FParse::Param(FCommandLine::Get(),TEXT("C13PlaytestNoSave"))?TEXT("E interagir | I mochila | F5 salvar"):TEXT("E interagir | I mochila")),30*S,Bottom-30*S);
    if (PS->Health<=0) Text(TEXT("Sem condições de continuar. Resgate e morte ainda em desenvolvimento."),30*S,35*S,FLinearColor(1,.3f,.2f));
    if(!PC->bInventoryOpen && !PS->RestingBed && PS->Health>0)
    {
        DrawRect(FLinearColor(.92f,.93f,.86f,.8f),Canvas->ClipX*.5f-1.5f*S,Canvas->ClipY*.5f-1.5f*S,3*S,3*S);
        if(!PC->InteractionPrompt.IsEmpty()) {const float X=(Canvas->ClipX-610*S)/2;DrawRect(FLinearColor(.025f,.04f,.035f,.82f),X,Canvas->ClipY-115*S,610*S,30*S);Text(PC->InteractionPrompt,X+12*S,Canvas->ClipY-108*S);}
        if(GetWorld()->GetTimeSeconds()<PC->HudNoticeUntil)Text(PC->HudNotice,30*S,30*S,FLinearColor(.93f,.80f,.58f));
    }
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
