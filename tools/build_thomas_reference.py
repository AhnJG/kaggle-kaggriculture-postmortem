#!/usr/bin/env python3
"""Build a deterministic submission from Thomas Tschinkel's public notebook."""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import shutil
import tarfile
from pathlib import Path


NOTEBOOK_SHA256 = "7e3c99179e84dcbb79aed3d5e80b142b9c370ddbd9200c9400123c1f5368823c"
MAIN_SHA256 = "8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97"
MAIN_CELL_ID = "60e8c082-522e-474d-b5fb-9356dd891987"
SOURCE_URL = (
    "https://www.kaggle.com/code/thomastschinkel/"
    "kaggriculture-95-5-win-rate-via-replay-routing"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cell_source(notebook: dict, cell_id: str) -> str:
    for cell in notebook["cells"]:
        if cell.get("id") == cell_id:
            source = cell["source"]
            return "".join(source) if isinstance(source, list) else source
    raise ValueError(f"missing notebook cell {cell_id}")


def build(notebook_path: Path, metadata_path: Path, output_dir: Path) -> dict:
    notebook_bytes = notebook_path.read_bytes()
    notebook_sha = sha256(notebook_bytes)
    if notebook_sha != NOTEBOOK_SHA256:
        raise ValueError(f"notebook SHA mismatch: {notebook_sha} != {NOTEBOOK_SHA256}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected_ref = "thomastschinkel/kaggriculture-95-5-win-rate-via-replay-routing"
    if metadata.get("id") != expected_ref or metadata.get("is_private") is not False:
        raise ValueError("unexpected kernel metadata")

    notebook = json.loads(notebook_bytes)
    source = cell_source(notebook, MAIN_CELL_ID)
    marker = "%%writefile main.py\n"
    if not source.startswith(marker):
        raise ValueError("main.py cell marker changed")
    main_bytes = source[len(marker) :].encode("utf-8")
    main_sha = sha256(main_bytes)
    if main_sha != MAIN_SHA256:
        raise ValueError(f"main.py SHA mismatch: {main_sha} != {MAIN_SHA256}")
    ast.parse(main_bytes.decode("utf-8"), filename="main.py")

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "main.py").write_bytes(main_bytes)
    shutil.copyfile(notebook_path, output_dir / "source.ipynb")
    shutil.copyfile(metadata_path, output_dir / "source-metadata.json")

    archive_data = io.BytesIO()
    with tarfile.open(fileobj=archive_data, mode="w") as archive:
        member = tarfile.TarInfo("main.py")
        member.size, member.mode, member.mtime = len(main_bytes), 0o644, 0
        archive.addfile(member, io.BytesIO(main_bytes))
    submission = gzip.compress(archive_data.getvalue(), mtime=0)
    submission_path = output_dir / "submission.tar.gz"
    submission_path.write_bytes(submission)

    manifest = {
        "candidate_id": "public-thomas-replay-router-v2-exact",
        "purpose": "Exact public-source reproduction; no strategy changes.",
        "source": {
            "url": SOURCE_URL,
            "kaggle_ref": expected_ref,
            "kaggle_id": metadata["id_no"],
            "version": 2,
            "retrieved_on": "2026-09-11",
            "public": True,
            "author": "Thomas Tschinkel",
            "title": metadata["title"],
            "notebook_sha256": notebook_sha,
            "main_cell_id": MAIN_CELL_ID,
        },
        "license": {
            "spdx": "N/A",
            "basis": (
                "Competition Rules treat public Competition Code posted on Kaggle as "
                "licensed under an OSI-approved license without commercial-use restrictions; "
                "winner review remains required."
            ),
        },
        "artifact": {
            "file": str(submission_path),
            "sha256": sha256(submission),
            "bytes": len(submission),
            "members": {"main.py": main_sha},
        },
        "preflight": {"status": "PENDING"},
        "hosted_observation": {
            "sample": "first 50 public episodes in API order after submission",
            "success": "Wilson 95% lower bound of point score > 0.5",
            "failure": "Wilson 95% upper bound of point score < 0.5",
            "inconclusive": "otherwise",
        },
        "evidence_boundary": (
            "This reproduces the published source cell, not the author's submitted artifact. "
            "Notebook claims and the author's live rating remain COMMUNITY/HOSTED context, "
            "not proof for this tarball."
        ),
        "state_exception": (
            "BOARD.md and HOSTED_LEDGER.md were stale on 2026-09-11 and are outside Codex "
            "write ownership; direct user instruction authorized this build and conditional submit."
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.notebook, args.metadata, args.output_dir),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
