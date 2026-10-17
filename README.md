# Gemini Web Gateway Skill

面向 Codex 的通用部署 skill：在自有 NAS/服务器或 Mac 本机运行 Gemini 网页会话的 OpenAI 兼容网关，并接入 Cherry Studio 或 WorkBuddy。

## 使用

将 `skills/deploy-gemini-web-gateway` 文件夹放入你的 Codex skill 目录，例如 `${CODEX_HOME:-$HOME/.codex}/skills/`，然后调用：

```text
使用 $deploy-gemini-web-gateway 检查我的自有 NAS 或 Mac 本机部署条件，并将已授权的 Gemini 对话网关接入所选 GUI。私密处理凭据，保留现有服务和默认配置。
```

入口是 [SKILL.md](skills/deploy-gemini-web-gateway/SKILL.md)，按任务选择NAS、[Mac本地](skills/deploy-gemini-web-gateway/references/mac-local.md)、GUI或排障引用。Mac包含容器与本地uv两条路线，默认loopback；上游版本与产品UI会变化，执行时需重新核实。

## 范围

- 专用容器、资源/网络边界、私密Cookie更新、真实模型发现与严格路由验收。
- Mac本地运行时/芯片架构核实、loopback Compose模板、独立uv环境、GUI地址和休眠/自启边界。
- Cherry Studio和WorkBuddy的追加式配置，不覆盖现有模型、默认项或历史。
- 仅普通对话集成；不承诺 Gemini 网页原生Task、客户端工具工作流或账户资格。
- 新生成请求需核对明确授权，不能把“测试连接”当作只读。

此仓库不包含个人部署配置、真实账号模型清单、凭据、缓存、日志或截图。所有示例均为占位符/合成数据。网页会话方案并非官方API，须自行核实适用条款和上游兼容性。

## 本地检查

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

附带的模板生成器只读取显式提供的模型目录，生成**空API key**的WorkBuddy新增条目；不联网、不读取任何客户端凭据、不修改真实配置。使用方式见GUI引用。

发布文件及隐私检查范围见 [REVIEW.md](REVIEW.md)。
