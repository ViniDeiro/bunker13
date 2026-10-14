#include "BunkerInteractionManager.h"
#include "BunkerInteractable.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

ABunkerInteractionManager::ABunkerInteractionManager()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = false;
}

void ABunkerInteractionManager::BeginPlay()
{
    Super::BeginPlay();
    if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        EnableInput(PC);
        InputComponent->BindKey(EKeys::E, IE_Pressed, this, &ABunkerInteractionManager::Interact);
        InputComponent->BindKey(EKeys::F, IE_Pressed, this, &ABunkerInteractionManager::LeaveBed);
        Show(TEXT("CONDOMÍNIO 13  |  WASD mover  •  E interagir  •  F levantar"), FColor(235, 190, 105), 8.f);
    }
}

void ABunkerInteractionManager::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (!PC || !PC->PlayerCameraManager || RestingBed.IsValid()) return;
    const FVector Start = PC->PlayerCameraManager->GetCameraLocation();
    const FVector End = Start + PC->PlayerCameraManager->GetActorForwardVector() * 350.f;
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BunkerInteract), false, PC->GetPawn());
    GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
    ABunkerInteractable* NewFocus = Cast<ABunkerInteractable>(Hit.GetActor());
    if (NewFocus != Focused.Get())
    {
        Focused = NewFocus;
        if (NewFocus) Show(NewFocus->GetPrompt(), FColor::White, 1.5f);
    }
}

void ABunkerInteractionManager::Interact()
{
    ABunkerInteractable* Item = Focused.Get();
    ACharacter* Character = UGameplayStatics::GetPlayerCharacter(this, 0);
    if (!Item || !Character) return;

    switch (Item->Interaction)
    {
        case EBunkerInteraction::Pickup:
            Inventory.Add(Item->DisplayName.ToString());
            Item->SetActorHiddenInGame(true);
            Item->SetActorEnableCollision(false);
            Item->bActive = false;
            Show(FString::Printf(TEXT("Guardado: %s  |  mochila: %d item(ns)"), *Item->DisplayName.ToString(), Inventory.Num()), FColor(120, 230, 160), 4.f);
            break;
        case EBunkerInteraction::Bed:
            RestingBed = Item;
            Character->SetActorLocation(Item->GetActorLocation() + FVector(0, 0, 72));
            Character->SetActorRotation(Item->GetActorRotation());
            Character->GetCharacterMovement()->DisableMovement();
            Show(TEXT("Você está descansando. Energia se recupera.  [F] levantar"), FColor(255, 205, 135), 8.f);
            break;
        case EBunkerInteraction::Darts:
        {
            const int32 Score = FMath::RandRange(1, 20) * (FMath::RandRange(0, 4) == 0 ? 3 : 1);
            DartThrows++;
            DartScore += Score;
            Show(FString::Printf(TEXT("DARDOS  •  arremesso %d/3  •  +%d  •  total %d"), DartThrows, Score, DartScore), FColor(255, 185, 80), 4.f);
            if (DartThrows >= 3) { Show(FString::Printf(TEXT("Fim da rodada: %d pontos. [E] iniciar outra"), DartScore), FColor(255, 220, 100), 6.f); DartThrows = 0; DartScore = 0; }
            break;
        }
        case EBunkerInteraction::Generator:
            bGeneratorOn = !bGeneratorOn;
            Show(bGeneratorOn ? TEXT("Gerador ligado — sistemas essenciais alimentados") : TEXT("Gerador desligado — modo de emergência"), bGeneratorOn ? FColor::Green : FColor::Red, 5.f);
            break;
        case EBunkerInteraction::Radio:
            Show(TEXT("RÁDIO: ...Santa Aurora... procurem o antibiótico na clínica..."), FColor(120, 200, 255), 7.f);
            break;
        case EBunkerInteraction::Panel:
            Show(TEXT("STATUS: filtragem 78%  •  água 62%  •  porta externa segura"), FColor(100, 220, 255), 6.f);
            break;
    }
}

void ABunkerInteractionManager::LeaveBed()
{
    if (!RestingBed.IsValid()) return;
    if (ACharacter* Character = UGameplayStatics::GetPlayerCharacter(this, 0))
    {
        Character->SetActorLocation(RestingBed->GetActorLocation() + RestingBed->GetActorRightVector() * 110.f + FVector(0, 0, 20));
        Character->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    }
    RestingBed.Reset();
    Show(TEXT("Você se levantou descansado."), FColor(180, 230, 180), 3.f);
}

void ABunkerInteractionManager::Show(const FString& Message, FColor Color, float Seconds) const
{
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, Seconds, Color, Message, true, FVector2D(1.2f, 1.2f));
}
