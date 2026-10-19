#include "BunkerNetwork.h"
#include "BunkerInteractable.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "GameFramework/GameStateBase.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "UObject/ConstructorHelpers.h"

void ABunkerPlayerState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION(ABunkerPlayerState, Inventory, COND_OwnerOnly);
    DOREPLIFETIME(ABunkerPlayerState, RestingBed);
}
ABunkerGameMode::ABunkerGameMode()
{
    PlayerControllerClass = ABunkerPlayerController::StaticClass();
    PlayerStateClass = ABunkerPlayerState::StaticClass();
    static ConstructorHelpers::FClassFinder<APawn> PawnBP(TEXT("/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"));
    if (PawnBP.Succeeded()) DefaultPawnClass = PawnBP.Class;
}
void ABunkerGameMode::PreLogin(const FString& Options, const FString& Address, const FUniqueNetIdRepl& Id, FString& Error)
{
    Super::PreLogin(Options, Address, Id, Error);
    if (GetNumPlayers() >= 4) Error = TEXT("Bunker cheio (4 jogadores).");
}
void ABunkerGameMode::Logout(AController* Exiting)
{
    if (auto* PC = Cast<ABunkerPlayerController>(Exiting)) PC->ReleaseBed(true);
    Super::Logout(Exiting);
}
ABunkerPlayerController::ABunkerPlayerController() { PrimaryActorTick.bCanEverTick = true; }
void ABunkerPlayerController::BeginPlay()
{
    Super::BeginPlay();
    if (IsLocalController())
    {
        SetInputMode(FInputModeGameOnly());
        bShowMouseCursor = false;
        ClientNotice(TEXT("CONDOMÍNIO 13 | WASD mover • E usar • F levantar"));
    }
}
void ABunkerPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    InputComponent->BindKey(EKeys::E, IE_Pressed, this, &ABunkerPlayerController::Interact);
    InputComponent->BindKey(EKeys::F, IE_Pressed, this, &ABunkerPlayerController::LeaveBed);
    InputComponent->BindAxisKey(EKeys::MouseX, this, &ABunkerPlayerController::LookYaw);
    InputComponent->BindAxisKey(EKeys::MouseY, this, &ABunkerPlayerController::LookPitch);
}
void ABunkerPlayerController::MoveForward(float V)
{
    if (APawn* P = GetPawn()) P->AddMovementInput(FRotator(0, GetControlRotation().Yaw, 0).Vector(), V);
}
void ABunkerPlayerController::MoveRight(float V)
{
    if (APawn* P = GetPawn()) P->AddMovementInput(FRotationMatrix(FRotator(0, GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::Y), V);
}
void ABunkerPlayerController::LookYaw(float V) { AddYawInput(V * 0.35f); }
void ABunkerPlayerController::LookPitch(float V) { AddPitchInput(-V * 0.35f); }
void ABunkerPlayerController::PlayerTick(float DT)
{
    Super::PlayerTick(DT);
#if !UE_BUILD_SHIPPING
    NetProbeTick(DT);
#endif
    if (!IsLocalController() || !GetPawn() || !PlayerCameraManager) return;
    auto* PS = GetPlayerState<ABunkerPlayerState>();
    if (PS && PS->RestingBed) { Focused.Reset(); return; }
    MoveForward(float(IsInputKeyDown(EKeys::W)) - float(IsInputKeyDown(EKeys::S)));
    MoveRight(float(IsInputKeyDown(EKeys::D)) - float(IsInputKeyDown(EKeys::A)));
    FVector Start; FRotator Rot; GetPlayerViewPoint(Start, Rot);
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BunkerFocus), false, GetPawn());
    GetWorld()->LineTraceSingleByChannel(Hit, Start, Start + Rot.Vector()*350, ECC_Visibility, Params);
    Focused = Cast<ABunkerInteractable>(Hit.GetActor());
    PromptTimer -= DT;
    if (Focused.IsValid() && PromptTimer <= 0)
    {
        if (GEngine) GEngine->AddOnScreenDebugMessage(1301, .25f, FColor::White, Focused->GetPrompt());
        PromptTimer = .15f;
    }
}
void ABunkerPlayerController::Interact() { if (Focused.IsValid()) ServerInteract(Focused.Get()); }
void ABunkerPlayerController::LeaveBed() { ServerLeaveBed(); }
void ABunkerPlayerController::ClientNotice_Implementation(const FString& Message)
{
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 5, FColor(235,205,150), Message);
    UE_LOG(LogTemp, Display, TEXT("C13_NOTICE %s"), *Message);
}
void ABunkerPlayerController::ServerInteract_Implementation(ABunkerInteractable* Target)
{
    auto* PS = GetPlayerState<ABunkerPlayerState>();
    auto* Character = Cast<ACharacter>(GetPawn());
    if (!IsValid(Target) || !PS || !Character || PS->RestingBed) return;
    const double Now = GetWorld()->GetTimeSeconds();
    if (Now < NextActionTime) return;
    NextActionTime = Now + .2;
    FMinimalViewInfo View;
    Character->CalcCamera(0.f, View);
    const FVector Eye = View.Location;
    const FRotator Rot = GetControlRotation();
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BunkerAuthority), false, Character);
    // Validate the same camera ray on authority, not just the client supplied actor.
    if (!GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + Rot.Vector()*350, ECC_Visibility, Params) || Hit.GetActor() != Target)
    {
        UE_LOG(LogTemp, Verbose, TEXT("C13_REJECT view target=%s hit=%s eye=%s rotation=%s"),*Target->GetName(),*GetNameSafe(Hit.GetActor()),*Eye.ToString(),*Rot.ToString()); return;
    }
    if (FVector::DistSquared(Character->GetActorLocation(), Hit.ImpactPoint) > FMath::Square(450.f)) return;
    switch (Target->Interaction)
    {
    case EBunkerInteraction::Pickup:
    {
        if (!Target->bActive) return;
        if (PS->Inventory.Num() >= 12) { ClientNotice(TEXT("Mochila cheia (12 espaços).")); return; }
        FBunkerInventoryEntry Entry; Entry.Id = Target->ItemId; Entry.Name = Target->DisplayName.ToString();
        if (PS->Inventory.ContainsByPredicate([&Entry](const FBunkerInventoryEntry& E){return E.Id == Entry.Id;})) return;
        PS->Inventory.Add(Entry);
        Target->bActive = false; Target->OnRep_State(); Target->ForceNetUpdate(); PS->ForceNetUpdate();
        ClientNotice(FString::Printf(TEXT("Guardado: %s | mochila %d/12"), *Entry.Name, PS->Inventory.Num()));
        UE_LOG(LogTemp, Display, TEXT("C13_PICKUP player=%d id=%s count=%d"), PS->GetPlayerId(), *Entry.Id.ToString(), PS->Inventory.Num());
        break;
    }
    case EBunkerInteraction::Bed:
        if (Target->Occupant) { ClientNotice(TEXT("Esta cama está ocupada.")); return; }
        RestExit = Character->GetActorLocation();
        if (!Character->SetActorLocation(Target->GetActorLocation()+FVector(0,0,72), false, nullptr, ETeleportType::TeleportPhysics)) return;
        Target->Occupant = PS; PS->RestingBed = Target;
        Character->GetCharacterMovement()->DisableMovement();
        Character->ForceNetUpdate(); Target->ForceNetUpdate(); PS->ForceNetUpdate();
        ClientNotice(TEXT("Descansando | F levantar. Recuperação de energia ainda em desenvolvimento."));
        break;
    case EBunkerInteraction::Generator:
        Target->bActive = !Target->bActive; Target->ForceNetUpdate();
        ClientNotice(Target->bActive ? TEXT("Gerador: comando ligado (circuitos em desenvolvimento)") : TEXT("Gerador: comando desligado (circuitos em desenvolvimento)"));
        break;
    case EBunkerInteraction::Darts:
        DartThrows++; DartScore += FMath::RandRange(1,20);
        ClientNotice(FString::Printf(TEXT("Dardos: protótipo %d/3 | %d pontos"), DartThrows, DartScore));
        if (DartThrows >= 3) { DartThrows=0; DartScore=0; }
        break;
    case EBunkerInteraction::Radio:
        ClientNotice(TEXT("RÁDIO: ...Santa Aurora... procurem o antibiótico na clínica...")); break;
    case EBunkerInteraction::Panel:
        ClientNotice(TEXT("Painel: diagnóstico de sobrevivência em desenvolvimento.")); break;
    }
}
void ABunkerPlayerController::ReleaseBed(bool bDisconnect)
{
    if (!HasAuthority()) return;
    auto* PS = GetPlayerState<ABunkerPlayerState>();
    if (!PS || !PS->RestingBed) return;
    auto* C = Cast<ACharacter>(GetPawn());
    FVector Exit = RestExit;
    if (C && !bDisconnect && !GetWorld()->FindTeleportSpot(C, Exit, C->GetActorRotation()))
    {
        ClientNotice(TEXT("A passagem está ocupada. Aguarde para levantar.")); return;
    }
    PS->RestingBed->Occupant = nullptr; PS->RestingBed->ForceNetUpdate(); PS->RestingBed = nullptr;
    if (C && !bDisconnect)
    {
        C->SetActorLocation(Exit, false, nullptr, ETeleportType::TeleportPhysics);
        C->GetCharacterMovement()->SetMovementMode(MOVE_Walking); C->ForceNetUpdate();
    }
    PS->ForceNetUpdate();
    UE_LOG(LogTemp, Display, TEXT("C13_BED_RELEASE player=%d disconnect=%d"), PS->GetPlayerId(), bDisconnect);
}
void ABunkerPlayerState::OnRep_RestingBed()
{
    auto* PC = Cast<APlayerController>(GetOwner());
    if (PC && PC->IsLocalController())
        if (auto* C = Cast<ACharacter>(PC->GetPawn()))
            C->GetCharacterMovement()->SetMovementMode(RestingBed ? MOVE_None : MOVE_Walking);
}

