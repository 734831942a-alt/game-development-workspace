# UE5.5.4 迁移检查记录

检查日期：2026-10-03。

## 结论

战斗工程已完成基础兼容性适配，95 个项目蓝图编译通过，DungeonMap 在无画面的游戏模式下完成 600 个模拟帧运行，图形编辑器已启动并打开工程。

这不是“全部内容完美移植”的结论：原仓库缺失地牢贴图和预烘焙光照数据；键鼠实战、完整 Boss 战、性能以及打包版本尚未验证。桌面界面控制工具返回未授予权限，因此没有通过屏幕操作进行人工试玩。

## 工程位置

- 工作副本：`projects/MeleeCombatSystem-UE5.5/MeleeCombatSystem.uproject`
- 双击入口：工作区根目录的 `打开战斗工程.command`
- 原始下载：`upstream/Unreal-Melee-Combat-System/`
- 检查日志：`projects/MeleeCombatSystem-UE5.5/Saved/Migration/`

本机引擎为 `/Users/Shared/Epic Games/UE_5.5`，实际版本 5.5.4（CL 40574608），Apple Silicon Mac，Xcode 27.0。没有替换或修改引擎源码。

## 下载与范围

上游：https://github.com/georgehuan1994/Unreal-Melee-Combat-System

固定版本：`dde95ebb68d2b355428acfbca0137ccc7080dd58`。

由于 GitHub 连接多次中断，最终使用官方文件入口获取快照，而非保留完整 Git 历史。工作副本纳入的 2,605 个源文件、1,279,978,285 字节均通过大小与 Git blob SHA-1 校验。

排除了 126 个可选文件：UE5 Manny/Quinn 模板目录及两份 UE4↔UE5 重定向资产，其中 16 个大文件未下载完成。扫描未发现战斗主目录对这些模板的引用。原始目录及未完成下载保留，不影响再次补齐；排除清单在 `artifacts/snapshot-verification.json`。实际战斗用的 UE4 骨架、骑士角色、动作、Boss 音频及地牢地图已纳入工作副本。

## 兼容性修复

1. 将工作副本引擎关联从 5.1 改为 5.5。
2. 禁用仓库未提供的 `SwitchLanguage`、`DidItHit`、`BlueprintGraphScreenshot`。核心碰撞蓝图使用 UE 原生球形检测；最终编译与加载没有报告对这些插件的依赖。
3. 启用引擎内置 `XRBase`，恢复素材示例角色引用的 `ResetOrientationAndPosition` 函数。
4. 修复 `WB_EnemyFelled` 与 `BP_HumanoidEnemy` 中旧版 GameViewportSubsystem 获取节点：从通用 `K2Node_GetSubsystem` 转换为 `K2Node_GetEngineSubsystem`。采用临时精确类重定向，让 UE 的 ResavePackages 仅保存这两个资产，再移除临时规则。玩家的 `K2Node_GetSubsystemFromPC` 不在此转换范围内。
5. 启用仅限编辑器的 PythonScriptPlugin，用于资产审计与键位导出。

没有修改攻击数值、AI 策略、地图布局或原工程的 24 FPS 固定步长设置。

## 验证结果

| 检查 | 结果 |
|---|---|
| 工作副本纳入文件完整性 | 全部通过哈希与大小校验 |
| 项目蓝图编译 | 95 个；0 编译错误、0 加载失败 |
| 编译警告 | 80 个，来自 10 个素材示例角色的旧输入映射 |
| 地牢游戏模式启动 | 成功，使用 BP_ThirdPersonGameMode |
| 无画面运行 | 600 个模拟帧，正常退出，未发现 Error / Accessed None |
| 图形编辑器 | 完成启动，原生 Metal 渲染初始化成功；工程留在编辑器中 |
| 地牢材质 | 部分失败，回退默认材质，原因是上游缺贴图 |
| 键鼠实战、手感、完整 Boss 战 | 未验证 |
| 独立打包及 Windows 兼容性 | 未验证 |

对应证据文件：

- `Saved/Migration/compile-blueprints.log`
- `Saved/Migration/upgrade-viewport-nodes.log`
- `Saved/Migration/asset-audit.json`
- `Saved/Migration/runtime-smoke.log`
- `Saved/Migration/editor-open.log`

早期 `artifacts/probe-*` 是下载未完成时的临时检查，曾因角色父类尚未下载而失败；最终结果以上面的工作副本日志为准。

## 原仓库仍存在的资源缺项

资产注册表报告 101 个资产包存在未解析的项目依赖，共 148 个不同路径，其中包括旧目录软引用、示例预览资源、光照缓存等。不能将它们全部等同于运行阻断错误。

其中明确影响画面的有 109 个 `FantasyDungeon/Textures/` 贴图路径。上游固定版本的文件清单中这个贴图目录没有文件，因此不是迁移或当前网络失败造成的。Metal 材质编译日志确认部分地牢材质回退到 Default Material。`DungeonMap_BuiltData` 也没有提供，预烘焙光照不能完整复现。

后续可用已获授权的环境包替换这些材质，或直接建立墨竹区灰盒场景继续使用战斗逻辑。恢复原作者地牢视觉需要另行取得其缺失资源。

## 实际键位

以下从当前工程 `IMC_Default` 导出，非通用魂游键位猜测。编辑器点 Play 后，先点击游戏视口获取输入焦点。

| 操作 | 按键 |
|---|---|
| 移动 | WASD / 方向键 |
| 视角 | 鼠标 |
| 进入/退出战斗（拔刀/收刀） | R |
| 轻攻击 | 鼠标左键 |
| 格挡 | 鼠标右键 |
| 翻滚 | 左 Shift |
| 锁定目标 | 鼠标中键 |
| 冲刺 | F |
| 使用物品 | E |
| 交互 | Q |
| 走/跑切换 | Tab |
| 跳跃 | 空格 |

原工程 `IA_HeavyAttack` 的映射键为 None，本次未擅自重新分配。动作是否能执行还受角色战斗状态、精力及动画状态限制。

## 文件保留与授权

保留原仓库 MIT 声明。上游 README 另列出多个第三方美术资源，MIT 并不自动覆盖它们。工作区 Git 忽略了原始素材、工作副本和缓存，没有向任何远程仓库上传文件。
