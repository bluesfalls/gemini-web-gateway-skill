# Gemini Web Gateway Skill

面向 Codex 的通用部署 skill：在自有 NAS/服务器或 Mac 本机运行 Gemini 网页会话的 OpenAI 兼容网关，并接入 Cherry Studio 或 WorkBuddy。

## 使用

将 `skills/deploy-gemini-web-gateway` 文件夹放入你的 Codex skill 目录，例如 `${CODEX_HOME:-$HOME/.codex}/skills/`，然后调用：

```text
使用 $deploy-gemini-web-gateway 检查我的自有 NAS 或 Mac 本机部署条件，并将已授权的 Gemini 对话网关接入所选 GUI。私密处理凭据，保留现有服务和默认配置。
```

入口是 [SKILL.md](skills/deploy-gemini-web-gateway/SKILL.md)，按任务选择NAS、[Mac本地](skills/deploy-gemini-web-gateway/references/mac-local.md)、GUI或排障引用。Mac包含容器与本地uv两条路线，默认loopback；上游版本与产品UI会变化，执行时需重新核实。

## 最新方案（2026-10-18）

新增 [文件工具与桌面 Agent](skills/deploy-gemini-web-gateway/references/file-tools-and-agents.md) 实施与验收清单：

- 区分模型 API、客户端本机工具与真实文件产物；只发送本地路径不等于上传内容。
- Cherry 的 Pi runtime 与 WorkBuddy 的工具能力声明、独立工作目录和逐次授权。
- 工具调用的严格参数兼容、带工具聊天的 buffered SSE，以及限定路径的生成重试门禁。
- 单 active ASGI 请求、有限排队、队列超时与远端取消未知的边界。
- 先离线审查和合成预检，再私密备份、限定升级、哈希/规格/健康核对与失败回滚。

本仓库分发的是 **部署操作 skill、文档与空 key 模板**，不是增强网关的一键发行包；不包含现场补丁、SSH 安装器或私人部署记录。增强适配须按目标源码和 SDK 版本另行实现、审查并验收，不能仅修改能力开关就当作已支持。NAS 案例结论也不能外推为 Mac 同适配已实机验证。

## 范围

- 专用容器、资源/网络边界、私密Cookie更新、真实模型发现与严格路由验收。
- Mac本地运行时/芯片架构核实、loopback Compose模板、独立uv环境、GUI地址和休眠/自启边界。
- Cherry Studio和WorkBuddy的追加式配置，不覆盖现有模型、默认项或历史。
- 普通对话与经分层验证的客户端文件工具路径；不承诺任意客户端/模型组合、所有文件类型、Gemini 网页原生Task或账户资格。
- 新生成请求需核对明确授权，不能把“测试连接”当作只读。

此仓库不包含个人部署配置、真实账号模型清单、凭据、缓存、日志或截图。所有示例均为占位符/合成数据。网页会话方案并非官方API，须自行核实适用条款和上游兼容性。

## 本地检查

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

附带的模板生成器只读取显式提供的模型目录，生成**空API key**的WorkBuddy新增条目；不联网、不读取任何客户端凭据、不修改真实配置。使用方式见GUI引用。

自动检查还覆盖公开文件白名单、manifest、相对文档链接与示例地址；能力边界另经审查。这些检查不发送模型请求，也不证明某个设备已完成真实部署。

发布文件及隐私检查范围见 [REVIEW.md](REVIEW.md)。
