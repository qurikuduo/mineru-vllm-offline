# mineru-vllm-offline

An offline-ready Docker image for the [`mineru`](https://github.com/opendatalab/MinerU) vLLM-backed document-conversion API. The image vendors the Swagger UI and ReDoc static assets, so `/docs` and `/redoc` work in **air-gapped (no-internet) environments** such as isolated LANs. Supports both **CUDA 13.0** (cu130) and **CUDA 12.4** (cu124) GPU architectures, and runs on both **Windows** and **Linux** hosts.

---

## Why this exists / 项目背景

### English

By default, `mineru-api` uses FastAPI's stock `get_swagger_ui_html`, whose generated HTML references CDN-hosted assets:

- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css`
- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
- `https://fastapi.tiangolo.com/img/favicon.png`

In an air-gapped LAN, none of these can be loaded and the `/docs` page is unusable. This project vendors the necessary assets into the image and overrides the default docs routes so everything is served from inside the container. The service has been offline-tested on both CUDA 13.0 and CUDA 12.4 environments.

### 中文

`mineru-api` 默认使用 FastAPI 自带的 `get_swagger_ui_html` 生成 Swagger UI 页面，HTML 中引用的 CSS / JS / favicon 全部托管在 CDN 上：

- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css`
- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
- `https://fastapi.tiangolo.com/img/favicon.png`

在物理隔离的局域网里这些资源都拉不到，`/docs` 页面就完全打不开。本项目把所需静态资源直接内嵌到镜像内，并替换默认的 docs 路由，使整个 API 文档完全离线可用。已在 CUDA 13.0 与 CUDA 12.4 两套环境下经过实际离线测试验证。

---

## What you get / 提供的功能

### English

- Self-contained `/docs` (Swagger UI) and `/redoc` pages served from inside the container — no internet required at runtime.
- Support for two GPU/CUDA generations:
  - **cu130** — for modern GPUs (Volta through Blackwell, Compute Capability 7.0–12.0), backed by vLLM v0.22.0 on CUDA 13.0.
  - **cu124** — for older GPUs (e.g. Tesla V100S, A10), backed by vLLM v0.11.2 on CUDA 12.4.
- Works on both **Windows** and **Linux** hosts via `docker compose up -d`.
- Idempotent build: rebuilding the image will not re-apply the patch twice.

### 中文

- `/docs`（Swagger UI）和 `/redoc` 页面完全由容器自身提供，运行时零外网依赖。
- 支持两套 GPU / CUDA 版本：
  - **cu130** — 适用于现代 GPU（Volta 至 Blackwell，算力 7.0–12.0），基于 CUDA 13.0 + vLLM v0.22.0。
  - **cu124** — 适用于老款 GPU（如 Tesla V100S、A10），基于 CUDA 12.4 + vLLM v0.11.2。
- **Windows 与 Linux** 均可通过 `docker compose up -d` 直接启动服务。
- 幂等构建：镜像重建时不会重复注入补丁。

---

## Quick start / 快速开始

### English

Prerequisites:

- Docker 24+ with the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed.
- The offline image built locally — see "Build the images" below.
- An NVIDIA GPU.

Once the image is built, start the service:

```bash
docker compose up -d
```

`docker-compose.yml` references `mineru:2.5-vllm-cu130-offline-docs` by default. Change the `image:` line if you built the cu124 variant instead.

Once healthy, open:

- API docs (Swagger UI): http://localhost:8000/docs
- API docs (ReDoc): http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

View logs / status:

```bash
docker compose logs -f mineru-api
docker compose ps
```

Stop:

```bash
docker compose down
```

### 中文

前置条件：

- Docker 24+，且已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)。
- 已在本地构建好离线镜像（见下文"构建镜像"）。
- 一块 NVIDIA GPU。

镜像构建完毕后，启动服务：

```bash
docker compose up -d
```

`docker-compose.yml` 默认引用 `mineru:2.5-vllm-cu130-offline-docs`。如果你构建的是 cu124 版本，请修改 `image:` 字段。

服务健康后，浏览器访问：

- API 文档（Swagger UI）：http://localhost:8000/docs
- API 文档（ReDoc）：http://localhost:8000/redoc
- OpenAPI schema：http://localhost:8000/openapi.json

查看日志 / 状态：

```bash
docker compose logs -f mineru-api
docker compose ps
```

停止服务：

```bash
docker compose down
```

---

## Build the images / 构建镜像

Each variant is built in two steps. Run both commands in order; the second image layers the offline docs patch on top of the first.

每个版本都分两步构建，必须按顺序执行；第二步在第一步产生的镜像上叠加离线 docs 补丁。

---

### CUDA 13.0 — cu130 (recommended / 推荐)

Suitable for: Volta, Turing, Ampere, Ada Lovelace, Hopper, Blackwell (Compute Capability 7.0–12.0)  
适用于：Volta、Turing、Ampere、Ada Lovelace、Hopper、Blackwell（算力 7.0–12.0）

