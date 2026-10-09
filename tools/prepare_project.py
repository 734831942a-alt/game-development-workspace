"""Verify the complete snapshot and copy it without changing upstream files."""
import json
import shutil
import sys
from pathlib import Path
from fetch_upstream import ROOT, DEST, COMMIT, FILES, valid

target = ROOT / "projects" / "MeleeCombatSystem-UE5.5"
combat_only = "--combat-only" in sys.argv
optional_prefix = "MeleeCombatSystem/Content/Characters/Mannequins/"
optional_rigs = {"MeleeCombatSystem/Content/Characters/Mannequin_UE4/Rigs/RTG_UE5Manny_UE4Manny.uasset", "MeleeCombatSystem/Content/Characters/Mannequin_UE4/Rigs/RTG_UE4Manny_UE5Manny.uasset"}
selected = [item for item in FILES if not combat_only or not (item["path"].startswith(optional_prefix) or item["path"] in optional_rigs)]
if target.exists():
    raise SystemExit("Working copy already exists; will not overwrite: " + str(target))
bad = [item["path"] for item in selected if not (DEST / item["path"]).is_file() or not valid(DEST / item["path"], item)]
if bad:
    raise SystemExit("Snapshot incomplete; missing/invalid: " + str(len(bad)) + "\n" + "\n".join(bad[:10]))
for item in selected:
    relative = Path(item["path"])
    if relative.parts[0] != "MeleeCombatSystem":
        continue
    destination = target.joinpath(*relative.parts[1:])
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEST / relative, destination)
shutil.copy2(DEST / "LICENSE", target / "LICENSE-upstream.txt")
shutil.copy2(DEST / "README.md", target / "README-upstream.md")
assets = sorted((target / "Content").rglob("*.uasset"))
object_paths = ["/Game/" + str(p.relative_to(target / "Content").with_suffix("")) + "." + p.stem for p in assets]
(target / "BlueprintAllowList.txt").write_text("\n".join(object_paths) + "\n")
(ROOT / "artifacts" / "snapshot-verification.json").write_text(json.dumps({"commit": COMMIT, "verified_files": len(selected), "verified_bytes": sum(f["size"] for f in selected), "working_copy": str(target), "excluded_optional_files": [item["path"] for item in FILES if item not in selected]}, indent=2))
print("Verified and copied " + str(len(selected)) + " files. Working copy: " + str(target))
