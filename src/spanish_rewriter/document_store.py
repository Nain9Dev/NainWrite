"""Local document-job persistence, atomic checkpoints and immutable outputs."""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import uuid


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def read_input(path):
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() not in {".md", ".txt"} or not path.is_file():
        raise ValueError("Only UTF-8 .md and .txt files are supported")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Input is not valid UTF-8") from error
    if not text.strip():
        raise ValueError("Input document is empty")
    return path, text, hashlib.sha256(raw).hexdigest()


def new_job_dir(source, output_dir=None):
    root = Path(output_dir).resolve() if output_dir else source.parent / (source.stem + ".rewritten")
    root.mkdir(parents=True, exist_ok=True)
    job = root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:10])
    job.mkdir()
    return job


def _atomic(path, content, *, replace):
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            for attempt in range(6):
                try:
                    os.replace(temporary, path)
                    break
                except PermissionError as error:
                    if getattr(error, "winerror", None) not in {5, 32, 33} or attempt == 5:
                        raise
                    time.sleep(0.05 * (2 ** attempt))
        else:
            # Linking the complete temporary file publishes atomically without clobbering.
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != content.encode("utf-8"):
                    raise ValueError(f"Existing artifact differs; will not overwrite {path.name}")
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def publish(job, name, content):
    if Path(name).name != name:
        raise ValueError("Artifact name must not contain a directory")
    _atomic(Path(job) / name, content, replace=False)


def _artifact_path(job, name):
    if not isinstance(name, str) or Path(name).name != name or (Path(job) / name).is_symlink():
        raise ValueError("Invalid job artifact path")
    return Path(job) / name


def verify_artifact(job, name, expected):
    """Verify an immutable artifact without silently recreating missing history."""
    if _artifact_path(job, name).read_bytes() != expected.encode("utf-8"):
        raise ValueError(f"Saved artifact differs: {name}")


def verify_artifact_hash(job, name, expected_hash):
    """Check immutable report bytes before an approval or resumed model call."""
    if hashlib.sha256(_artifact_path(job, name).read_bytes()).hexdigest() != expected_hash:
        raise ValueError(f"Saved report artifact differs: {name}")


def read_editable(job, name):
    """Read exact editable UTF-8 bytes through the local persistence boundary."""
    return read_input(_artifact_path(job, name))


def read_published_json(job, name):
    """Recover an atomically published record after an interrupted checkpoint save."""
    path = _artifact_path(job, name)
    try:
        raw = path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return None
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError('Published JSON record must be an object')
    return result


def initialize_editable(job, name, baseline):
    """Create the editable copy once, never replacing pre-existing user edits."""
    path = _artifact_path(job, name)
    if not path.exists():
        publish(job, name, baseline)


def save_state(job, state):
    envelope = {"sha256": digest(state), "state": state}
    _atomic(Path(job) / "checkpoint.json", canonical(envelope), replace=True)


def read_state(job):
    try:
        envelope = json.loads((Path(job) / "checkpoint.json").read_text(encoding="utf-8"))
        if digest(envelope["state"]) != envelope["sha256"]:
            raise ValueError("Checkpoint checksum mismatch")
        return envelope["state"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid checkpoint") from error


@contextmanager
def job_lock(job):
    with (Path(job) / "job.lock").open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("Another process is already running this document job") from error
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