```bash
docker build -f Dockerfile-offline-cu130-vllm220 -t mineru:2.5-vllm-cu130 .
docker build -f Dockerfile-offline-cu130-vllm220-offline-docs -t mineru:2.5-vllm-cu130-offline-docs .
```

The final image is `mineru:2.5-vllm-cu130-offline-docs` — this is what `docker-compose.yml` references by default.

最终镜像为 `mineru:2.5-vllm-cu130-offline-docs`，即 `docker-compose.yml` 默认引用的镜像。

---

### CUDA 12.4 — cu124 (older GPUs / 旧款 GPU)

Suitable for: Tesla V100S, A10, and other GPUs requiring CUDA 12.4  
适用于：Tesla V100S、A10 等需要 CUDA 12.4 的旧款 GPU

```bash
docker build -f Dockerfile-offline-cu124-vllm112 -t mineru:2.5-vllm-cu124 .
docker build -f Dockerfile-offline-cu124-vllm112-offline-docs -t mineru:2.5-vllm-cu124-offline-docs .
```

After building, update `docker-compose.yml` to use the cu124 image:

构建完成后，修改 `docker-compose.yml` 中的 `image:` 字段：

```yaml
image: mineru:2.5-vllm-cu124-offline-docs
```

Then start as usual / 然后照常启动：

```bash
docker compose up -d
```

---

## How the patch works / 补丁实现原理

### English

The `mineru` package builds its FastAPI app in `mineru/cli/fast_api.py` via `create_app()`. The default constructor registers `/docs`, `/redoc`, and `/docs/oauth2-redirect` routes whose HTML references external CDN URLs.

This project ships:

- `mineru_offline_docs.py` — exposes `apply_offline_docs(app)`, which mounts the vendored static assets from `/opt/mineru-static/` and re-registers the docs routes to point at them.
- `static/` — contains the vendored `swagger-ui-bundle.js`, `swagger-ui.css`, and `redoc.standalone.js`, copied directly into the image at build time (no download needed).
- `patch_fastapi.py` — a one-shot script run at image build time that injects `apply_offline_docs(app)` into `mineru/cli/fast_api.py` right after `app = create_app()`. The injection is guarded by an idempotency check.

The `-offline-docs` Dockerfile copies these files into the image and runs the patch:

```dockerfile
COPY mineru_offline_docs.py /usr/local/lib/python3.12/dist-packages/mineru_offline_docs.py
COPY patch_fastapi.py       /tmp/patch_fastapi.py
COPY static/                /opt/mineru-static/
RUN python3 /tmp/patch_fastapi.py && rm -f /tmp/patch_fastapi.py
```

No source code of `mineru`, `fastapi`, or `vllm` is distributed; only a two-line shim is injected at build time.

### 中文

`mineru` 包在 `mineru/cli/fast_api.py` 里通过 `create_app()` 构建 FastAPI 应用，默认路由的 HTML 全部引用外部 CDN。

本项目包含三个关键文件：

- `mineru_offline_docs.py` — 对外暴露 `apply_offline_docs(app)`，把 `/opt/mineru-static/` 里的静态资源挂载到 `/static`，并重新注册 docs 路由指向本地资源。
- `static/` — 包含 `swagger-ui-bundle.js`、`swagger-ui.css`、`redoc.standalone.js`，构建时直接 COPY 进镜像，无需任何网络下载。
- `patch_fastapi.py` — 构建时执行的一次性脚本，在 `app = create_app()` 后注入 `apply_offline_docs(app)` 调用，注入前做幂等检查，重复构建不会叠加。

`-offline-docs` Dockerfile 将上述文件复制进镜像并执行 patch：

```dockerfile
COPY mineru_offline_docs.py /usr/local/lib/python3.12/dist-packages/mineru_offline_docs.py
COPY patch_fastapi.py       /tmp/patch_fastapi.py
COPY static/                /opt/mineru-static/
RUN python3 /tmp/patch_fastapi.py && rm -f /tmp/patch_fastapi.py
```

不分发 `mineru`、`fastapi`、`vllm` 任何源码，仅在构建阶段注入两行 shim。

---

## Configuration reference / 配置项参考

`docker-compose.yml` exposes the following settings:

`docker-compose.yml` 中可调整的主要配置项：

