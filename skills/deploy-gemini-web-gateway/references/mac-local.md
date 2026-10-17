# Mac 本机部署

当网关和桌面GUI都在同一台Mac时，不需要NAS、SSH、DSM root任务或LAN端口。先明确用户选**容器运行**还是**本地Python/uv运行**；不因本skill替换现有运行时或把服务部署到另一台机器。

## 选择与检查

| 路径 | 适用情形 | 需要核实 |
|---|---|---|
| A：已有Docker兼容运行时 | 用户已有Docker Desktop/OrbStack等，希望隔离和便于回滚 | 当前context指向本机，运行时已启动，镜像架构/VM资源/卷权限合适 |
| B：本地uv | 用户不想运行容器，接受独立项目环境 | 所选上游ref的Python要求、锁文件、原生依赖wheel/构建条件 |

只读检查 `uname -m`、macOS支持情况、内存/磁盘、端口与现有进程；容器路线另查 `docker context show`、context目标、客户端/引擎版本和当前容器。**若context实际指向远端，停止本地部署，不能顺手切换全局context或在远端创建容器。**

Apple Silicon与Intel不同；读取候选镜像manifest，选择匹配平台的已审查digest。没有原生arm64镜像时，不静默强制amd64模拟、安装Rosetta或运行未知镜像；说明性能/兼容性代价，取得相应决定，或选择经审查的本地构建/uv路径。运行时的Linux VM预算与Mac总内存、容器限制是不同层级，不擅自调整其他应用的预算。