void ABunkerPlayerController::ServerLeaveBed_Implementation() { ReleaseBed(); }
void ABunkerPlayerController::C13Host() { if (GetNetMode() == NM_Standalone) GetWorld()->ServerTravel(TEXT("/Game/Bunker/Lvl_Bunker?listen")); }
void ABunkerPlayerController::C13Join(const FString& Address)
{
    // Engine validates the destination URL; no process execution.
    if (!Address.IsEmpty() && Address.Len() < 128) ClientTravel(Address, TRAVEL_Absolute);
}

#if !UE_BUILD_SHIPPING
namespace {
bool NetTestEnabled() { return FParse::Param(FCommandLine::Get(), TEXT("C13NetTest")); }
ABunkerInteractable* FindProbe(UWorld* W, int Phase)
{
    const FString Name = Phase == 0 ? TEXT("NET_Pickup") : Phase == 1 ? TEXT("NET_Bed") : TEXT("NET_Far");
    for (TActorIterator<ABunkerInteractable> It(W); It; ++It) if (It->DisplayName.ToString() == Name) return *It;
    return nullptr;
}
}
#endif
void ABunkerPlayerController::NetProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    if (!NetTestEnabled() || !IsLocalController() || !GetPawn()) return;
    ProbeTime = GetWorld()->GetGameState() ? GetWorld()->GetGameState()->GetServerWorldTimeSeconds() : ProbeTime+DT;
    // Each phase uses an actual owner-to-server ServerInteract RPC after arranging the test view.
    const int Phase = ProbeTime < 18 ? 0 : ProbeTime < 24 ? 1 : 2;
    if (ProbeTime < 12 || Phase == ProbeCompleted) return;
    if (HasAuthority() && GetNetMode() == NM_ListenServer && Phase < 2 && FParse::Param(FCommandLine::Get(),TEXT("C13RemoteOnly"))) return;
    auto* Target = FindProbe(GetWorld(), Phase);
    if (!Target) return;
    if (!bProbePrepared) { ServerPrepareProbe(Phase); bProbePrepared=true; ProbePreparedAt=ProbeTime; return; }
    if (ProbeTime - ProbePreparedAt < 1) return;
    ServerInteract(Target); ProbeCompleted=Phase; bProbePrepared=false;
    UE_LOG(LogTemp, Display, TEXT("C13_PROBE_SENT phase=%d client=%s"), Phase, *GetName());
    if (Phase == 2)
    {
        auto* PS=GetPlayerState<ABunkerPlayerState>();
        auto* Pick=FindProbe(GetWorld(),0); auto* Bed=FindProbe(GetWorld(),1);
        UE_LOG(LogTemp, Display, TEXT("C13_CLIENT_STATE pickupHidden=%d pickupCollision=%d bedOccupied=%d inventory=%d"), Pick && Pick->IsHidden(), Pick && Pick->GetActorEnableCollision(), Bed && Bed->Occupant != nullptr, PS ? PS->Inventory.Num() : -1);
    }
