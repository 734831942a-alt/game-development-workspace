# UE5.5 迁移修改

此目录保存相对固定上游版本 `dde95ebb68d2b355428acfbca0137ccc7080dd58` 的全部 4 个已修改文件：工程配置、引擎配置、敌人蓝图与击败提示 UI 蓝图。它们来自本机已通过基础检查的工作副本；原始素材另由下载工具取得。

`manifest.json` 记录上游 Git blob SHA-1、修改后 SHA-256 和文件大小。上游 MIT 许可证随目录保留。详细修改与验证范围见 [迁移检查记录](../docs/UE5.5迁移检查记录.md)。

## 恢复到新的工作副本

在仓库根目录运行下载和准备脚本，工作副本必须是新生成的上游副本：

```sh
python3 tools/fetch_upstream.py
python3 tools/prepare_project.py --combat-only
```

将本目录的 `MeleeCombatSystem.uproject`、`Config/DefaultEngine.ini` 和 `Content/` 下的两个 `.uasset` 按原相对路径复制到 `projects/MeleeCombatSystem-UE5.5/`，替换刚生成的原始文件。不要覆盖含有后续编辑的工作副本。

使用 UE5.5 打开工程，或运行 `bash tools/run_checks.sh` 重新进行蓝图编译和资产审计。原项目的第三方素材、引擎本体、缓存与日志未包含在此目录。
