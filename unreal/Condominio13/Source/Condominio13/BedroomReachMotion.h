#pragma once
#include "CoreMinimal.h"

// Cosmetic timeline shared by the owner and observers; never moves inventory entries.
namespace BedroomReachMotion
{
inline FVector Position(const FVector& Rest,const FVector& Contact,float T,bool Place)
{
 if(Place)return T<.88f?FMath::Lerp(Rest,Contact,FMath::SmoothStep(0.f,.72f,T)):FMath::Lerp(Contact,Rest,FMath::SmoothStep(.88f,1.f,T));
 return T<.34f?FMath::Lerp(Rest,Contact,FMath::SmoothStep(0.f,.25f,T)):FMath::Lerp(Contact,Rest,FMath::SmoothStep(.34f,1.f,T));
}
// During pickup the item waits at the shelf while the empty hands approach.
inline FVector ItemPosition(const FVector& Rest,const FVector& Contact,float T,bool Place)
{return !Place && T<.34f?Contact:Position(Rest,Contact,T,Place);}
inline FQuat ItemRotation(const FQuat& Held,const FQuat& Shelf,float T,bool Place)
{return FQuat::Slerp(Held,Shelf,Place?FMath::SmoothStep(0.f,.72f,T):1-FMath::SmoothStep(.34f,1.f,T)).GetNormalized();}
inline bool ItemVisible(float T,bool Place){return Place?T<=.88f:T<=1.f;}
}