如需新安装Docker Desktop，按 [官方Mac安装页](https://docs.docker.com/desktop/setup/install/mac-install/) 核对当前芯片、系统支持与许可，由用户完成条款/权限步骤；不自动安装另一套运行时或停用现有服务。

## 通用私密目录与网络边界

可在用户选择的非共享/非同步目录下建立独立项目，例如 `$HOME/Library/Application Support/gemini-web-gateway`。所有含空格路径均引用。目录默认0700，凭据配置/备份0600；保持HOME、CODEX_HOME、全局Python、shell启动文件及其他客户端默认项不变。

Google Cookie仅进入用户私下编辑的配置文件；GUI仍只用网关API key。即使loopback允许客户端留空，也不因此关闭网关鉴权。不要在命令参数、Compose环境、plist、截图或公开文件中嵌入Cookie/key。

本机GUI默认访问 `http://127.0.0.1:8000/v1`（端口仅示例，需查空闲）。容器内部监听与Mac对外发布是两个设置；[Docker端口文档](https://docs.docker.com/engine/network/port-publishing/) 说明不写主机地址可能暴露到所有接口，且旧引擎存在loopback例外。显式loopback发布后仍核对实际绑定及运行时安全版本，不把示例当成隔离保证；不开放LAN、公网或全局防火墙豁免。

## A. Mac 上运行专用容器

1. 复用用户确认的本地Docker兼容运行时，不更改共享代理、全局context或VM设置。按 [nas-gateway.md](nas-gateway.md) 的共同原则核实上游schema、API鉴权、私密Cookie、稳定client ID与cache/data持久化；不执行其中DSM/SSH操作。
2. 在独立私密工作目录建立 `config/`、`data/`、`cache/`，将按所选ref审查的配置私下保存到 `config/config.yaml`。核对非空API key、客户端Cookie、CORS与应用日志级别；没有完整私密配置时不启动。
3. 查看 [mac-compose.yaml](../assets/mac-compose.yaml)，复制到工作目录；它是**配置片段模板，不是包含凭据/权限适配的即用安装器**。填入已审查digest，只用非敏感环境变量；不设置凭据环境变量。
4. 核对镜像的非root运行身份、Mac文件共享和容器UID映射，确认实际进程能只读配置并写自己的cache/data。不要为兼容使用777、修改整个用户目录所有权，或硬编码另一台Linux主机的UID。
5. 先离线审阅Compose，再确认项目名/服务/端口不与现有工作冲突，最后只启动这个项目。`docker compose config`可能展开真实配置路径或环境，不在聊天/公开日志输出完整结果。

示例操作顺序（**先填配置、确认授权及真实digest**，再手动运行；这里不提供任何真实值）。`up -d` 可能触发真实账户初始化与外网请求，不是离线准备；仅被授权写计划时不能执行：

```sh
cd "$HOME/Library/Application Support/gemini-web-gateway"
export GEMINI_IMAGE='ghcr.io/nativu5/gemini-fastapi@sha256:REVIEWED_DIGEST'
export GATEWAY_PORT='8000'
docker compose -p gemini-web-local -f compose.yaml config --quiet
docker compose -p gemini-web-local -f compose.yaml up -d
```

`REVIEWED_DIGEST`必须替换，示例不能原样启动。模板只检查镜像变量非空，并不机器验证digest、架构、完整凭据或非root身份；这些都是启动前必须人工/工具核对的门槛。平台/资源/只读rootfs/tmpfs等适配要按选定镜像验证；不要为规避错误放宽到privileged或挂载Docker socket。若需只读rootfs，先明确所有必要写路径并离线/限定运行验证。

容器里的 `127.0.0.1` 是容器自身，不是Mac。需要访问Mac已有代理时，先核对该运行时官方支持的host访问方式；Docker Desktop可参考 [其网络文档](https://docs.docker.com/desktop/features/networking/) 中的VM/host边界。不能照搬NAS代理地址，也不为访问代理自动将其绑定到所有接口。

## B. 不使用容器：本地uv

仅在用户选择此路径时进行。把**经审查的上游ref**取到独立项目目录，核对 `pyproject.toml`、`uv.lock` 和入口。不要使用下载即执行脚本，也不复制旧NAS的venv到macOS。

当前上游 [pyproject](https://github.com/Nativu5/Gemini-FastAPI/blob/main/pyproject.toml) 与 [锁文件](https://github.com/Nativu5/Gemini-FastAPI/blob/main/uv.lock) 可用于发现要求；实际以选定ref为准，不能从README的“某版本以上”猜测任意系统Python都合适。uv锁定安装的行为见 [uv同步文档](https://docs.astral.sh/uv/concepts/projects/sync/)。

在已核对ref的项目目录中执行：

```sh
uv sync --frozen --no-dev
```

它可能下载项目要求的Python和依赖；先确认该安装范围获准。若curl_cffi/LMDB等没有匹配平台wheel或构建失败，保留错误阶段并评估，不能卸载全局Python、升级用户其他环境或放宽锁定要求“试到能跑”。

在此项目的私密 `config/config.yaml` 中设置：

- `server.host`为`127.0.0.1`，端口选择已确认空闲值；不能沿用面向容器的`0.0.0.0`。
- `server.api_key`为私密强随机值；Google客户端凭据由用户私下填入。
- `storage`、`cache`等路径属于本项目；保持client ID稳定，设置持久Cookie cache。
- 关闭不需要的CORS/调试日志，按所选ref确认全部schema，而非只改这几项。

完成配置后，可先以前台进程运行，明确退出/回滚方法：

```sh
export GEMINI_COOKIE_PATH="$PWD/cache"
uv run --frozen --no-dev python run.py
```

入口以所选ref的 [run.py](https://github.com/Nativu5/Gemini-FastAPI/blob/main/run.py) 为准。使用项目解释器，不依赖终端裸Python。开始真实初始化前核对用户授权；初次账户初始化不等于聊天生成，但也不是纯离线操作。

## 验收、GUI与持续运行

按 [validation-and-diagnosis.md](validation-and-diagnosis.md) 先验loopback绑定、health、鉴权、真实目录，再按 [gui-clients.md](gui-clients.md) 追加配置：

| 客户端 | Mac本地示例地址 |
|---|---|
| Cherry Studio | `http://127.0.0.1:8000/v1` |
| WorkBuddy | `http://127.0.0.1:8000/v1/chat/completions` |

只有另有授权才发送最小chat/SSE；本机和NAS是不同会话/进程，不能复制NAS成功结论。此方案不改变网页原生Task尚需独立验证的边界。

关闭终端、退出容器运行时、Mac休眠/关机可能使服务不可用。不要为了常驻自动改电源策略、安装root daemon或设置登录自启。用户明确需要持续运行时，再设计当前用户LaunchAgent或运行时启动方案，使用绝对可执行路径/WorkingDirectory、私密配置引用与可撤销卸载步骤；不在plist写入Cookie/key。

回滚仅停本项目或明确进程，保留私密cache/data与备份；不要执行全局prune、删除VM、卸载运行时或停止别的项目。升级不重置API key，不并行运行共享同一LMDB/cache的新旧实例。

本引用经过文档/模板静态核查，不代表已在真实Intel/Apple Silicon设备上完成部署或账户验收；使用时仍需分层验证。
