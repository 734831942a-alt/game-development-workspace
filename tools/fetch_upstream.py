"""Fetch the pinned public upstream snapshot and verify each Git blob hash."""
import concurrent.futures
import hashlib
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / "upstream" / "Unreal-Melee-Combat-System"
COMMIT = "dde95ebb68d2b355428acfbca0137ccc7080dd58"
TREE = json.loads((ROOT / "artifacts" / "upstream-tree.json").read_text())
METADATA = json.loads((ROOT / "artifacts" / "upstream-commit.json").read_text())
assert METADATA["sha"] == COMMIT
assert TREE["sha"] in (COMMIT, METADATA["commit"]["tree"]["sha"]) and TREE.get("truncated") is False
FILES = sorted([item for item in TREE["tree"] if item["type"] == "blob"], key=lambda item: item["size"])

def fetch(item):
    relative = pathlib.PurePosixPath(item["path"])
    assert not relative.is_absolute() and ".." not in relative.parts
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and valid(target, item):
        return item["size"]
    temporary = target.with_name(target.name + ".partial")
    remotes = ["https://raw.githubusercontent.com/georgehuan1994/Unreal-Melee-Combat-System/" + COMMIT + "/" + item["path"], "https://github.com/georgehuan1994/Unreal-Melee-Combat-System/raw/" + COMMIT + "/" + item["path"]]
    for attempt in range(3):
        result = subprocess.run(["curl", "-fsSL", "--connect-timeout", "15", "--max-time", "300", "--speed-limit", "1024", "--speed-time", "20", remotes[attempt % 2], "-o", str(temporary)], capture_output=True)
        if result.returncode == 0 and valid(temporary, item):
            temporary.replace(target)
            return item["size"]
        time.sleep(attempt + 1)
    raise RuntimeError("Failed download or hash verification: " + item["path"] + " " + result.stderr.decode(errors="replace").strip())

def valid(path, item):
    data = path.read_bytes()
    return len(data) == item["size"] and hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == item["sha"]

if __name__ == "__main__":
    count = 0
    size = 0
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, item): item for item in FILES}
        for future in concurrent.futures.as_completed(futures):
            try:
                size += future.result()
                count += 1
                if count % 100 == 0 or count == len(FILES):
                    print(f"Verified {count}/{len(FILES)} files, {size / 1048576:.1f} MiB", flush=True)
            except Exception as error:
                failures.append(str(error))
                print(str(error), flush=True)
    if failures:
        raise SystemExit(f"{len(failures)} downloads failed; rerun to resume")
    print("Pinned upstream snapshot fully downloaded and hash-verified: " + COMMIT, flush=True)
