# mineru-vllm-offline-docs

A drop-in patch for the [`mineru`](https://github.com/opendatalab/MinerU) vLLM-backed
FastAPI service that vendors the Swagger UI and ReDoc static assets, so
`/docs` and `/redoc` work in **air-gapped (no-internet) environments** such as
isolated LANs.

---

## Why this exists / 项目背景

### English

By default, `mineru-api` uses FastAPI's stock `get_swagger_ui_html`, whose
generated HTML references CDN-hosted assets:

- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css`
- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
- `https://fastapi.tiangolo.com/img/favicon.png`

In an air-gapped LAN, none of these can be loaded and the `/docs` page is
unusable. This project vendors the necessary assets and overrides the default
docs routes so everything is served from inside the container.

### 中文

`mineru-api` 默认使用 FastAPI 自带的 `get_swagger_ui_html` 生成 Swagger UI
页面，HTML 中引用的 CSS / JS / favicon 全部托管在 CDN 上：

- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css`
- `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
- `https://fastapi.tiangolo.com/img/favicon.png`

在物理隔离的局域网里这些资源都拉不到，`/docs` 页面就完全打不开。本项目把
所需的静态资源内嵌到容器内，并替换默认的 docs 路由，使整个 API 文档
完全离线可用。

---

## What you get / 提供的功能

### English

- Self-contained `/docs` (Swagger UI) and `/redoc` pages served from inside
  the container.
- No internet access required at runtime — fully air-gapped friendly.
- Minimal footprint: a single Python file + a thin Dockerfile on top of the
  official `mineru:2.5-vllm` image.
- Idempotent build: rebuilding the image will not re-apply the patch twice.

### 中文

- `/docs`（Swagger UI）和 `/redoc` 页面完全由容器自身提供，零外网依赖。
- 完全离线 / 物理隔离网络友好。
- 改动极小：仅一个 Python 补丁文件 + 基于 `mineru:2.5-vllm` 的轻量 Dockerfile。
- 幂等构建：镜像重建时不会重复注入补丁。

---

## Quick start / 快速开始

### English

Prerequisites:

- Docker 24+ with the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed.
- The `mineru:2.5-vllm-offline` image built locally (see "Build the images" below). It is built in two layers on top of `vllm/vllm-openai:v0.20.0-cu130`.
- An NVIDIA GPU (this service is vLLM-backed).

Run the service:

```bash
docker compose up -d
```

`docker-compose.yml` references `mineru:2.5-vllm-offline` as a pre-built
image; it does not build it for you. Make sure that image exists locally
before running the command.

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
- 本地已存在 `mineru:2.5-vllm-offline` 镜像（构建方法见下文"构建镜像"）。该镜像在 `vllm/vllm-openai:v0.20.0-cu130` 之上分两层构建。
- 一块 NVIDIA GPU（服务由 vLLM 驱动）。

启动服务：

```bash
docker compose up -d
```

`docker-compose.yml` 把 `mineru:2.5-vllm-offline` 作为已经构建好的镜像
来引用，不会自动构建。运行这条命令前请先确保该镜像已经存在于本地。

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

### English

Two images are involved, built in order:

**1. Base image — `mineru:2.5-vllm`** (built from the upstream `Dockerfile` in
this repo, identical to the one in the original project):

```bash
docker build -f Dockerfile -t mineru:2.5-vllm .
```

This image:

1. Starts from `vllm/vllm-openai:v0.20.0-cu130`.
2. Installs libgl + Noto fonts (for opencv and CJK characters).
3. Installs the `mineru[core]` package and downloads all models at build time.

**2. Offline-docs image — `mineru:2.5-vllm-offline`** (built from
`Dockerfile.offline-docs` in this repo, layered on top of step 1):

```bash
docker build -f Dockerfile.offline-docs -t mineru:2.5-vllm-offline .
```

This step:

1. Vendors `redoc.standalone.js` into vllm's swagger-ui static dir.
2. Copies `mineru_offline_docs.py` into the image.
3. Injects a two-line shim into `mineru/cli/fast_api.py` so that
   `apply_offline_docs(app)` runs at startup, overriding the default
   `/docs` and `/redoc` routes to use the vendored assets.

`docker-compose.yml` references the second image by tag, so make sure
it exists before running `docker compose up -d`.

### 中文

整套流程涉及两个镜像，按顺序构建：

**1. 基础镜像 — `mineru:2.5-vllm`**（用仓库自带的 `Dockerfile` 构建，
与原项目一致）：

```bash
docker build -f Dockerfile -t mineru:2.5-vllm .
```

这个镜像会做三件事：

1. 基于 `vllm/vllm-openai:v0.20.0-cu130`。
2. 安装 libgl 与 Noto 字体（OpenCV 与中文字符支持）。
3. 安装 `mineru[core]` 包，并在构建阶段下载全部模型。

**2. 离线文档镜像 — `mineru:2.5-vllm-offline`**（用仓库自带的
`Dockerfile.offline-docs` 构建，叠在第 1 步之上）：

```bash
docker build -f Dockerfile.offline-docs -t mineru:2.5-vllm-offline .
```

这一步会做：

1. 把 `redoc.standalone.js` 内嵌到 vllm 的 swagger-ui 静态目录。
2. 把 `mineru_offline_docs.py` 拷进镜像。
3. 向 `mineru/cli/fast_api.py` 注入两行 shim，让 `apply_offline_docs(app)`
   在启动时被调用，把默认的 `/docs`、`/redoc` 路由替换为使用内嵌资源。

`docker-compose.yml` 按 tag 引用第 2 个镜像，运行 `docker compose up -d`
前请先确保它已经构建好。

---

## Manual build (without docker compose) / 手动构建

### English

```bash
# 1. Build the offline image on top of mineru:2.5-vllm
docker build \
  -f Dockerfile.offline-docs \
  -t mineru:2.5-vllm-offline \
  .

# 2. Run it
docker run --gpus all --rm -it \
  --name mineru-vllm \
  -p 8000:8000 \
  -e MINERU_MODEL_SOURCE=local \
  mineru:2.5-vllm-offline \
  mineru-api --host 0.0.0.0 --port 8000
```

To pin a different mirror for the redoc bundle (e.g. a private registry):

```bash
docker build \
  -f Dockerfile.offline-docs \
  --build-arg REDOC_JS_URL=https://your-mirror/redoc.standalone.js \
  -t mineru:2.5-vllm-offline \
  .
```

### 中文

```bash
# 1. 在 mineru:2.5-vllm 基础上构建离线镜像
docker build \
  -f Dockerfile.offline-docs \
  -t mineru:2.5-vllm-offline \
  .

# 2. 运行
docker run --gpus all --rm -it \
  --name mineru-vllm \
  -p 8000:8000 \
  -e MINERU_MODEL_SOURCE=local \
  mineru:2.5-vllm-offline \
  mineru-api --host 0.0.0.0 --port 8000
```

如果构建机器上需要走内部镜像源，可以覆盖 `REDOC_JS_URL`：

```bash
docker build \
  -f Dockerfile.offline-docs \
  --build-arg REDOC_JS_URL=https://your-mirror/redoc.standalone.js \
  -t mineru:2.5-vllm-offline \
  .
```

---

## How the patch works / 补丁实现原理

### English

The `mineru` package builds its FastAPI app in
`mineru/cli/fast_api.py` via `create_app()`. The default constructor
registers `/docs`, `/redoc`, and `/docs/oauth2-redirect` routes whose HTML
references external CDN URLs.

This project ships a single module — [`mineru_offline_docs.py`](./mineru_offline_docs.py) —
that exposes `apply_offline_docs(app)`. Calling it does three things:

1. Mounts the vllm-shipped swagger-ui static dir (already present in the
   base image) plus the `redoc.standalone.js` bundle we drop alongside, at
   `/static`.
2. Removes the three default routes from `app.router.routes` (they are
   registered first and would otherwise shadow any replacement).
3. Re-registers `/docs`, `/redoc`, and `/docs/oauth2-redirect` with
   `swagger_js_url` / `swagger_css_url` / `redoc_js_url` pointing at
   `/static/...`. The favicon is replaced with an inline base64 data URL
   so the browser does not try to fetch a remote favicon.

The `Dockerfile.offline-docs` does two things at build time:

- Drops `redoc.standalone.js` (downloaded via Python's `urllib`) into
  vllm's static dir.
- Injects two lines into `mineru/cli/fast_api.py` right after
  `app = create_app()`:

  ```python
  from mineru_offline_docs import apply_offline_docs
  apply_offline_docs(app)
  ```

  The injection is guarded by a string-match idempotency check, so
  rebuilding does not stack patches.

No source code of `mineru`, `fastapi`, or `vllm` is modified; only a
two-line shim is added.

### 中文

`mineru` 包在 `mineru/cli/fast_api.py` 里通过 `create_app()` 构建 FastAPI
应用。默认构造函数会注册 `/docs`、`/redoc`、`/docs/oauth2-redirect` 三条
路由，它们生成的 HTML 全部引用外部 CDN。

本项目只新增一个模块 —— [`mineru_offline_docs.py`](./mineru_offline_docs.py)，
对外暴露 `apply_offline_docs(app)`。调用它会做三件事：

1. 把 vllm 自带的 swagger-ui 静态目录（基础镜像里已经有）连同我们额外
   放进去的 `redoc.standalone.js` 一起挂载到 `/static`。
2. 从 `app.router.routes` 中摘掉那三条默认路由（它们在路由表最前面，
   否则会永远优先匹配，新路由根本走不到）。
3. 重新注册 `/docs`、`/redoc`、`/docs/oauth2-redirect`，把
   `swagger_js_url` / `swagger_css_url` / `redoc_js_url` 全部指向
   `/static/...`。favicon 替换为内联 base64 data URL，避免浏览器再去
   拉外网 favicon。

`Dockerfile.offline-docs` 在构建阶段只做两件事：

- 用 Python `urllib` 下载 `redoc.standalone.js` 到 vllm 的静态目录。
- 在 `mineru/cli/fast_api.py` 里、`app = create_app()` 之后注入两行：

  ```python
  from mineru_offline_docs import apply_offline_docs
  apply_offline_docs(app)
  ```

  注入前会做幂等检查（字符串匹配），所以反复构建不会叠加补丁。

没有改动 `mineru`、`fastapi`、`vllm` 任何源码，只插入两行 shim。

---

## Configuration reference / 配置项参考

### English

`docker-compose.yml` exposes the following knobs (most only need changing if
your environment differs from the defaults):

| Key | Default | Purpose |
| --- | --- | --- |
| `ports` | `8000:8000` | Host port mapped to the container. |
| `MINERU_MODEL_SOURCE` | `local` | Use models vendored in the image, not a download at runtime. |
| `VLLM_ENABLE_CUDA_COMPATIBILITY` | `0` | Set to `1` if you hit CUDA driver issues on older GPUs (e.g. A10). |
| `HF_HUB_OFFLINE` | `1` | Disallow Hugging Face hub calls at runtime. |
| `MODELSCOPE_ENVIRONMENT` | `offline` | Disallow ModelScope calls at runtime. |
| `--gpu-memory-utilization` | `0.8` | Fraction of GPU memory vLLM may use. |
| `--max-num-seqs` | `4` | Max concurrent sequences vLLM will batch. |
| `devices.device_ids` | `["0"]` | GPU id(s) to bind. |
| `resources.limits.memory` | `12G` | Container memory cap. |
| `REDOC_JS_URL` (build arg) | `https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js` | Source of the vendored redoc bundle. |

### 中文

`docker-compose.yml` 暴露以下可调项（多数情况下默认值即可，环境不同时
再改）：

| 配置项 | 默认值 | 作用 |
| --- | --- | --- |
| `ports` | `8000:8000` | 宿主机到容器的端口映射 |
| `MINERU_MODEL_SOURCE` | `local` | 使用镜像内预下载的模型，运行时不再去下载 |
| `VLLM_ENABLE_CUDA_COMPATIBILITY` | `0` | 老 GPU（如 A10）出现 CUDA 兼容性问题时设为 `1` |
| `HF_HUB_OFFLINE` | `1` | 禁止运行时访问 Hugging Face |
| `MODELSCOPE_ENVIRONMENT` | `offline` | 禁止运行时访问 ModelScope |
| `--gpu-memory-utilization` | `0.8` | vLLM 可使用的显存比例 |
| `--max-num-seqs` | `4` | vLLM 同时批处理的最大序列数 |
| `devices.device_ids` | `["0"]` | 绑定的 GPU id |
| `resources.limits.memory` | `12G` | 容器内存上限 |
| `REDOC_JS_URL`（构建参数） | `https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js` | redoc 离线包的下载源 |

---

## Verifying the offline patch worked / 验证离线补丁生效

### English

After `docker compose up -d` is healthy:

```bash
# 1. /docs HTML should reference local /static/... assets, not CDN URLs.
curl -s http://localhost:8000/docs | grep -E 'swagger-ui|cdn.jsdelivr'
# expect: /static/swagger-ui.css and /static/swagger-ui-bundle.js

# 2. /static assets must be served.
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui-bundle.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/redoc.standalone.js
# expect: 200 / 200 / 200
```

You can disconnect the host from the network and `/docs` will continue to
work.

### 中文

`docker compose up -d` 健康后：

```bash
# 1. /docs 的 HTML 里应引用本地 /static/... 资源，不应出现 CDN URL。
curl -s http://localhost:8000/docs | grep -E 'swagger-ui|cdn.jsdelivr'
# 期望看到：/static/swagger-ui.css 和 /static/swagger-ui-bundle.js

# 2. /static 资源应能正常访问。
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/swagger-ui-bundle.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/static/redoc.standalone.js
# 期望：200 / 200 / 200
```

验证通过后，断开宿主机的外网，`/docs` 仍然可以正常使用。

---

## Repository layout / 仓库文件说明

| File | Purpose |
| --- | --- |
| `Dockerfile` | Builds the upstream `mineru:2.5-vllm` base image. |
| `Dockerfile.offline-docs` | Layers the offline docs patch on top of `mineru:2.5-vllm`. |
| `mineru_offline_docs.py` | The offline docs patch module. |
| `docker-compose.yml` | One-command run config for the offline image. |
| `README.md` | This file. |

---

## License / 许可证

### English

The patch module (`mineru_offline_docs.py`) and Dockerfiles in this repo
are released under the MIT License. They build on top of the
[open-source MinerU](https://github.com/opendatalab/MinerU) project; please
refer to that project for the licensing of the underlying `mineru`
package.

### 中文

本仓库内的补丁模块（`mineru_offline_docs.py`）与 Dockerfile 采用 MIT
许可证发布。它们基于开源的 [MinerU](https://github.com/opendatalab/MinerU)
项目，`mineru` 包本身的许可证请参考上游项目。
