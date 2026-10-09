"""Run with UE5.5 -run=pythonscript -script=<this file>."""
import json
from pathlib import Path
import unreal

project = Path(unreal.Paths.project_dir())
out = project / "Saved" / "Migration"
out.mkdir(parents=True, exist_ok=True)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
assets = registry.get_assets_by_path("/Game", recursive=True)
report = {"engine": unreal.SystemLibrary.get_engine_version(), "asset_count": len(assets), "missing_game_dependencies": {}, "maps": [], "inputs": []}
options = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True, include_searchable_names=False, include_soft_management_references=False, include_hard_management_references=False)
packages = {str(a.package_name) for a in assets}
for package in sorted(packages):
    missing = [str(d) for d in registry.get_dependencies(package, options) if str(d).startswith("/Game/") and str(d) not in packages]
    if missing:
        report["missing_game_dependencies"][package] = missing
for asset in assets:
    cls = str(asset.asset_class_path.asset_name)
    path = str(asset.package_name)
    if cls == "World":
        report["maps"].append(path)
    if cls == "InputMappingContext":
        obj = asset.get_asset()
        if obj:
            for mapping in obj.get_editor_property("mappings"):
                report["inputs"].append({"context": path, "action": mapping.action.get_name() if mapping.action else None, "key": str(unreal.InputLibrary.key_get_display_name(mapping.key, False))})
(out / "asset-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
unreal.log("MIGRATION_AUDIT " + json.dumps({"assets": len(assets), "packages_with_missing_dependencies": len(report["missing_game_dependencies"]), "maps": report["maps"]}))
