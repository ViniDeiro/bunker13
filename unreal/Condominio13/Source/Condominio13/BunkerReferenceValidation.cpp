#include "BunkerNetwork.h"
#include "BunkerReferenceCabinet.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/PlatformTime.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Misc/Paths.h"
#include "Misc/App.h"
#include "HAL/IConsoleManager.h"
#include "UnrealClient.h"

// Development-only comparison: test the cooked world, including actual furniture collisions.
static void AuditOpenPlan(UWorld* W, APawn* Pawn)
{
    FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
    FCollisionQueryParams Q(SCENE_QUERY_STAT(OpenPlan),true,Pawn);
    const auto Shape=FCollisionShape::MakeCapsule(34.f,96.f);
    TSet<FIntPoint> Free,Reached;TArray<FIntPoint> Queue;
    auto Pos=[](FIntPoint P){return FVector(25+P.X*50,-25-P.Y*50,102);};
    for(int X=0;X<56;X++)for(int Y=0;Y<40;Y++)
    {
        FIntPoint P(X,Y);const FVector V=Pos(P);FHitResult Floor;
        if(!W->OverlapAnyTestByObjectType(V,FQuat::Identity,Objects,Shape,Q) && W->LineTraceSingleByObjectType(Floor,FVector(V.X,V.Y,30),FVector(V.X,V.Y,-40),Objects,Q) && Floor.ImpactNormal.Z>.9f)Free.Add(P);
    }
    const FIntPoint Start(22,19);if(Free.Contains(Start)){Reached.Add(Start);Queue.Add(Start);}
    for(int I=0;I<Queue.Num();I++)for(const auto D:{FIntPoint(1,0),FIntPoint(-1,0),FIntPoint(0,1),FIntPoint(0,-1)})
    {
        const auto Next=Queue[I]+D;if(!Free.Contains(Next)||Reached.Contains(Next))continue;
        FHitResult Hit;if(W->SweepSingleByObjectType(Hit,Pos(Queue[I]),Pos(Next),FQuat::Identity,Objects,Shape,Q))continue;
        Reached.Add(Next);Queue.Add(Next);
    }
    const FVector Targets[]={FVector(1150,-650,0),FVector(2000,-400,0),FVector(2500,-1400,0),FVector(250,-1450,0),FVector(800,-1450,0),FVector(1400,-1450,0)};
    int Count=0;for(int I=0;I<UE_ARRAY_COUNT(Targets);I++)
    {bool OK=false;for(auto P:Reached)if(FVector::Dist2D(Pos(P),Targets[I])<130){OK=true;break;}Count+=OK;UE_LOG(LogTemp,Display,TEXT("C13_OPEN_PLAN_ZONE index=%d reachable=%d"),I,OK);}
    int Four=0;for(const float X:{1095.f,1205.f})for(const float Y:{-945.f,-1055.f})Four+=!W->OverlapAnyTestByObjectType(FVector(X,Y,102),FQuat::Identity,Objects,Shape,Q);
    UE_LOG(LogTemp,Display,TEXT("C13_OPEN_PLAN_AUDIT zones=%d total=6 free=%d reachable=%d four_capsules=%d"),Count,Free.Num(),Reached.Num(),Four);
}

