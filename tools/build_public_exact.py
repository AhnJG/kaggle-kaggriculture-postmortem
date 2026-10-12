#!/usr/bin/env python3
"""Build deterministic, unmodified Kaggriculture submissions from public notebooks."""

from __future__ import annotations

import argparse
import ast
import base64
import gzip
import hashlib
import contextlib
import io
import json
import os
import re
import tarfile
import tempfile
from pathlib import Path


CANDIDATES = {
    "alperen": {
        "release_id": "public-alperen-before-dawn-stock-cash-sales-exact",
        "author": "alperen5252525",
        "title": "kaggriculture-before-dawn-stock-cash-sales",
        "notebook": "docs/code/alperen5252525_kaggriculture-before-dawn-stock-cash-sales.ipynb",
        "notebook_sha256": "d49b0540fe7ff082c4f5947563b0e433c62161cdf284638c08db103372f657de",
        "cell_id": "bb3f017679d9",
        "method": "decode SOURCE_B85 with base85+gzip, then reproduce the cell's GNU tar and gzip.compress(mtime=0)",
    },
    "lynnsakurai": {
        "release_id": "public-lynnsakurai-farming-score-v2-exact",
        "author": "lynnsakurai",
        "title": "farming-score-v2-a-better-approach",
        "notebook": "docs/code/lynnsakurai_farming-score-v2-a-better-approach.ipynb",
        "notebook_sha256": "f419b98e395cf1ab970bc8355257ac2c98a27f982739647886c881d69942ac12",
        "cell_id": "v49-cell-05",
        "archive_cell_id": "v49-cell-09",
        "method": "take the %%writefile main.py body verbatim, then reproduce the cell's GNU tar and GzipFile(mtime=0)",
    },
    "tetsutani": {
        "release_id": "public-tetsutani-market-smart-farming-exact",
        "author": "tetsutani",
        "title": "market-smart-farming-kaggriculture",
        "notebook": "docs/code/tetsutani_market-smart-farming-kaggriculture.ipynb",
        "notebook_sha256": "ac5bfab445488fe88589a06460a7509a7fb5aff1273c8b679bbcd04b5d6fd0d3",
        "cell_id": "6ed155d0",
        "archive_cell_id": "b3681d2d",
        "method": "decode the notebook's ARCHIVE_B64 verbatim and extract its main.py without modifying either artifact",
    },
    "p2-new": {
        "release_id": "public-lynnsakurai-farming-score-v2-latest-exact",
        "author": "lynnsakurai",
        "title": "farming-score-v2-a-better-approach",
        "notebook": "docs/collection_snapshots/farming-score-v2-a-better-approach/farming-score-v2-a-better-approach.ipynb",
        "notebook_sha256": "2fbebaf26ff26d47b606d7d80bf205331fd9374ac1ec549a8837fb32dba60d9e",
        "kernel_metadata": "docs/collection_snapshots/farming-score-v2-a-better-approach/kernel-metadata.json",
        "cell_id": "v49-cell-05",
        "archive_cell_id": "v49-cell-09",
        "method": "join the notebook's SOURCE_BYTES byte literals verbatim, then reproduce the cell's GNU tar and GzipFile(mtime=0)",
        "strict_expected_sha": True,
    },
    "p3-new": {
        "release_id": "public-tetsutani-market-smart-farming-latest-exact",
        "author": "tetsutani",
        "title": "market-smart-farming-kaggriculture",
        "notebook": "docs/collection_snapshots/market-smart-farming-kaggriculture/market-smart-farming-kaggriculture.ipynb",
        "notebook_sha256": "17d587525c226205467ac00a9b61eb7631fa1a4c73d6ef44a2f76b9e3e879201",
        "kernel_metadata": "docs/collection_snapshots/market-smart-farming-kaggriculture/kernel-metadata.json",
        "cell_id": "6ed155d0",
        "archive_cell_id": "b3681d2d",
        "method": "decode the notebook's ARCHIVE_B64 verbatim and extract its main.py without modifying either artifact",
        "strict_expected_sha": True,
    },
    "d1": {
        "release_id": "public-hesoponyo-pure-rl-agent-bc-ppo-self-play-exact",
        "author": "hesoponyo",
        "title": "pure-rl-agent-bc-ppo-self-play",
        "notebook": "docs/collection_snapshots/pure-rl-agent-bc-ppo-self-play/pure-rl-agent-bc-ppo-self-play.ipynb",
        "notebook_sha256": "d6afc8cd3ee39164432bc3e1dc198e25a4553099fc03c544b58dee3bfe33fea5",
        "kernel_metadata": "docs/collection_snapshots/pure-rl-agent-bc-ppo-self-play/kernel-metadata.json",
        "cell_id": "3c0ee859",
        "method": "take the %%writefile main.py body verbatim and place it in the common deterministic single-member archive",
        "source_notice": "No separate license notice was found in the extracted main.py.",
    },
    "d2": {
        "release_id": "public-salemali7-kaggriculture-2900-exact",
        "author": "salemali7",
        "title": "kaggriculture-2900",
        "notebook": "docs/collection_snapshots/kaggriculture-2900/kaggriculture-2900.ipynb",
        "notebook_sha256": "2acebbad45c10703e1587f6e57a964f571e2a9c2891d2ffdeea19ab03846b6cc",
        "kernel_metadata": "docs/collection_snapshots/kaggriculture-2900/kernel-metadata.json",
        "cell_index": 13,
        "archive_cell_index": 14,
        "method": "take the %%writefile main.py body verbatim, then reproduce the notebook's tarfile.open(mode='w') and GzipFile(mtime=0) archive",
        "source_notice": "No separate license notice was found in the extracted main.py.",
        "strict_expected_sha": True,
    },
    "d3": {
        "release_id": "public-aasim2003-notebookb3a3ef21c3-exact",
        "author": "aasim2003",
        "title": "notebookb3a3ef21c3",
        "notebook": "docs/collection_snapshots/notebookb3a3ef21c3/notebookb3a3ef21c3.ipynb",
        "notebook_sha256": "99e9c4f9bdc846d6a41fa6b4eb646878f1ff94184ee95a3c4f6f005efa665952",
        "kernel_metadata": "docs/collection_snapshots/notebookb3a3ef21c3/kernel-metadata.json",
        "cell_id": "16dd8c91-dd44-4fc6-93dc-892cff71196c",
        "method": "take the %%writefile main.py body verbatim and place it in the common deterministic single-member archive",
        "source_notice": "No separate license notice was found in the extracted main.py.",
    },
    "v1": {
        "release_id": "public-goodpjw2008-kaggriculture-melon-threshold-squeeze-2749-exact",
        "author": "goodpjw2008",
        "title": "kaggriculture-melon-threshold-squeeze-2749",
        "notebook": "docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/kaggriculture-melon-threshold-squeeze-2749.ipynb",
        "notebook_sha256": "ae34db0ef30bb7f858532ded3bbed229678c2db804f117d8fe5cdbad1e5d6eed",
        "kernel_metadata": "docs/collection_snapshots/kaggriculture-melon-threshold-squeeze-2749/kernel-metadata.json",
        "cell_id": "a1635dde-7dda-456e-a8ae-fa27b23b28bc",
        "archive_cell_id": "cf9d8605-e761-43b9-a074-87187bad5deb",
        "method": "take the %%writefile main.py body verbatim, then reproduce the notebook's tarfile.open('submission.tar.gz','w:gz') + tar.add('main.py') as a deterministic archive (PAX format, GzipFile mtime=0)",
        "expectation_kind": "printed_literal_no_assert",
        "strict_expected_sha": True,
    },
    "v2": {
        "release_id": "public-seyitkaangunes-kaggriculture-2820-score-exact",
        "author": "seyitkaangunes",
        "title": "kaggriculture-2820-score",
        "notebook": "docs/collection_snapshots/kaggriculture-2820-score/kaggriculture-2820-score.ipynb",
        "notebook_sha256": "09d9833a860b521db3083abd24a9abcd9a74404be81adf2b0ae096a01b6a3be4",
        "kernel_metadata": "docs/collection_snapshots/kaggriculture-2820-score/kernel-metadata.json",
        "cell_id": "cell-14",
        "archive_cell_id": "cell-14",
        "base_cell_id": "cell-04",
        "layer_cell_ids": ["cell-06", "cell-08", "cell-10", "cell-12"],
        "method": "execute the notebook's own base cell (cell-04) and build cell (cell-14) unmodified in an empty temp dir, emulating only %%writefile for the four layer cells with default settings; then reproduce the notebook's tarfile.open('submission.tar.gz','w:gz') as a deterministic archive (PAX format, GzipFile mtime=0)",
        "expectation_kind": "active_assert",
        "strict_expected_sha": True,
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cell_source(notebook: dict, cell_id: str) -> str:
    for cell in notebook["cells"]:
        if cell.get("id") == cell_id:
            source = cell.get("source", "")
            return "".join(source) if isinstance(source, list) else source
    raise ValueError(f"missing notebook cell {cell_id}")


def candidate_cell_source(notebook: dict, info: dict, prefix: str = "cell") -> str:
    index_key = f"{prefix}_index"
    id_key = f"{prefix}_id"
    if index_key in info:
        cell = notebook["cells"][info[index_key]]
        source = cell.get("source", "")
        return "".join(source) if isinstance(source, list) else source
    return cell_source(notebook, info[id_key])


def literal_assignment(source: str, name: str):
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(f"missing literal assignment {name}")


def joined_bytes_assignment(source: str, name: str) -> bytes:
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != name:
            continue
        call = node.value
        if (
            not isinstance(call, ast.Call)
            or call.keywords
            or len(call.args) != 1
            or not isinstance(call.func, ast.Attribute)
            or call.func.attr != "join"
            or ast.literal_eval(call.func.value) != b""
        ):
            raise ValueError(f"unexpected {name} construction")
        parts = ast.literal_eval(call.args[0])
        if not isinstance(parts, tuple) or not all(isinstance(part, bytes) for part in parts):
            raise ValueError(f"unexpected {name} byte parts")
        return b"".join(parts)
    raise ValueError(f"missing joined bytes assignment {name}")


def printed_expected_sha(source: str, label: str) -> str:
    """Return SHA literal from ``print(<label>, "<sha>")`` (a printed, non-asserting expectation)."""
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            and len(node.args) == 2
            and all(isinstance(arg, ast.Constant) and isinstance(arg.value, str) for arg in node.args)
            and node.args[0].value.replace(" ", "") == label
        ):
            return node.args[1].value
    raise ValueError(f"missing printed expectation {label!r}")


def writefile_cell(source: str) -> tuple[str, bytes]:
    """Emulate IPython ``%%writefile <path>``: file name from line 1, body = everything after it."""
    first, sep, body = source.partition("\n")
    if not sep or not first.startswith("%%writefile "):
        raise ValueError("cell is not a %%writefile cell")
    return first.split(None, 1)[1].strip(), body.encode("utf-8")


def run_v2_notebook_build(notebook: dict, info: dict, build_source: str, details: dict) -> bytes:
    """Run the notebook's own base + build cells unmodified; only %%writefile is emulated."""
    if os.path.isdir("/kaggle/working"):
        raise RuntimeError("/kaggle/working exists; refusing to run notebook cells against it")
    base_source = cell_source(notebook, info["base_cell_id"])
    layer_files: dict[str, str] = {}
    base_log, build_log = io.StringIO(), io.StringIO()
    previous_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            namespace: dict = {"__name__": "__main__"}  # one shared namespace, like a Jupyter kernel
            with contextlib.redirect_stdout(base_log):
                exec(compile(base_source, f"<notebook {info['base_cell_id']}>", "exec"), namespace)
            for cell_id in info["layer_cell_ids"]:
                name, body = writefile_cell(cell_source(notebook, cell_id))
                target = Path(name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                layer_files[name] = sha256(body)
            with contextlib.redirect_stdout(build_log):
                exec(compile(build_source, f"<notebook {info['cell_id']}>", "exec"), namespace)
            main_bytes = Path("main.py").read_bytes()
            scrub = lambda text: re.sub(
                r"(submission\.tar\.gz): [\d,]+ bytes",
                r"\1: <size of the notebook's own non-deterministic tar> bytes",
                text.replace(os.path.realpath(tmp), "<tmpdir>").replace(tmp, "<tmpdir>"),
            )
            base_text, build_text = scrub(base_log.getvalue()), scrub(build_log.getvalue())
        finally:
            os.chdir(previous_cwd)
    details["v2_build"] = {
        "base_cell_id": info["base_cell_id"],
        "layer_cell_ids": info["layer_cell_ids"],
        "build_cell_id": info["cell_id"],
        "notebook_defaults": {
            "USE_CADENCE": literal_assignment(build_source, "USE_CADENCE"),
            "EXTRA_LAYERS": literal_assignment(build_source, "EXTRA_LAYERS"),
            "VERIFY_LIVE_SHA": literal_assignment(build_source, "VERIFY_LIVE_SHA"),
        },
        "notebook_expected_sha256_by_use_cadence": {
            str(key): value for key, value in literal_assignment(build_source, "EXPECTED_SHA256").items()
        },
        "notebook_v44_base_sha256": literal_assignment(base_source, "V44_SHA256"),
        "writefile_layer_bodies_sha256": layer_files,
        "notebook_cell_stdout": {
            base_log_key: text.strip().splitlines()
            for base_log_key, text in (("base_cell", base_text), ("build_cell", build_text))
        },
        "note": "cells executed verbatim; USE_CADENCE/EXTRA_LAYERS/VERIFY_LIVE_SHA left at notebook defaults",
    }
    return main_bytes


def archive_main(
    main_bytes: bytes, *, gzip_file: bool, tar_format: int = tarfile.GNU_FORMAT
) -> bytes:
    buffer = io.BytesIO()
    if gzip_file:
        with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tar_format) as archive:
                member = tarfile.TarInfo("main.py")
                member.size = len(main_bytes)
                member.mode = 0o644
                member.mtime = 0
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                archive.addfile(member, io.BytesIO(main_bytes))
        return buffer.getvalue()

    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.GNU_FORMAT) as archive:
        member = tarfile.TarInfo("main.py")
        member.size = len(main_bytes)
        member.mtime = 0
        member.mode = 0o644
        archive.addfile(member, io.BytesIO(main_bytes))
    return gzip.compress(buffer.getvalue(), mtime=0)


