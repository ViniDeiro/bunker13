#!/bin/zsh
set -eu
export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
export TOOLCHAINS="${TOOLCHAINS:-com.apple.dt.toolchain.Metal.32023.883}"
C13_STUDY_ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
C13_STUDY_ENGINE="${C13_UNREAL_ROOT:-/Users/Shared/Epic Games/UE_5.8}"
exec "$C13_STUDY_ENGINE/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$C13_STUDY_ROOT/unreal/Condominio13/Condominio13.uproject" /Game/Bunker/BedroomVisual/Lvl_Bedroom_Study_Rest_Visual -game -C13DoorVisual -windowed -ResX=960 -ResY=540 -ForceRes '-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 85,r.ShadowQuality 2,r.Shadow.MaxResolution 512,r.AmbientOcclusionLevels 1'