void ABunkerPlayerController::ReferenceProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    if (!IsLocalController() || !FParse::Param(FCommandLine::Get(),TEXT("C13Reference")) || !GetPawn()) return;
    if (FParse::Param(FCommandLine::Get(),TEXT("C13PhysicalTest"))) {PhysicalProbeTick(DT);return;}
    if(FParse::Param(FCommandLine::Get(),TEXT("C13ReferenceShowcase")) && ReferenceStage>0)return;
    const double Now=FPlatformTime::Seconds();
    const float T=GetWorld()->GetTimeSeconds();
    FString Phase=TEXT("before");FParse::Value(FCommandLine::Get(),TEXT("ReferencePhase="),Phase);
    if (ReferenceWall && T>8 && T<24) ReferenceFrames.Add((Now-ReferenceWall)*1000.0);
    ReferenceWall=Now;
    if (ReferenceStage==0 && T>3)
    {
        const bool OpenPlan=FParse::Param(FCommandLine::Get(),TEXT("C13OpenPlan"));
        if(OpenPlan && HasAuthority())AuditOpenPlan(GetWorld(),GetPawn());
        GetPawn()->SetActorLocation(FVector(1460,-650,98));
        SetControlRotation((FVector(1000,-285,125)-FVector(1460,-650,160)).Rotation());
        if(OpenPlan){GetPawn()->SetActorLocation(FVector(2100,-1050,102));SetControlRotation((FVector(1100,-500,130)-FVector(2100,-1050,170)).Rotation());}
        ReferenceStage=1;
        if(FParse::Param(FCommandLine::Get(),TEXT("C13ReferenceShowcase")))
        {
            TActorIterator<ABunkerReferenceCabinet> BoxIt(GetWorld());auto* Box=BoxIt?*BoxIt:nullptr;
            if(Box && HasAuthority())
            {
                GetPlayerState<ABunkerPlayerState>()->Food=40;GetPlayerState<ABunkerPlayerState>()->Water=40;TSet<FName> Added;int Slot=6;for(TActorIterator<ABunkerInteractable> It(GetWorld());It;++It)
                    if(It->Interaction==EBunkerInteraction::Pickup && It->bActive && (It->ItemType==TEXT("Water") || It->ItemType==TEXT("Food")) && Slot<8 && !Added.Contains(It->ItemType))
                    {
                        auto* PS=GetPlayerState<ABunkerPlayerState>();FBunkerInventoryEntry E;E.Id=It->ItemId;E.ItemType=It->ItemType;E.Name=It->DisplayName.ToString();E.WeightKg=PS->Rules->Find(E.ItemType)->WeightKg;E.WorldMesh=It->Mesh->GetStaticMesh();E.WorldScale=It->GetActorScale3D();E.StorageSlot=Slot++;
                        for(int I=0;I<It->Mesh->GetNumMaterials();I++)E.Materials.Add(It->Mesh->GetMaterial(I));Box->Contents.Add(E);Added.Add(E.ItemType);It->bActive=false;It->OnRep_State();It->ForceNetUpdate();
                    }
                Box->Revision++;
            }
            ClientNotice(TEXT("Avaliação da sala: esta sessão não grava a campanha. E abre e pega; X guarda o item selecionado da mochila."));
            return;
        }
    }
    if (ReferenceStage==1 && T>7)
    {
        FVector Eye;FRotator R;GetPlayerViewPoint(Eye,R);UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_CAMERA pawn=%s eye=%s rotation=%s"),*GetPawn()->GetActorLocation().ToString(),*Eye.ToString(),*R.ToString());
        const FVector2D Samples[]={FVector2D(.88f,.55f),FVector2D(.5f,.1f)};int SX,SY;GetViewportSize(SX,SY);
        for(int I=0;I<2;I++){FVector O,D;DeprojectScreenPositionToWorld(Samples[I].X*SX,Samples[I].Y*SY,O,D);FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(ReferenceSurface),true,GetPawn());GetWorld()->LineTraceSingleByChannel(H,O,O+D*2000,ECC_Visibility,Q);UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_SURFACE sample=%d actor=%s component=%s point=%s normal=%s"),I,*GetNameSafe(H.GetActor()),*GetNameSafe(H.GetComponent()),*H.ImpactPoint.ToString(),*H.ImpactNormal.ToString());}
        FScreenshotRequest::RequestScreenshot(TEXT("reference_")+Phase+TEXT("_wide.png"),true,false);ReferenceStage=2;
    }
    if (ReferenceStage==2 && T>25)
    {
        ReferenceFrames.Sort();double Sum=0;for (double V:ReferenceFrames) Sum+=V;
        if (ReferenceFrames.Num()) UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_FPS phase=%s samples=%d mean_ms=%.3f median_ms=%.3f p95_ms=%.3f fps=%.2f"),*Phase,ReferenceFrames.Num(),Sum/ReferenceFrames.Num(),ReferenceFrames[ReferenceFrames.Num()/2],ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,FMath::FloorToInt(ReferenceFrames.Num()*.95))],1000.0/(Sum/ReferenceFrames.Num()));
        UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_SETTINGS screen_pct=%.1f shadow_quality=%d max_fps=%.1f vsync=%d"),IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenPercentage"))->GetFloat(),IConsoleManager::Get().FindConsoleVariable(TEXT("r.ShadowQuality"))->GetInt(),IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS"))->GetFloat(),IConsoleManager::Get().FindConsoleVariable(TEXT("r.VSync"))->GetInt());
        GetPawn()->SetActorLocation(FVector(930,-150,98));
        SetControlRotation((FVector(1250,-480,115)-FVector(930,-150,160)).Rotation());ReferenceStage=3;
        if(FParse::Param(FCommandLine::Get(),TEXT("C13OpenPlan"))){GetPawn()->SetActorLocation(FVector(1100,-700,102));SetControlRotation((FVector(2100,-1100,140)-FVector(1100,-700,170)).Rotation());}
    }
    if (ReferenceStage==3 && T>29)
    {FScreenshotRequest::RequestScreenshot(TEXT("reference_")+Phase+TEXT("_reverse.png"),true,false);ReferenceStage=4;}
    if(ReferenceStage==4 && T>30)
    {GetPawn()->SetActorLocation(FVector(1360,-450,100.75f));SetControlRotation((FVector(1000,-270,130)-FVector(1360,-450,170)).Rotation());ReferenceStage=5;}
    if(ReferenceStage==5 && T>34){FScreenshotRequest::RequestScreenshot(TEXT("reference_")+Phase+TEXT("_hero.png"),true,false);ReferenceStage=6;}
    if (T>36) FGenericPlatformMisc::RequestExit(false);
