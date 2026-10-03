"""Provenance and reproducibility tracking."""

from __future__ import annotations
import hashlib, json, os, platform, subprocess, sys, time, uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _git_commit() -> str:
    try:
        r = subprocess.run(["git","rev-parse","HEAD"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class ProvenanceRecord:
    run_id: str
    problem_id: str
    git_commit: str
    timestamp_utc: str
    python_version: str
    os_info: str
    seed: int
    config_hash: str
    dependencies: dict = field(default_factory=dict)

    @classmethod
    def create(cls, problem_id: str, seed: int, config_path: Optional[Path] = None) -> "ProvenanceRecord":
        config_hash = _sha256(config_path) if config_path and config_path.exists() else "N/A"
        deps = {}
        for pkg in ["numpy","scipy","sympy","mpmath"]:
            try:
                deps[pkg] = __import__(pkg).__version__
            except ImportError:
                deps[pkg] = "NOT_INSTALLED"
        return cls(run_id=str(uuid.uuid4())[:12], problem_id=problem_id, git_commit=_git_commit(),
                   timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                   python_version=sys.version, os_info=platform.platform(), seed=seed,
                   config_hash=config_hash, dependencies=deps)

    def to_dict(self) -> dict:
        return {"run_id":self.run_id,"problem_id":self.problem_id,"git_commit":self.git_commit,
                "timestamp_utc":self.timestamp_utc,"python_version":self.python_version,
                "os_info":self.os_info,"seed":self.seed,"config_hash":self.config_hash,
                "dependencies":self.dependencies}

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2))


_MANIFEST_FILES = {"SHA256SUMS", "manifest.json"}


def build_sha256sums(directory: Path) -> dict[str, str]:
    """SHA-256 of every result file, excluding the manifest files that list them
    (otherwise the manifest would hash itself and never verify)."""
    return {str(f.relative_to(directory)): _sha256(f)
            for f in sorted(directory.rglob("*"))
            if f.is_file() and f.name not in _MANIFEST_FILES}
