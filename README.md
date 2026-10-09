# 游戏开发工作区：霜月 Mod 与 UE5.5 战斗工程

本仓库独立保存当前游戏开发成果：原创「霜月 Frostmoon」Mod、角色与卡牌美术、卡池研究与设计文档，以及 Unreal Melee Combat System 的 UE5.5 迁移修改。

## 霜月 Frostmoon v0.2.2

面向《杀戮尖塔 2》v0.107.1 的原创角色 Mod，已在 macOS Apple Silicon 的真实游戏中构建、加载和进行本地单人测试。包含冰、月、血月三形态，64 张主卡、2 张衍生牌及独立插画。

- [使用说明与构建方式](frostmoon/mod/README.md)
- [Mod 源码](frostmoon/mod/src/)、[原创资源](frostmoon/mod/assets/)与[美术原图、提示词](frostmoon/mod/art/)
- [研究与设计资料](frostmoon/README.md)
- [设计工作簿和说明文档](outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0/)

安装包、源码 ZIP 和离线卡册作为 GitHub Releases 附件保存，不重复放进 Git 文件历史。生成卡册所需的源码、美术资源和脚本均保留在仓库中。

## Unreal Melee Combat System — UE5.5 迁移

目标：将 [georgehuan1994/Unreal-Melee-Combat-System](https://github.com/georgehuan1994/Unreal-Melee-Combat-System) 的 UE5.1 工程迁移至本机 UE5.5.4（Mac / Apple Silicon）。

当前结果：基础适配与蓝图编译通过，游戏模式启动测试通过，图形编辑器已打开。原仓库缺少部分地牢贴图，画面仍有默认材质。详见 [迁移检查记录](docs/UE5.5迁移检查记录.md)。

## 目录

- `upstream/Unreal-Melee-Combat-System/`：固定版本的原始文件，不在这里升级或编辑。
- `projects/MeleeCombatSystem-UE5.5/`：完整校验后生成的迁移工作副本。
- `artifacts/`：文件清单、下载版本信息、临时检查日志。
- `ue-migration/`：本次迁移修改的 4 个文件及校验清单，用于在原始快照上恢复适配结果。
- `tools/`：可恢复下载、文件校验和 UE 编译检查脚本。
- `打开战斗工程.command`：完整工作副本准备好后，双击通过本机 UE5.5 打开。

## 固定上游版本

`dde95ebb68d2b355428acfbca0137ccc7080dd58`

下载不依赖 Git LFS；逐文件核对原始字节数和 Git blob SHA-1。因为网络连接不稳定，文件通过 GitHub 官方下载入口获取，而非完整 Git 历史克隆。

## 本地检查

先运行 `python3 tools/fetch_upstream.py` 补齐文件，再运行 `python3 tools/prepare_project.py` 创建独立副本。准备脚本会拒绝不完整的输入，也不会覆盖已有工作副本。随后按 [迁移文件说明](ue-migration/README.md) 应用已保存的适配文件。

本次采用 `python3 tools/prepare_project.py --combat-only`：网络连接反复超时，原始快照中未使用的 UE5 Manny／Quinn 模板资源未全部下载完成，因此工作副本排除 `Content/Characters/Mannequins/` 和两个 UE4↔UE5 模板重定向资产。仍严格校验所有纳入工作副本的文件。战斗系统使用的 UE4 骨架、骑士角色、动作和主地牢不属于这个排除范围。完整排除清单在 `artifacts/snapshot-verification.json`。

工作副本的引擎关联与插件配置调整完成后，运行 `bash tools/run_checks.sh` 编译项目蓝图并检查资产依赖。日志保存在工作副本的 `Saved/Migration/`。命令行检查不能证明画面、操作手感、全部战斗分支或打包版本均无问题。

原仓库的 MIT 声明保留在上游目录，工作副本会附带 `LICENSE-upstream.txt`。原 README 另外列出多项第三方美术资产；本工作区默认忽略原始素材及工作副本，避免误上传，公开作品前需另行确认素材授权。
