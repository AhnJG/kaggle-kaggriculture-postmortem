#!/usr/bin/env python3
"""Build the exact embedded submission from the public Shop Router notebook."""

from __future__ import annotations

import argparse
import ast
import base64
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


NOTEBOOK_SHA256 = "a36029e34448e823b6b11990ad06a86e255da6b629cbfb30035b542422592dd4"
EXPECTED_HASHES = {
    "main.py": "d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b",
    "actions.json": "17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef",
    "LICENSE.txt": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}
MAIN_CELL_ID = "f88df406"
DATA_CELL_ID = "fbd55715"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cell_source(notebook: dict, cell_id: str) -> str:
    for cell in notebook["cells"]:
        if cell.get("id") == cell_id:
            source = cell["source"]
            return "".join(source) if isinstance(source, list) else source
    raise ValueError(f"missing notebook cell {cell_id}")


def extract_payload(source: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "data_payload":
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                return value
    raise ValueError("data_payload string not found")


def build(notebook_path: Path, output_dir: Path) -> dict:
    notebook_bytes = notebook_path.read_bytes()
    actual_notebook_sha = sha256(notebook_bytes)
    if actual_notebook_sha != NOTEBOOK_SHA256:
        raise ValueError(
            f"notebook SHA mismatch: {actual_notebook_sha} != {NOTEBOOK_SHA256}"
        )
    notebook = json.loads(notebook_bytes)

    main_cell = cell_source(notebook, MAIN_CELL_ID)
    marker = "%%writefile main.py\n"
    if not main_cell.startswith(marker):
        raise ValueError("main.py cell marker changed")
    files: dict[str, bytes] = {"main.py": main_cell[len(marker) :].encode("utf-8")}

    payload = extract_payload(cell_source(notebook, DATA_CELL_ID))
    decoded = json.loads(gzip.decompress(base64.b64decode(payload)))
    if set(decoded) != {"actions.json", "LICENSE.txt"}:
        raise ValueError(f"unexpected embedded files: {sorted(decoded)}")
    files.update({name: content.encode("utf-8") for name, content in decoded.items()})

    actual_hashes = {name: sha256(files[name]) for name in EXPECTED_HASHES}
    if actual_hashes != EXPECTED_HASHES:
        raise ValueError(f"member SHA mismatch: {actual_hashes}")

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in EXPECTED_HASHES:
        (output_dir / name).write_bytes(files[name])

    archive_data = io.BytesIO()
    with tarfile.open(fileobj=archive_data, mode="w") as archive:
        for name in EXPECTED_HASHES:
            data = files[name]
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(data), 0o644, 0
            archive.addfile(member, io.BytesIO(data))
    submission = gzip.compress(archive_data.getvalue(), mtime=0)
    (output_dir / "submission.tar.gz").write_bytes(submission)

    manifest = {
        "candidate_id": "public-yhay81-shop-router-0909-exact",
        "purpose": "Exact public-code baseline reproduction; no strategy changes.",
        "source": {
            "notebook": str(notebook_path),
            "notebook_sha256": actual_notebook_sha,
            "author": "Yusuke Hayashi",
            "title": "Shop Router 0909 Python",
            "upstream_attribution": "aurax7 Kaggriculture Reactive Router",
        },
        "artifact": {
            "file": str(output_dir / "submission.tar.gz"),
            "sha256": sha256(submission),
            "bytes": len(submission),
            "members": actual_hashes,
        },
        "evidence_boundary": (
            "The public author's live leaderboard rating does not prove that this exact "
            "embedded artifact produced that rating; this submission measures that link."
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.notebook, args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