#endif
}

#include "BunkerReferenceCabinet.h"
#include "BunkerObservedAction.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/GameStateBase.h"
#include "Components/CapsuleComponent.h"
#include "EngineUtils.h"

void ABunkerPlayerController::ServerReferenceStep_Implementation(int32 Step)
{
#if !UE_BUILD_SHIPPING
    if (!FParse::Param(FCommandLine::Get(),TEXT("C13PhysicalTest"))) return;
    TActorIterator<ABunkerReferenceCabinet> BoxIt(GetWorld());ABunkerReferenceCabinet* Box=BoxIt?*BoxIt:nullptr;
    auto* PS=GetPlayerState<ABunkerPlayerState>();if(!Box || !PS || !GetPawn())return;
    const bool Host=IsLocalController();
    if(Step==0)
    {
        GetPawn()->SetActorLocation(FVector(Host?1475:1375,-310,100.75f));PS->Water=40;PS->Food=40;
        if(Host)
        {
            Box->Contents.Empty();Box->Revision=0;Box->bDoorOpen=false;Box->DoorAngle=0;
            for(int I=0;I<2;I++)
            {
                FBunkerInventoryEntry E;E.Id=FGuid(0xC1300022,0,0,I+1);E.ItemType=I==0?TEXT("Water"):TEXT("Food");E.Name=I==0?TEXT("Água de teste"):TEXT("Lata de teste");E.StorageSlot=6+I;E.WeightKg=PS->Rules->Find(E.ItemType)->WeightKg;
                E.WorldMesh=LoadObject<UStaticMesh>(nullptr,*(TEXT("/Game/Bunker/Items/")+E.ItemType.ToString()+TEXT("/SM_Item_")+E.ItemType.ToString()+TEXT(".SM_Item_")+E.ItemType.ToString()));Box->Contents.Add(E);
            }
        }
    }
    if(Step==1) GetPawn()->SetActorLocation(FVector(Host?1475:1375,-310,100.75f));
    if(Step==5) GetPawn()->SetActorLocation(FVector(Host?1475:1375,Host?-225:-245,100.75f));
    if(Step==0 || Step==1 || Step==3 || Step==5)
    {
        FVector Eye;FRotator R;GetPawn()->GetActorEyesViewPoint(Eye,R);
        FVector P=Step==3?Box->ItemPoint(7):Box->ItemPoint(6);
        if(Step==1)P=Box->DoorCollision->GetComponentLocation();
        auto* Character=Cast<ACharacter>(GetPawn());
        for(int Iteration=0;Iteration<3;Iteration++){FMinimalViewInfo V;Character->CalcCamera(0,V);SetControlRotation((P-V.Location).Rotation());Character->SetActorRotation(FRotator(0,GetControlRotation().Yaw,0));}
        ClientSetRotation(GetControlRotation(),true);
        FMinimalViewInfo V;Character->CalcCamera(0,V);FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(ReferenceAim),false,Character);GetWorld()->LineTraceSingleByChannel(Hit,V.Location,V.Location+GetControlRotation().Vector()*350,ECC_Visibility,Q);
        UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_AIM step=%d host=%d hit=%s component=%s target=%s camera=%s"),Step,Host,*GetNameSafe(Hit.GetActor()),*GetNameSafe(Hit.GetComponent()),*P.ToString(),*V.Location.ToString());
    }
    if(Step==2 && Host)
    {
        const FGuid Id(0xC1300022,0,0,1);int Count=0;for(auto& E:Box->Contents)Count+=E.Id==Id;
        int Players=0;for(TActorIterator<ABunkerPlayerState> It(GetWorld());It;++It){Players++;for(auto& E:It->Inventory)Count+=E.Id==Id;}
        UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_AUDIT players=%d ownership=%d contents=%d revision=%d open=%.1f"),Players,Count,Box->Contents.Num(),Box->Revision,Box->DoorAngle);
    }
    if(Step==7 && Host)
    {
        auto* C=Cast<ACharacter>(GetPawn());auto* Cap=C->GetCapsuleComponent();const float R=Cap->GetScaledCapsuleRadius(),H=Cap->GetScaledCapsuleHalfHeight();
        const FVector2D XY[]={FVector2D(1150,-680),FVector2D(1370,-610),FVector2D(1370,-300),FVector2D(1370,-220),FVector2D(1030,-170),FVector2D(780,-180),FVector2D(910,-260),FVector2D(910,-500),FVector2D(1150,-510),FVector2D(1150,-680)};
        FCollisionObjectQueryParams O;O.AddObjectTypesToQuery(ECC_WorldStatic);O.AddObjectTypesToQuery(ECC_WorldDynamic);FCollisionQueryParams Q(SCENE_QUERY_STAT(ReferenceCirculation),false,C);int Clear=0;
        for(int I=1;I<UE_ARRAY_COUNT(XY);I++) {FHitResult Hit;const bool Block=GetWorld()->SweepSingleByObjectType(Hit,FVector(XY[I-1],H+6),FVector(XY[I],H+6),FQuat::Identity,O,FCollisionShape::MakeCapsule(R,H),Q);if(!Block)Clear++;else UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_ROUTE_BLOCK segment=%d actor=%s"),I,*GetNameSafe(Hit.GetActor()));}
        UE_LOG(LogTemp,Display,TEXT("C13_REFERENCE_CIRCULATION clear=%d total=9 radius=%.2f halfHeight=%.2f"),Clear,R,H);
    }
    if(Step==6) ServerPhysicalTransfer(Box,6,FGuid(0xC1300022,0,0,1),0,true);
    if(Step==4)
    {
        const int Before=Box->Revision;ServerPhysicalTransfer(Box,6,FGuid(0xC1300022,0,0,1),Box->Revision,true);
        UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_CLOSED_REJECT pass=%d"),Before==Box->Revision && Box->DoorAngle<5);
    }
#endif
}
void ABunkerPlayerController::PhysicalProbeTick(float DT)
{
#if !UE_BUILD_SHIPPING
    auto* GS=GetWorld()->GetGameState();auto* PS=GetPlayerState<ABunkerPlayerState>();if(!GS || !PS)return;
    const float T=GS->GetServerWorldTimeSeconds();const bool Host=HasAuthority();
    if(!Host && T>45.5f) {FGenericPlatformMisc::RequestExit(false);return;}
    const float Times[]={5,12,14,15.5,17,19,21,23,25,27,29,31,33,34,37,39,40,44,46};
    if(PhysicalStage<UE_ARRAY_COUNT(Times) && T>Times[PhysicalStage]+(Host?0:.08f))
    {
        const int S=PhysicalStage++;
        if(S==0){ServerReferenceStep(0);ServerReferenceStep(7);}
        if(S==1 || S==7 || S==9)ServerReferenceStep(1);
        if(Host && (S==2 || S==4 || S==8 || S==10 || S==12 || S==15))ProbeKey(EKeys::E);
        if(!Host && S==4)ServerReferenceStep(6);
        if(S==3 || S==5 || S==11)ServerReferenceStep(5); // aim shelf; no fixture reset
        if(S==6)ProbeKey(EKeys::X);
        if(S==7 || S==14 || S==17)ServerReferenceStep(2);
        if(S==9)ServerReferenceStep(4);
        if(S==13 || S==16) {if(!PS->Inventory.IsEmpty()){SelectedItem=0;ProbeKey(EKeys::I);ProbeKey(EKeys::U);}}
        if(S==14)ServerReferenceStep(3);
        if(S==18)FGenericPlatformMisc::RequestExit(false);
        UE_LOG(LogTemp,Display,TEXT("C13_PHYSICAL_STAGE step=%d role=%s modal=%d lookFree=%d"),S,Host?TEXT("host"):TEXT("client"),bInventoryOpen,!IsLookInputIgnored());
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("C13ReferenceVideo")) && T>11 && T<45 && T>ReferenceNextFrame)
    {
        if(Host && !bReferenceAudio) {FApp::SetUnfocusedVolumeMultiplier(1.f);FApp::SetVolumeMultiplier(1.f);UAudioMixerBlueprintLibrary::StartRecordingOutput(this,36);bReferenceAudio=true;UE_LOG(LogTemp,Display,TEXT("C13_AUDIO_START time=%.5f"),T);}
        ReferenceNextFrame=T+.125f;
        const FString N=FString::Printf(TEXT("refvideo_%s_%05d.png"),Host?TEXT("host"):TEXT("client"),ReferenceVideoFrame++);
        FScreenshotRequest::RequestScreenshot(N,true,false);
        UE_LOG(LogTemp,Display,TEXT("C13_VIDEO_FRAME time=%.5f file=%s"),T,*N);
    }
    if(Host && bReferenceAudio && !bReferenceAudioEnded && T>45)
    {const FString Path=FPaths::ProjectSavedDir()/TEXT("C13ReferenceAudio");UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("refvideo_host"),Path);bReferenceAudioEnded=true;UE_LOG(LogTemp,Display,TEXT("C13_AUDIO_STOP time=%.5f path=%s"),T,*Path);}
    const double Now=FPlatformTime::Seconds();if(ReferenceWall && T>6 && T<11)ReferenceFrames.Add((Now-ReferenceWall)*1000);ReferenceWall=Now;
    if(PhysicalStage==18 && !ReferenceFrames.IsEmpty())
    {
        double Sum=0;for(double V:ReferenceFrames)Sum+=V;ReferenceFrames.Sort();
        UE_LOG(LogTemp,Display,TEXT("C13_TWO_PLAYER_FPS role=%s samples=%d fps=%.2f p95_ms=%.3f"),Host?TEXT("host"):TEXT("client"),ReferenceFrames.Num(),1000/(Sum/ReferenceFrames.Num()),ReferenceFrames[FMath::Min(ReferenceFrames.Num()-1,int(ReferenceFrames.Num()*.95))]);ReferenceFrames.Empty();
    }
