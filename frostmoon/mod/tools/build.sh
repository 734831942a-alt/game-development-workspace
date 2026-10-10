#!/bin/zsh
set -euo pipefail
task_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$task_root"
export DOTNET_CLI_HOME="$task_root/tools/dotnet-home"
export NUGET_PACKAGES="$task_root/tools/packages"
export DOTNET_CLI_TELEMETRY_OPTOUT=1
task_dotnet="$task_root/tools/dotnet/dotnet"
if [[ ! -x "$task_dotnet" ]]; then task_dotnet="$(command -v dotnet)"; fi
"$task_dotnet" build Frostmoon.csproj -c Release --nologo -v:minimal "$@"
"$task_dotnet" run --project tools/BuildPack -p:UseSharedCompilation=false -- assets dist/Frostmoon/Frostmoon.pck
cp bin/Release/net9.0/Frostmoon.dll dist/Frostmoon/Frostmoon.dll
cp Frostmoon.json dist/Frostmoon/Frostmoon.json
print '小木曾和纱 Mod 已生成至 dist/Frostmoon/'