| Key / 配置项 | Default / 默认值 | Purpose / 说明 |
| --- | --- | --- |
| `image` | `mineru:2.5-vllm-cu130-offline-docs` | Image tag to run. Change to the cu124 variant if needed. / 要运行的镜像标签，cu124 版本需改此处 |
| `ports` | `8000:8000` | Host-to-container port mapping. / 宿主机到容器端口映射 |
| `MINERU_MODEL_SOURCE` | `local` | Use models baked into the image, not downloaded at runtime. / 使用镜像内预下载的模型 |
| `VLLM_ENABLE_CUDA_COMPATIBILITY` | `0` | Set to `1` for CUDA 12.4–12.9; leave `0` for CUDA 13.0. / CUDA 12.4–12.9 环境设为 `1`，CUDA 13.0 保持 `0` |
| `HF_HUB_OFFLINE` | `1` | Disallow Hugging Face hub calls at runtime. / 禁止运行时访问 Hugging Face |
| `HF_HUB_DISABLE_TELEMETRY` | `1` | Disable Hugging Face telemetry. / 关闭 Hugging Face 遥测 |
| `VLLM_NO_USAGE_STATS` | `1` | Disable vLLM usage statistics reporting. / 关闭 vLLM 统计上报 |
| `MODELSCOPE_ENVIRONMENT` | `offline` | Disallow ModelScope calls at runtime. / 禁止运行时访问 ModelScope |
| `DO_NOT_TRACK` | `1` | Disable additional tracking signals. / 关闭额外追踪信号 |
| `entrypoint` | `mineru-api` | Runs the core MinerU document-conversion API service. / 启动核心文档转换 API |
| `--gpu-memory-utilization` | `0.9` | Fraction of GPU memory vLLM may use. / vLLM 可使用的显存比例 |
| `--max-num-seqs` | `2` | Max concurrent sequences vLLM will batch. / vLLM 最大并发序列数 |
| `resources.limits.memory` | `16G` | Container memory cap. / 容器内存上限 |
| `device_ids` | `["0"]` | GPU id(s) to bind. / 绑定的 GPU 编号 |
| `healthcheck` | `curl -f http://localhost:8000/health` | Container health probe used by compose. / compose 健康检查 |

---

## Verifying the offline patch worked / 验证离线补丁生效

### English

After `docker compose up -d` is healthy:

```bash
# /docs HTML should reference local /static/... assets, not CDN URLs.
curl -s http://localhost:8000/docs | grep -E 'swagger-ui|cdn.jsdelivr'
# expect: /static/swagger-ui.css and /static/swagger-ui-bundle.js

# /static assets must return HTTP 200.
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui-bundle.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/redoc.standalone.js
# expect: 200 / 200 / 200
```

After verification, disconnect the host from the network — `/docs` will continue to work.

### 中文

`docker compose up -d` 健康后：

```bash
# /docs 的 HTML 里应引用本地 /static/... 资源，不应出现 CDN URL。
curl -s http://localhost:8000/docs | grep -E 'swagger-ui|cdn.jsdelivr'
# 期望看到：/static/swagger-ui.css 和 /static/swagger-ui-bundle.js

# /static 资源应返回 HTTP 200。
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui-bundle.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/redoc.standalone.js
# 期望：200 / 200 / 200
```

验证通过后，断开宿主机外网，`/docs` 仍然可以正常使用。

---

## Repository layout / 仓库文件说明

| File / 文件 | Purpose / 说明 |
| --- | --- |
| `Dockerfile-offline-cu130-vllm220` | Step 1 (cu130): builds base runtime image `mineru:2.5-vllm-cu130`. / 第一步：构建 cu130 运行时基础镜像 |
| `Dockerfile-offline-cu130-vllm220-offline-docs` | Step 2 (cu130): layers offline docs patch → `mineru:2.5-vllm-cu130-offline-docs`. / 第二步：叠加离线 docs 补丁 |
| `Dockerfile-offline-cu124-vllm112` | Step 1 (cu124): builds base runtime image `mineru:2.5-vllm-cu124`. / 第一步：构建 cu124 运行时基础镜像 |
| `Dockerfile-offline-cu124-vllm112-offline-docs` | Step 2 (cu124): layers offline docs patch → `mineru:2.5-vllm-cu124-offline-docs`. / 第二步：叠加离线 docs 补丁 |
| `mineru_offline_docs.py` | Runtime patch module — mounts vendored assets and overrides docs routes. / 运行时补丁模块 |
| `patch_fastapi.py` | Build-time script that injects the patch shim into `mineru/cli/fast_api.py`. / 构建时注入 shim 的脚本 |
| `static/` | Vendored Swagger UI and ReDoc static assets — no internet download needed at build time. / 内嵌静态资源，构建时无需联网 |
| `docker-compose.yml` | One-command service start config. / 一键启动服务的 compose 配置 |
| `README.md` | This file. |

---

## License / 许可证

### English

The files in this repo (`mineru_offline_docs.py`, `patch_fastapi.py`, Dockerfiles, and compose configs) are released under the MIT License. They build on top of the [open-source MinerU](https://github.com/opendatalab/MinerU) project; please refer to that project for the licensing of the underlying `mineru` package.

### 中文

本仓库内的文件（`mineru_offline_docs.py`、`patch_fastapi.py`、Dockerfile 及 compose 配置）采用 MIT 许可证发布。它们基于开源的 [MinerU](https://github.com/opendatalab/MinerU) 项目，`mineru` 包本身的许可证请参考上游项目。
