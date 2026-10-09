#!/bin/zsh
set -eu
task_root="$(cd "$(dirname "$0")" && pwd)"
project_file="$task_root/projects/MeleeCombatSystem-UE5.5/MeleeCombatSystem.uproject"
engine_bin="/Users/Shared/Epic Games/UE_5.5/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
if [[ ! -f "$project_file" ]]; then
  print '完整工程尚未准备完成，请先查看迁移检查记录。'
  exit 1
fi
exec "$engine_bin" "$project_file"
