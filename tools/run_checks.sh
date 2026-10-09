#!/bin/bash
set -euo pipefail
task_root="$(cd "$(dirname "$0")/.." && pwd)"
project_dir="$task_root/projects/MeleeCombatSystem-UE5.5"
engine_cmd="/Users/Shared/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor-Cmd"
project_file="$project_dir/MeleeCombatSystem.uproject"
test -f "$project_file"
mkdir -p "$project_dir/Saved/Migration"
"$engine_cmd" "$project_file" -run=CompileAllBlueprints -AllowListFile=BlueprintAllowList.txt -unattended -nullrhi -nosound -nop4 -abslog="$project_dir/Saved/Migration/compile-blueprints.log" > "$project_dir/Saved/Migration/compile-blueprints-console.log" 2>&1
"$engine_cmd" "$project_file" -run=pythonscript -script="$task_root/tools/inspect_project.py" -unattended -nullrhi -nosound -nop4 -abslog="$project_dir/Saved/Migration/asset-audit.log" > "$project_dir/Saved/Migration/asset-audit-console.log" 2>&1
printf 'Blueprint compilation and asset audit completed. Logs: %s\n' "$project_dir/Saved/Migration"
