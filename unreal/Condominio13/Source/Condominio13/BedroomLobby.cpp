#include "BunkerNetwork.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"

namespace
{
struct FLobbyLayout
{
    float Scale, X, Y;
    FLobbyLayout(float W,float H): Scale(FMath::Min(W/960.f,H/540.f)), X((W-960*Scale)*.5f), Y((H-540*Scale)*.5f){}
    bool Button(float MouseX,float MouseY)const
    {
        const float U=(MouseX-X)/Scale,V=(MouseY-Y)/Scale;
        return U>=56&&U<=394&&V>=366&&V<=420;
    }
};
}

bool ABunkerHUD::IsLobbyButtonHovered() const
{
    if(!bLobbyInput||!PlayerOwner)return false;
    float MX,MY;int32 W,H;
    PlayerOwner->GetViewportSize(W,H);
    return W>0&&H>0&&PlayerOwner->GetMousePosition(MX,MY)&&FLobbyLayout(W,H).Button(MX,MY);
}

void ABunkerHUD::DrawLobby(ABunkerPlayerController& PC)
{
    const FLobbyLayout L(Canvas->ClipX,Canvas->ClipY);
    const FLinearColor Ink(.028f,.049f,.052f), Panel(.039f,.074f,.075f), Line(.13f,.24f,.23f);
    const FLinearColor Cream(.89f,.91f,.82f), Muted(.58f,.70f,.65f), Orange(.97f,.66f,.32f);
    auto Rect=[&](float X,float Y,float W,float H,const FLinearColor& C)
        {DrawRect(C,L.X+X*L.Scale,L.Y+Y*L.Scale,W*L.Scale,H*L.Scale);};
    auto Stroke=[&](float X,float Y,float XX,float YY,const FLinearColor& C,float Thickness=1)
        {DrawLine(L.X+X*L.Scale,L.Y+Y*L.Scale,L.X+XX*L.Scale,L.Y+YY*L.Scale,C,Thickness*L.Scale);};
    auto TextAt=[&](const TCHAR* Text,float X,float Y,float Size,const FLinearColor& C,bool Big=false)
        {DrawText(Text,C,L.X+X*L.Scale,L.Y+Y*L.Scale,Big?GEngine->GetLargeFont():GEngine->GetSmallFont(),Size*L.Scale,false);};
    DrawRect(Ink,0,0,Canvas->ClipX,Canvas->ClipY);
    Rect(474,0,486,540,Panel);
    for(int X=474;X<960;X+=24)Stroke(X,0,X,540,Line*.53f);
    for(int Y=12;Y<540;Y+=24)Stroke(474,Y,960,Y,Line*.53f);
    Stroke(474,0,474,540,Line);
    Rect(56,46,15,15,Orange);
    TextAt(TEXT("DEIROS DEV   /   DEFESA CIVIL"),83,45,1.25f,Muted);
    Stroke(56,78,418,78,Line);
    TextAt(TEXT("PROTOCOLO DE ABRIGO"),56,106,1.3f,Orange);
    TextAt(TEXT("CONDOMÍNIO"),53,142,2.28f,Cream,true);
    TextAt(TEXT("13"),48,184,4.3f,Cream,true);
    TextAt(TEXT("Os recursos são finitos."),56,275,1.55f,Cream);
    TextAt(TEXT("Decida o que levar. Volte antes que seja tarde."),56,300,1.25f,Muted);
    const bool Hover=IsLobbyButtonHovered();
    Rect(56,366,338,54,Hover?FLinearColor(1,.79f,.48f):Orange);
    TextAt(TEXT("COMEÇAR PARTIDA"),77,383,1.6f,Ink);
    TextAt(TEXT("→"),356,379,2.05f,Ink);
    TextAt(TEXT("ENTER  ·  PRÉVIA LOCAL"),56,439,1.12f,Muted);
    TextAt(TEXT("C13  /  SEÇÃO DO ABRIGO"),514,46,1.25f,Muted);
    TextAt(TEXT("01   SUPERFÍCIE"),518,111,1.15f,Cream);
    Stroke(515,139,904,139,Orange,2);
    Rect(652,115,109,24,Line);
    // Diagrammatic section, not a navigation map.
    Stroke(545,232,899,232,Muted,2);
    Stroke(545,232,545,392,Muted,2);
    Stroke(899,232,899,392,Muted,2);
    Stroke(545,392,899,392,Muted,2);
    Stroke(545,309,899,309,Line,2);
    Stroke(681,232,681,392,Line,2);
    Stroke(770,232,770,392,Line,2);
    for(int I=0;I<7;++I){Stroke(655+I*12,153+I*11,667+I*12,153+I*11,Orange,2);Stroke(667+I*12,153+I*11,667+I*12,164+I*11,Orange,2);}
    Rect(699,255,51,28,Orange);
    TextAt(TEXT("13"),712,258,1.37f,Ink);
    TextAt(TEXT("02   NÍVEL DO ABRIGO"),548,412,1.15f,Cream);
    Stroke(56,490,904,490,Line);
    TextAt(TEXT("VERSÃO DE TESTE"),56,506,1.05f,Muted);
    TextAt(TEXT("WASD  MOVER    /    E  INTERAGIR    /    I  MOCHILA"),552,506,1.05f,Muted);
}