def extract(
    candidate: str, notebook: dict, details: dict | None = None
) -> tuple[bytes, bytes, dict]:
    if details is None:
        details = {}
    info = CANDIDATES[candidate]
    source = candidate_cell_source(notebook, info)
    expected: dict[str, str] = {}

    if candidate == "alperen":
        main_bytes = gzip.decompress(base64.b85decode(literal_assignment(source, "SOURCE_B85")))
        expected["main.py"] = literal_assignment(source, "SOURCE_SHA256")
        archive_bytes = archive_main(main_bytes, gzip_file=False)
    elif candidate == "lynnsakurai":
        marker = "%%writefile main.py\n"
        if not source.startswith(marker):
            raise ValueError("lynnsakurai main.py cell marker changed")
        main_bytes = source[len(marker):].encode("utf-8")
        verify_source = cell_source(notebook, "v49-cell-07")
        expected["main.py"] = literal_assignment(verify_source, "EXPECTED_MAIN_SHA256")
        archive_bytes = archive_main(main_bytes, gzip_file=True)
    elif candidate == "p2-new":
        main_bytes = joined_bytes_assignment(source, "SOURCE_BYTES")
        expected["main.py"] = literal_assignment(source, "EXPECTED_MAIN_SHA256")
        archive_bytes = archive_main(main_bytes, gzip_file=True)
    elif candidate == "v1":
        marker = "%%writefile main.py\n"
        if not source.startswith(marker):
            raise ValueError("v1 main.py cell marker changed")
        main_bytes = source[len(marker):].encode("utf-8")
        archive_source = candidate_cell_source(notebook, info, "archive_cell")
        expected["main.py"] = printed_expected_sha(archive_source, "expected:")
        details["v1_build"] = {
            "expectation": "printed in build cell (print('expected      :', <sha>)); the notebook does not assert it",
            "archive_cell_id": info["archive_cell_id"],
        }
        archive_bytes = archive_main(main_bytes, gzip_file=True, tar_format=tarfile.PAX_FORMAT)
    elif candidate == "v2":
        main_bytes = run_v2_notebook_build(notebook, info, source, details)
        defaults = details["v2_build"]["notebook_defaults"]
        expected["main.py"] = literal_assignment(source, "EXPECTED_SHA256")[defaults["USE_CADENCE"]]
        archive_bytes = archive_main(main_bytes, gzip_file=True, tar_format=tarfile.PAX_FORMAT)
    elif candidate in {"d1", "d2", "d3"}:
        marker = "%%writefile main.py\n"
        if not source.startswith(marker):
            raise ValueError(f"{candidate} main.py cell marker changed")
        main_bytes = source[len(marker):].encode("utf-8")
        if candidate == "d2":
            archive_source = candidate_cell_source(notebook, info, "archive_cell")
            historical = literal_assignment(
                archive_source.replace("# expected_sha256 =", "expected_sha256 =", 1),
                "expected_sha256",
            )
            expected["main.py"] = historical
            archive_bytes = archive_main(
                main_bytes, gzip_file=True, tar_format=tarfile.PAX_FORMAT
            )
        else:
            archive_bytes = archive_main(main_bytes, gzip_file=True)
    else:
        archive_bytes = base64.b64decode(literal_assignment(source, "ARCHIVE_B64"))
        expected["submission.tar.gz"] = literal_assignment(source, "EXPECTED_ARCHIVE_SHA256")
        expected["main.py"] = literal_assignment(source, "EXPECTED_MAIN_SHA256")
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            main_bytes = archive.extractfile("main.py").read()

    ast.parse(main_bytes, filename="main.py")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        names = archive.getnames()
        if names != ["main.py"]:
            raise ValueError(f"unexpected archive members: {names}")
        if archive.extractfile("main.py").read() != main_bytes:
            raise ValueError("archived main.py differs from extracted notebook source")
    return main_bytes, archive_bytes, expected


