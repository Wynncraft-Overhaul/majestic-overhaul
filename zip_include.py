"""
Zips all files listed in manifest["include"]
"""
from __future__ import annotations

import hashlib
import json
import os
import zipfile


def md5(fname: str) -> str:
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


with open("manifest.json", "r") as f:
    manifest = json.load(f)

to_be_zipped: dict[str, list[str]] = {}
for include in manifest["include"]:
    location = include["location"]
    id = include.get("id", "default")
    if not to_be_zipped.get(id):
        to_be_zipped[id] = []
    if os.path.isdir(location):
        for path, dirs, files in os.walk(location):
            for file in files:
                to_be_zipped[id].append(f"{path}/{file}")
    else:
        to_be_zipped[id].append(location)

zips = []

for k, v in to_be_zipped.items():
    with zipfile.ZipFile(f"{k}.zip", "w") as _zip:
        for file in v:
            _zip.write(file, compress_type=zipfile.ZIP_DEFLATED)
    zips.append(f"{k}.zip")

hashes = {}

for zip in zips:
    hashes[zip] = md5(zip)


with open("hashes.json", "w") as f:
    json.dump(hashes, f)

print(*zips)
