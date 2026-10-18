# 发布前审查

## 结论与范围

发布内容为从零编写的通用 skill、引用文档、空 key 模板生成器与离线测试；不是任何人的部署备份或现场运行记录，也不包含增强网关运行时或一键升级脚本。

- 独立逐行隐私/授权审查：未发现可行动问题。
- 独立隔离前向演练：保留两项既有合成配置，只生成新增/合并草稿，不访问真实配置、网络、GUI或账户。
- 演练反馈已处理：补充生成器入口和使用说明；将热加载改为需核验当前版本的行为；保留配置冲突/合并属于有备份的授权步骤，不自动执行。
- 既有版本的发布记录包含官方 skill 格式校验与模板生成器 12 项离线测试；不把该记录当作本次更新的官方格式校验结果。
- 本次更新的 16 项离线测试通过，frontmatter 与 UI 元数据另经手工检查。当前环境缺少 PyYAML，官方 `quick_validate.py` 本轮未能完成；未为此安装额外依赖。
- Mac本地路线另经官方文档/上游入口核对和静态审阅；未执行实际部署、镜像拉取、Python依赖安装或登录。
- Mac隔离前向演练完成14项静态检查；明确区分loopback发布与容器内监听、已有本地运行时与远端context。模板不是digest/凭据的自动门禁，启动仍须核对授权并可能触发账户初始化。

测试覆盖空key/能力保守值、ID保持、目录校验、不可用模型过滤、重复ID、URL规范及凭据型URL拒绝、私密新文件、拒绝覆盖、错误不回显输入。合成fixture不含真实凭据或账号数据。

## 2026-10-18 方法更新

本次同步文件 Agent 的实施清单：客户端与模型/网关分层、Cherry runtime、WorkBuddy 能力门禁、严格工具参数编码、限定路径 buffered SSE/生成重试门禁，以及有限队列与未知远端取消。NAS 与 Mac 两条基础路线均保留，Mac 同增强适配未实机验收。

公开示例仅含占位路径与合成数据；不发布现场安装器、运行时哈希、账号模型目录、私密诊断、真实文件名/内容或截图。新增自动检查只验证公开树、manifest、相对链接和示例地址，能力边界另经独立审查，不能替代运行时兼容测试。

文档借鉴的局部验收限于选定版本和获准样例：接口工具闭环、Pi 合成文件任务、WorkBuddy 自然语言文件读取与新产物生成。它们不代表任意模型/会话/PDF 都可用，不保证文字无删改、图像逐像素无损、覆盖操作或网页原生 Task。对应现场代码与私密证据不随仓库发布。

## 发布白名单

仅发布以下源文件及其 `PUBLICATION_MANIFEST.sha256`，不发布工作目录/历史目录的其他内容：

```text
.gitignore
README.md
REVIEW.md
skills/deploy-gemini-web-gateway/SKILL.md
skills/deploy-gemini-web-gateway/agents/openai.yaml
skills/deploy-gemini-web-gateway/assets/mac-compose.yaml
skills/deploy-gemini-web-gateway/references/file-tools-and-agents.md
skills/deploy-gemini-web-gateway/references/gui-clients.md
skills/deploy-gemini-web-gateway/references/mac-local.md
skills/deploy-gemini-web-gateway/references/nas-gateway.md
skills/deploy-gemini-web-gateway/references/validation-and-diagnosis.md
skills/deploy-gemini-web-gateway/scripts/build_workbuddy_models.py
tests/test_build_workbuddy_models.py
tests/test_public_contract.py
```

审查对象包括上述文本中的真实secret、Cookie值、个人身份、真实内网地址/主机名、原机绝对路径、账户模型ID，以及意外打包的配置、缓存、数据库、HAR、截图、日志和bytecode。

`example.invalid`、`MODEL_ID_FROM_CATALOG`、demo/SYNTHETIC数据、Cookie字段名、通用`$HOME`/容器路径与loopback监听地址不是实际凭据或个人内网信息。生成器始终输出空key，不收集凭据，不替用户执行部署或生成测试。

## 限制

模式扫描不是对所有可能秘密形式的形式化证明；隐私结论还依赖逐行审查、从零构造和显式发布白名单。GitHub仓库归属及平台公开活动元数据不属于skill文件内容。

本次 GitHub 更新没有再次执行真实 NAS/Mac 部署、网页登录、模型生成或 GUI 任务。不能将上述匿名样例或仓库的离线文档测试当作任何新设备/上游版本的兼容性证明。上游链接、客户端 schema 与能力需在实际使用时重新核验。

发布后应回读实际Git tree并核对manifest。审查不授予新的账户、网络、生成、部署或公开敏感数据的授权。