def build(candidate: str, repo_root: Path, output_dir: Path) -> dict:
    info = CANDIDATES[candidate]
    notebook_path = repo_root / info["notebook"]
    notebook_bytes = notebook_path.read_bytes()
    notebook_sha = sha256(notebook_bytes)
    if notebook_sha != info["notebook_sha256"]:
        raise ValueError(
            f"notebook SHA mismatch: {notebook_sha} != {info['notebook_sha256']}"
        )
    notebook = json.loads(notebook_bytes)
    details: dict = {}
    main_bytes, archive_bytes, expected = extract(candidate, notebook, details)
    actual = {
        "main.py": sha256(main_bytes),
        "submission.tar.gz": sha256(archive_bytes),
    }
    expected_matches = {name: actual[name] == digest for name, digest in expected.items()}
    mismatches = [
        f"{name}: {actual[name]} != {expected[name]}"
        for name, matched in expected_matches.items()
        if not matched
    ]

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "main.py").write_bytes(main_bytes)
    (output_dir / "submission.tar.gz").write_bytes(archive_bytes)

    manifest = {
        "candidate_id": info["release_id"],
        "purpose": "Exact public notebook reproduction; no source changes.",
        "source": {
            "path": info["notebook"],
            "notebook_sha256": notebook_sha,
            "author": info["author"],
            "title": info["title"],
            "main_cell_id": (
                info["cell_id"] if "cell_id" in info else f"index:{info['cell_index']}"
            ),
            "archive_cell_id": (
                info["archive_cell_id"]
                if "archive_cell_id" in info
                else f"index:{info['archive_cell_index']}"
                if "archive_cell_index" in info
                else (info["cell_id"] if "cell_id" in info else f"index:{info['cell_index']}")
            ),
            "extraction_method": info["method"],
        },
        "artifact": {
            "file": "submission.tar.gz",
            "sha256": actual["submission.tar.gz"],
            "bytes": len(archive_bytes),
            "members": {"main.py": actual["main.py"]},
        },
        "notebook_expected_sha256": expected,
        "notebook_expected_matches": expected_matches,
        "license": {
            "archive_license_file": False,
            "source_notice": info.get(
                "source_notice",
                "The main.py source contains upstream license/attribution notices.",
            ),
            "decision": "Kaggle public notebook default; final license judgment deferred to Claude.",
        },
        "preflight": {
            "status": (
                "BLOCKED_SHA_MISMATCH"
                if info.get("strict_expected_sha") and mismatches
                else "PENDING"
            )
        },
    }
    if "expectation_kind" in info:
        manifest["expectation_kind"] = info["expectation_kind"]
    if details:
        manifest["build_details"] = details
        manifest["build_details"]["tar_normalization"] = (
            "notebook tarfile.open('submission.tar.gz','w:gz') stores filesystem mtime/uid/gid and a gzip header mtime; "
            "this builder stores the identical main.py bytes with mtime=0, uid=gid=0, mode 0644, PAX_FORMAT "
            "(Python>=3.8 default), GzipFile(filename='', mtime=0)"
        )
    if "kernel_metadata" in info:
        metadata_path = repo_root / info["kernel_metadata"]
        manifest["source"]["kernel_metadata"] = {
            "path": info["kernel_metadata"],
            "sha256": sha256(metadata_path.read_bytes()),
        }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if info.get("strict_expected_sha") and mismatches:
        raise ValueError(f"BLOCKED_SHA_MISMATCH: {', '.join(mismatches)}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", choices=sorted(CANDIDATES))
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifest = build(args.candidate, args.repo_root, args.output_dir)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
