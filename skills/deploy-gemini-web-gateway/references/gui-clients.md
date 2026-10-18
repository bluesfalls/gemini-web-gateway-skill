# 桌面客户端接入

本文用于把自有NAS/服务器或Mac本机上的 OpenAI 兼容 Gemini 网页对话网关接入桌面客户端。
普通对话是默认保守路径；文件 Agent 还须按 [文件工具与桌面 Agent](file-tools-and-agents.md) 验证网关协议、本机执行器和产物。本文不保证 Gemini 网页原生 Task，也不保证任意模型或 runtime 的工具执行。
接口兼容不等于所有模型能力兼容，不能把尚未验证的工具调用声明为已支持；附带生成器仍默认输出关闭的工具能力。

## 接入前确认

- 确认用户授权的网关地址、目标客户端与允许修改的配置范围。
- 以下地址均为占位符：`https://gateway.example.invalid/v1`。
- 通过网关的只读 `GET /v1/models` 获取真实模型 ID；示例中的 `MODEL_ID_FROM_CATALOG` 必须替换为该目录中的 ID。
- 模型显示名可以友好化，但不能把显示名、网页任务名称或自造别名当作模型 ID。
- 非回环地址必须配置非空 API key；不要以空 key、占位 key 或关闭鉴权绕过要求。
- 文档和交付配置中的 key 默认留空，由用户私下填写；不要把 key 写进日志、截图或公开产物。
- 只有用户明确允许同一 key 跨客户端复用后，才可在指定来源和目标之间转移该 key。
- 不读取浏览器 Cookie，不遍历其他 provider，不从历史配置中搜集凭据。
- 本文不是永久 schema 合同；操作前核验当前应用版本的界面、配置格式及字段语义。
- 若应用或企业策略不允许自定义模型，停止并说明限制，不通过改文件绕过策略。

## Cherry Studio

1. 在当前版本中确认可用的 OpenAI 兼容 provider 配置入口。
2. 使用用户授权的 provider；若需新增，采用独立名称，不改已有 provider 或默认模型。
3. Base URL 填写 `https://gateway.example.invalid/v1`，不是完整的聊天接口路径。
4. API key 留待用户私下填写；非回环接入时，未填有效 key 不应继续实际请求。
5. 添加来自 `GET /v1/models` 的真实模型 ID，例如 `MODEL_ID_FROM_CATALOG`。
6. 可为模型设置友好显示名；保持请求使用的 ID 与目录一致。
7. 保存后检查 provider、Base URL、模型 ID 与显示名的映射，不暴露 key。

不要把网页任务名伪装成 API 模型，也不要仅凭模型出现在列表中就宣称工具或图片能力已验证。
“测试连接”可能触发生成请求；未获明确授权，不点击该按钮或发送测试消息。
若用户授权实际验证，只进行约定的最小普通对话，并核对所选 provider 和返回结果。

若需要文件 Agent，核对实际 runtime，而不只看模型。Pi 与 `claude-code` 执行器不同；变更模型不会切换 runtime。需要更换时创建独立助手并保留旧助手，不改全局默认或旧历史；工具最小集、逐次批准和本机 bash 非沙箱的边界见文件工具引用。

## WorkBuddy

### 修改边界与备份

- 通用本地配置位置为 `$HOME/.workbuddy/models.json`，根结构是数组。
- 先确认当前应用仍使用此位置、结构和下列字段；不盲目套用旧版本快照。
- 只读取用户授权的目标文件，不查看对话历史或无关 provider 配置。
- 修改前创建一个新的私密备份，限制为当前用户可读写；不覆盖旧备份或公开备份内容。
- 如文件不存在，确认确需创建后以空数组为起点；不要覆盖已有配置。
- 在原数组末尾追加独立条目；不删除、重排或更改现有项、默认选择及历史记录。
- 若相同 ID 已存在，先确认用户意图，不静默替换或制造重复项。
- 保存读取时的文件摘要，写前重读比对；发现应用或其他人已修改则停止，不能覆盖并发更新。验证新增内容后，用同目录私密临时文件和原子替换更新，并核对权限与原有条目完全不变。

