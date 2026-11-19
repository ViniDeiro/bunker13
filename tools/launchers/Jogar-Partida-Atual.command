#!/bin/zsh
set -eu
export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
export TOOLCHAINS="${TOOLCHAINS:-com.apple.dt.toolchain.Metal.32023.883}"
C13_STUDY_ROOT="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
C13_STUDY_ENGINE="${C13_UNREAL_ROOT:-/Users/Shared/Epic Games/UE_5.8}"
exec "$C13_STUDY_ENGINE/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$C13_STUDY_ROOT/unreal/Condominio13/Condominio13.uproject" /Game/Bunker/Lvl_CollectionRound -game -C13Round -C13Expedition -C13PlaytestNoSave -C13MainLobby -windowed -ResX=960 -ResY=540 -ForceRes '-ExecCmds=t.IdleWhenNotForeground 0,t.MaxFPS 30,r.BufferVisualizationOverviewTargets None,r.ScreenPercentage 70,r.ShadowQuality 0,r.AmbientOcclusionLevels 0'