#endif
}
void ABunkerPlayerController::ServerPrepareProbe_Implementation(int32 Phase)
{
#if !UE_BUILD_SHIPPING
    if (!NetTestEnabled() || Phase<0 || Phase>2) return;
    auto* C=Cast<ACharacter>(GetPawn()); auto* PS=GetPlayerState<ABunkerPlayerState>();
    auto* T=FindProbe(GetWorld(),Phase);
    if (!C || !PS || !T) return;
    if (PS->RestingBed && Phase < 2) return;
    if (Phase < 2)
    {
        C->SetActorLocation(T->GetActorLocation()+FVector(-220, (PS->GetPlayerId()%4)*35-50, 0), false, nullptr, ETeleportType::TeleportPhysics);
        C->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
        C->GetCharacterMovement()->StopMovementImmediately();
    }
    FVector Eye; FRotator R; C->GetActorEyesViewPoint(Eye,R);
    R=(T->GetActorLocation()-Eye).Rotation(); SetControlRotation(R); ClientSetRotation(R,true);
#endif
}
void ABunkerGameMode::BeginPlay()
{
    Super::BeginPlay();
#if !UE_BUILD_SHIPPING
    if (!NetTestEnabled()) return;
    for (int Phase=0;Phase<3;Phase++)
    {
        FActorSpawnParameters P; P.Name=FName(Phase==0 ? TEXT("NET_Pickup") : Phase==1 ? TEXT("NET_Bed") : TEXT("NET_Far"));
        P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        auto* T=GetWorld()->SpawnActor<ABunkerInteractable>(FVector(10000+Phase*2000,10000,5000),FRotator::ZeroRotator,P);
        T->Interaction=Phase==1 ? EBunkerInteraction::Bed : EBunkerInteraction::Pickup;
        T->DisplayName=FText::FromString(P.Name.ToString());
        T->bAlwaysRelevant=true; T->SetActorScale3D(FVector(.5)); T->ForceNetUpdate();
    }
    FTimerHandle Audit;
    GetWorldTimerManager().SetTimer(Audit, FTimerDelegate::CreateWeakLambda(this,[this]() {
        int Players=0,Items=0,Resting=0; TSet<FGuid> Ids;
        for (TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It)
        {
            Players++; Items+=It->Inventory.Num(); Resting+=It->RestingBed!=nullptr;
            for (const auto& E:It->Inventory) Ids.Add(E.Id);
        }
        auto* Pick=FindProbe(GetWorld(),0);auto* Bed=FindProbe(GetWorld(),1);auto* Far=FindProbe(GetWorld(),2);
        const bool Pass=Players==4 && Items==1 && Ids.Num()==1 && Resting==1 && Pick && !Pick->bActive && Bed && Bed->Occupant && Far && Far->bActive;
        UE_LOG(LogTemp, Display, TEXT("C13_NET_AUDIT %s players=%d items=%d unique=%d resting=%d farActive=%d"), Pass?TEXT("PASS"):TEXT("FAIL"),Players,Items,Ids.Num(),Resting,Far && Far->bActive);
    }),32,false);
#endif
}
