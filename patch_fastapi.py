#!/usr/bin/env python3

import pathlib
import shutil

FASTAPI_FILE = pathlib.Path(
    "/usr/local/lib/python3.12/dist-packages/mineru/cli/fast_api.py"
)

if not FASTAPI_FILE.exists():
    raise RuntimeError(f"{FASTAPI_FILE} not found")

src = FASTAPI_FILE.read_text(encoding="utf-8")

MARKER = "app = create_app()"

PATCH = """

# ----------------------------------------------------------------------
# Offline Swagger/ReDoc patch
# ----------------------------------------------------------------------
from mineru_offline_docs import apply_offline_docs
apply_offline_docs(app)
"""

if "apply_offline_docs(app)" not in src:

    if MARKER not in src:
        raise RuntimeError(f"Cannot find '{MARKER}'")

    src = src.replace(MARKER, MARKER + PATCH, 1)

    FASTAPI_FILE.write_text(src, encoding="utf-8")

    print("Patched fast_api.py")

else:

    print("Patch already exists.")

pycache = FASTAPI_FILE.parent / "__pycache__"

if pycache.exists():
    shutil.rmtree(pycache)

print("Done.")

