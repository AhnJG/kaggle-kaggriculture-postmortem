import argparse
import json
import os
import tarfile
import io
import gzip
import hashlib
from pathlib import Path

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def archive_main(main_bytes: bytes, tar_format: int = tarfile.GNU_FORMAT) -> bytes:
    buffer = io.BytesIO()
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

def build(source_path: Path, output_dir: Path, title: str):
    main_bytes = source_path.read_bytes()
    archive_bytes = archive_main(main_bytes)
    
    actual_main = sha256(main_bytes)
    actual_tar = sha256(archive_bytes)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "main.py").write_bytes(main_bytes)
    (output_dir / "submission.tar.gz").write_bytes(archive_bytes)
    
    manifest = {
        "candidate_id": f"public-{title}-exact",
        "purpose": "Exact reproduction from extracted script.",
        "source": {
            "path": str(source_path),
            "title": title
        },
        "artifact": {
            "file": "submission.tar.gz",
            "sha256": actual_tar,
            "bytes": len(archive_bytes),
            "members": {"main.py": actual_main}
        },
        "preflight": {
            "status": "PENDING"
        }
    }
    
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("title", type=str)
    args = parser.parse_args()
    
    manifest = build(args.source_path, args.output_dir, args.title)
    print(f"Created {args.output_dir}/submission.tar.gz")
    print(f"SHA256: {manifest['artifact']['sha256']}")
