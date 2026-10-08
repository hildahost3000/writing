#!/usr/bin/env python3
"""Install the furigana dictionary (SudachiPy + sudachidict_core) into ./vendor.

    python3 setup_furigana.py            # install (does nothing if already installed)
    python3 setup_furigana.py --force    # reinstall

Uses pip when it works. Otherwise it downloads the exact wheels pinned in
requirements.txt straight from PyPI (standard library only) and checks their SHA-256.
Download is about 77 MB; it takes about 200 MB on disk. Needs Python 3.10+.
"""
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ = ROOT / "requirements.txt"


def pins():
    out = {}
    for line in REQ.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            name, _, ver = line.partition("==")
            out[name.strip()] = ver.strip()
    return out


def installed(target):
    return (target / "sudachipy").is_dir() and (target / "sudachidict_core").is_dir()


def works(target):
    """Load the dictionary in a fresh interpreter, exactly like the server will."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); from sudachipy import dictionary, tokenizer;"
            "t = dictionary.Dictionary().create(); print(len(t.tokenize('今日は晴れです', tokenizer.Tokenizer.SplitMode.B)))")
    return subprocess.run([sys.executable, "-c", code, str(target)], capture_output=True).returncode == 0


def try_pip(target):
    if subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True).returncode != 0:
        print("pip isn't available here, so downloading the wheels directly.")
        return False
    print("Installing with pip…")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--target", str(target), "--upgrade", "--no-input",
                        "--disable-pip-version-check", "--only-binary=:all:", "-r", str(REQ)])
    if r.returncode != 0:
        print("pip couldn't install it, so downloading the wheels directly.")
    return r.returncode == 0


def wheel_matches(filename):
    """Does this wheel run on this machine? (A small subset of what pip checks.)"""
    py, abi, plat = filename[:-4].split("-")[-3:]
    v = sys.version_info
    if plat == "any":
        return py.startswith("py3") or py.startswith("py2.py3")
    if not (abi == "abi3" and py.startswith("cp3") and int(py[2:]) <= v.major * 100 + v.minor) and abi != f"cp{v.major}{v.minor}":
        return False
    machine = platform.machine().lower()
    arch = {"x86_64": "x86_64", "amd64": "x86_64", "arm64": "arm64", "aarch64": "arm64"}.get(machine, machine)
    comps = plat.split(".")
    system = platform.system()
    if system == "Linux":
        want = "x86_64" if arch == "x86_64" else "aarch64"
        return any(c.startswith("manylinux") and c.endswith("_" + want) for c in comps)
    if system == "Darwin":
        return any(c.startswith("macosx") and (c.endswith("universal2") or c.endswith("_" + arch)) for c in comps)
    if system == "Windows":
        return ("win_arm64" if arch == "arm64" else "win_amd64") in comps
    return False


def download(target, pkg, ver):
    meta = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/{ver}/json", timeout=30))
    wheels = [u for u in meta["urls"] if u["packagetype"] == "bdist_wheel" and wheel_matches(u["filename"])]
    if not wheels:
        sys.exit(f"No {pkg} {ver} wheel matches this system ({platform.system()} {platform.machine()}, "
                 f"Python {sys.version_info.major}.{sys.version_info.minor}).\n"
                 "Try a standard Python 3.10+ with pip, or set up a virtualenv and run:  pip install --target vendor -r requirements.txt")
    w = wheels[0]
    print(f"  {w['filename']}  ({w['size'] // 1024} KB)")
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / w["filename"]
        urllib.request.urlretrieve(w["url"], dest)
        if hashlib.sha256(dest.read_bytes()).hexdigest() != w["digests"]["sha256"]:
            sys.exit(f"Checksum mismatch for {w['filename']}. Not installing it; try again.")
        with zipfile.ZipFile(dest) as z:
            z.extractall(target)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true", help="reinstall even if already present")
    ap.add_argument("--target", type=Path, default=ROOT / "vendor", help="install location (default: ./vendor)")
    args = ap.parse_args()
    target = args.target.resolve()

    if sys.version_info < (3, 10):
        sys.exit("Python 3.10 or newer is required for the furigana dictionary.")
    if installed(target) and not args.force:
        print(f"Already installed in {target}. (Use --force to reinstall.)")
        return
    for old in target.glob("sudachi*"):
        shutil.rmtree(old, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    if not try_pip(target):
        for pkg, ver in pins().items():
            print(f"Downloading {pkg} {ver} from PyPI…")
            download(target, pkg, ver)

    if works(target):
        print(f"\nFurigana is ready ({target}). Start the app with:  python3 server.py")
    else:
        sys.exit("\nInstalled, but the dictionary failed to load. Run again with --force, or see the README's troubleshooting section.")


if __name__ == "__main__":
    main()
