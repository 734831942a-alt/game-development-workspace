#!/bin/zsh
set -euo pipefail
task_root="$(cd -- "$(dirname -- "$0")/../../.." && pwd)"
task_exe="$task_root/frostmoon/mod/tools/test-app/SlayTheSpire2.app/Contents/MacOS/Slay the Spire 2"
if [[ ! -x "$task_exe" ]]; then
  print '找不到本机独立试玩副本。请按使用说明将安装包中的 mods 文件夹安装到游戏目录。'
  read -r '?按回车关闭。'
  exit 1
fi
print '启动霜月独立试玩。请保持 Steam 运行。'
print '推荐：主菜单 → Mod 设置 → 霜月 → 起始牌组选择 1，然后开始新的单人对局并选择霜月。'
print '测试存档位于 FrostmoonIsolatedPlaytest；该入口使用本地存档。'
cd "$(dirname -- "$task_exe")"
exec "$task_exe" --frostmoon-test
