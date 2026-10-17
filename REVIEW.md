# 发布前审查

## 结论与范围

发布内容为从零编写的通用skill、引用文档、空key模板生成器和合成测试；不是任何人的部署备份或现场运行记录。

- 独立逐行隐私/授权审查：未发现可行动问题。
- 独立隔离前向演练：保留两项既有合成配置，只生成新增/合并草稿，不访问真实配置、网络、GUI或账户。
- 演练反馈已处理：补充生成器入口和使用说明；将热加载改为需核验当前版本的行为；保留配置冲突/合并属于有备份的授权步骤，不自动执行。
- 官方skill格式校验通过；模板生成器12项离线测试通过。
- Mac本地路线另经官方文档/上游入口核对和静态审阅；未执行实际部署、镜像拉取、Python依赖安装或登录。
- Mac隔离前向演练完成14项静态检查；明确区分loopback发布与容器内监听、已有本地运行时与远端context。模板不是digest/凭据的自动门禁，启动仍须核对授权并可能触发账户初始化。

测试覆盖空key/能力保守值、ID保持、目录校验、不可用模型过滤、重复ID、URL规范及凭据型URL拒绝、私密新文件、拒绝覆盖、错误不回显输入。合成fixture不含真实凭据或账号数据。

## 发布白名单

仅发布以下源文件及其 `PUBLICATION_MANIFEST.sha256`，不发布工作目录/历史目录的其他内容：

```text
.gitignore
README.md
REVIEW.md
skills/deploy-gemini-web-gateway/SKILL.md
skills/deploy-gemini-web-gateway/agents/openai.yaml
skills/deploy-gemini-web-gateway/assets/mac-compose.yaml
skills/deploy-gemini-web-gateway/references/gui-clients.md
skills/deploy-gemini-web-gateway/references/mac-local.md
skills/deploy-gemini-web-gateway/references/nas-gateway.md
skills/deploy-gemini-web-gateway/references/validation-and-diagnosis.md
skills/deploy-gemini-web-gateway/scripts/build_workbuddy_models.py
tests/test_build_workbuddy_models.py
```

审查对象包括上述文本中的真实secret、Cookie值、个人身份、真实内网地址/主机名、原机绝对路径、账户模型ID，以及意外打包的配置、缓存、数据库、HAR、截图、日志和bytecode。

`example.invalid`、`MODEL_ID_FROM_CATALOG`、demo/SYNTHETIC数据、Cookie字段名、通用`$HOME`/容器路径与loopback监听地址不是实际凭据或个人内网信息。生成器始终输出空key，不收集凭据，不替用户执行部署或生成测试。

## 限制

模式扫描不是对所有可能秘密形式的形式化证明；隐私结论还依赖逐行审查、从零构造和显式发布白名单。GitHub仓库归属及平台公开活动元数据不属于skill文件内容。

没有为本次发布执行真实NAS部署、网页登录、账号生成或GUI端到端测试；不能将合成测试当作上游兼容性或模型能力证明。上游链接与客户端schema需在实际使用时重新核验。

发布后应回读实际Git tree并核对manifest。审查不授予新的账户、网络、生成、部署或公开敏感数据的授权。
