#include "BunkerNetwork.h"
#include "GameFramework/Character.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/Skeleton.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

void C13ExportBedroomRig(ABunkerPlayerController* PC)
{
#if !UE_BUILD_SHIPPING
 auto* C=Cast<ACharacter>(PC->GetPawn());if(!PC->HasAuthority()||!C||PC->GetWorld()->GetTimeSeconds()<2)return;
 auto* Mesh=C->GetMesh()->GetSkeletalMeshAsset();if(!Mesh)return;
 const auto& Ref=Mesh->GetRefSkeleton();const auto& Pose=Ref.GetRefBonePose();
 FString Out=FString::Printf(TEXT("{\"asset\":\"%s\",\"skeleton\":\"%s\",\"units\":\"cm\",\"bones\":["),*Mesh->GetPathName(),*Mesh->GetSkeleton()->GetPathName());
 for(int I=0;I<Pose.Num();I++)
 {
  const auto P=Pose[I].GetTranslation(),S=Pose[I].GetScale3D();const auto Q=Pose[I].GetRotation();
  Out+=FString::Printf(TEXT("%s{\"name\":\"%s\",\"parent\":%d,\"position\":[%.9f,%.9f,%.9f],\"rotation\":[%.9f,%.9f,%.9f,%.9f],\"scale\":[%.9f,%.9f,%.9f]}"),I?TEXT(","):TEXT(""),*Ref.GetBoneName(I).ToString(),Ref.GetParentIndex(I),P.X,P.Y,P.Z,Q.X,Q.Y,Q.Z,Q.W,S.X,S.Y,S.Z);
 }
 Out+=TEXT("]}");
 const FString Path=FPaths::ConvertRelativePathToFull(FPaths::ProjectDir()/TEXT("../../exports/bedroom_rest_rig.json"));
 const bool OK=FFileHelper::SaveStringToFile(Out,*Path);UE_LOG(LogTemp,Display,TEXT("C13_REST_RIG_EXPORT pass=%d bones=%d"),OK,Pose.Num());FGenericPlatformMisc::RequestExit(false);
#endif
}