### 追加条目示例

以下是一个完整数组示例，不是覆盖现有文件的指令：

```json
[
  {
    "id": "MODEL_ID_FROM_CATALOG",
    "name": "Gemini 网页对话网关",
    "vendor": "Custom",
    "url": "https://gateway.example.invalid/v1/chat/completions",
    "apiKey": "",
    "supportsToolCall": false,
    "supportsImages": false,
    "supportsReasoning": false,
    "useCustomProtocol": false
  }
]
```

- `id` 使用模型目录返回的原始 ID，不手动添加 `custom-local:`；运行时前缀由应用处理。
- `name` 只是显示名，不改变模型 ID，也不赋予网页原生任务能力。
- `vendor` 为 `Custom`；`url` 必须是完整的 `/v1/chat/completions` 地址。
- `apiKey` 在模板中为空；用户私下填入有效 key 后才可用于非回环请求。
- 未验证的 `supportsToolCall`、`supportsImages`、`supportsReasoning` 均保持 `false`。
- `useCustomProtocol` 保持 `false`，除非当前应用 schema 与网关协议均有明确依据要求其他值。
- 改动后验证 JSON 可解析、根结构为数组，且差异只有获准追加的条目；不得输出 key。
- 配置文件包含凭据时应保持私密文件权限，备份也按相同敏感级别处理。

### 加载与验收

先核实当前版本是否支持 `models.json` 热加载。若支持而设置页停留未刷新，可离开模型页再返回；若仍未出现，检查加载流程与策略，不直接强制重启或中断旧任务。确需重载/重启时先确认影响与授权。

先做不生成内容的检查：新模型是否出现，显示名、真实 ID、完整 URL 和能力开关是否正确。
未获授权，不点击“测试连接”、发送消息或启动 agent 任务。
若用户授权普通对话验证，使用新条目完成最小请求；成功仅证明该次普通对话可用。
不把普通对话成功外推为图片、推理、工具调用、网页 Task 或 agent 执行已受支持。

只有所选模型的合成工具闭环通过后，才经授权将该条目的 `supportsToolCall` 改为 `true`，同时保留其他条目与默认项。这个开关只声明能力，不修复网关或创建文件执行器；自然语言 PDF 任务还要实际验证读取工具、结果回传、新文件以及原件不变。文件工具引用列出了适配合同及先接口后 GUI 的验收顺序。

## 可选：离线生成新增条目草稿

已有经过确认的 `GET /v1/models` 目录时，可用 [build_workbuddy_models.py](../scripts/build_workbuddy_models.py) 避免重复手写条目。此工具面向 macOS/Linux，不联网、不读取客户端凭据，也不修改或合并真实 `models.json`。

在skill目录运行，路径按实际本地草稿位置替换：

```sh
python3 scripts/build_workbuddy_models.py \
  --catalog 'path/to/catalog.json' \
  --base-url 'https://gateway.example.invalid/v1' \
  --output 'path/to/workbuddy-additions.json'
```

输入是带 `data` 数组的模型目录；脚本保留原始ID，排除明确不可用项，重复/异常ID会拒绝。输出只含空key的新增条目，能力开关全false，新文件权限0600，已存在输出不会覆盖。**不要用输出覆盖正式配置**；先按前述边界私密备份、检查差异、追加条目并由用户私下填key。运行时生成的目录/草稿也不应提交到公开仓库。

## 出错与回退

- 鉴权失败：确认用户私下填写了正确 key；不打印 key，也不尝试其他 provider 的凭据。
- 模型不存在：重新核对授权网关的模型目录和原始 ID，不猜测别名或添加运行时前缀。
- 路径错误：Cherry 使用 `/v1` base，WorkBuddy 使用完整 `/v1/chat/completions`。
- 模型未出现：先检查 JSON 和当前版本 schema，再离开并返回模型页；保留现有任务。
- 需要回退时，仅撤销本次新增配置；恢复整份备份前先确认没有后续有效修改，并取得相应授权。