#endif
}

#include "HAL/IConsoleManager.h"
void ABunkerPlayerController::ReferenceQualityTick()
{
    if(!IsLocalController() || !GetPawn())return;
    const FVector P=GetPawn()->GetActorLocation();const bool Inside=P.X>700 && P.X<1600 && P.Y>-730 && P.Y<-30 && P.Z<300;
    if(Inside==bReferenceQuality)return;
    auto* S=IConsoleManager::Get().FindConsoleVariable(TEXT("r.ShadowQuality"));auto* A=IConsoleManager::Get().FindConsoleVariable(TEXT("r.AmbientOcclusionLevels"));auto* R=IConsoleManager::Get().FindConsoleVariable(TEXT("r.Shadow.MaxResolution"));
    if(!S || !A || !R)return;
    if(Inside){ReferenceOldShadow=S->GetInt();ReferenceOldAO=A->GetInt();ReferenceOldShadowRes=R->GetInt();}
    S->Set(Inside?FMath::Max(2,ReferenceOldShadow):ReferenceOldShadow,ECVF_SetByConsole);
    A->Set(Inside?FMath::Max(1,ReferenceOldAO):ReferenceOldAO,ECVF_SetByConsole);
    R->Set(Inside?FMath::Max(512,ReferenceOldShadowRes):ReferenceOldShadowRes,ECVF_SetByConsole);
    bReferenceQuality=Inside;
}

void ABunkerPlayerController::RestoreReferenceQuality()
{
    if(!bReferenceQuality)return;
    const TCHAR* Names[]={TEXT("r.ShadowQuality"),TEXT("r.AmbientOcclusionLevels"),TEXT("r.Shadow.MaxResolution")};
    const int32 Values[]={ReferenceOldShadow,ReferenceOldAO,ReferenceOldShadowRes};
    for(int I=0;I<3;I++)if(auto* V=IConsoleManager::Get().FindConsoleVariable(Names[I]))V->Set(Values[I],ECVF_SetByConsole);
    bReferenceQuality=false;
}
