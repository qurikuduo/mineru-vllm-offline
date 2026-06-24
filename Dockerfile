# Use DaoCloud mirrored vllm image for China region for gpu with Volta、Turing、Ampere、Ada Lovelace、Hopper、Blackwell architecture (7.0 <= Compute Capability <= 12.1)
# The default base image uses vLLM 0.21.0 with CUDA 13.0. For CUDA 12.9 environments, switch to the commented cu129 image below.
# Compute Capability version query (https://developer.nvidia.com/cuda-gpus)
# support x86_64 architecture and ARM(AArch64) architecture
FROM vllm/vllm-openai:v0.20.0-cu130
# FROM docker.m.daocloud.io/vllm/vllm-openai:v0.21.0-cu129

# Install libgl for opencv support & Noto fonts for Chinese characters
RUN apt-get update && \
    apt-get install -y \
        fonts-noto-core \
        fonts-noto-cjk \
        fontconfig \
        libgl1 && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install mineru latest
RUN python3 -m pip install -U 'mineru[core]>=3.2.1' -i https://mirrors.aliyun.com/pypi/simple --break-system-packages && \
    python3 -m pip cache purge

# Patch mineru FastAPI app to serve Swagger UI / ReDoc from vendored assets
# (works in air-gapped LANs with no internet access).
COPY mineru_offline_docs.py /usr/local/lib/python3.12/dist-packages/mineru_offline_docs.py
ARG REDOC_JS_URL=https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js
RUN mkdir -p /usr/local/lib/python3.12/dist-packages/vllm/entrypoints/serve/instrumentator/static && \
    curl -fsSL -o /usr/local/lib/python3.12/dist-packages/vllm/entrypoints/serve/instrumentator/static/redoc.standalone.js "${REDOC_JS_URL}" && \
    python3 - <<'PY'
import pathlib
p = pathlib.Path("/usr/local/lib/python3.12/dist-packages/mineru/cli/fast_api.py")
src = p.read_text()
marker = "app = create_app()"
inject = """

# --- mineru offline docs patch (air-gapped /docs & /redoc) ---
from mineru_offline_docs import apply_offline_docs
apply_offline_docs(app)
"""
if "apply_offline_docs" in src:
    print("mineru offline docs patch: already applied, skipping")
else:
    assert marker in src, f"marker {marker!r} not found in {p}"
    p.write_text(src.replace(marker, marker + inject, 1))
    print("mineru offline docs patch: applied")
PY

# Download models and update the configuration file
RUN /bin/bash -c "mineru-models-download -s modelscope -m all"

# Set the entry point to activate the virtual environment and run the command line tool
ENTRYPOINT ["/bin/bash", "-c", "export MINERU_MODEL_SOURCE=local && exec \"$@\"", "--"]

