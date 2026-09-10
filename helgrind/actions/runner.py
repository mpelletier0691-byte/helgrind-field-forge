"""Run privileged commands via pkexec."""
import os
import subprocess
from typing import Callable, Optional


def pkexec_run(script: str, log_cb: Optional[Callable[[str], None]] = None) -> int:
    env = {
        "DISPLAY": os.environ.get("DISPLAY", ":0"),
        "XAUTHORITY": os.environ.get("XAUTHORITY", os.path.expanduser("~/.Xauthority")),
        "HOME": os.environ.get("HOME", os.path.expanduser("~")),
    }
    cmd = ["pkexec", "env"] + [f"{k}={v}" for k, v in env.items()] + ["bash", script]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        if log_cb:
            log_cb(line.rstrip())
    return proc.wait()


def run_bash(script_body: str, log_cb: Optional[Callable[[str], None]] = None) -> int:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write("#!/bin/bash\nset -uo pipefail\n")
        f.write(script_body)
        path = f.name
    os.chmod(path, 0o755)
    try:
        return pkexec_run(path, log_cb)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
