# 插件贡献指南

感谢你有意向为 `rust-checker-plugins` 贡献插件！本文档介绍插件的贡献规范与审核流程。

---

## 贡献流程

1. **Fork** 本仓库
2. 在 `plugins/<your-plugin-name>/` 目录下创建 `plugin.toml`
3. 在 `registry.toml` 中添加你的插件条目
4. 确保 CI 验证通过（格式校验 + schema 合规检查）
5. 提交 Pull Request，描述插件功能与使用场景

---

## 命名规范

- 插件名称使用**小写字母 + 连字符**，如 `my-tool`
- 名称应简洁且能体现工具用途
- 不能与已有插件名称冲突（参见 `registry.toml`）

---

## plugin.toml 必填字段

| 字段 | 说明 |
|------|------|
| `plugin.name` | 插件唯一名称 |
| `plugin.version` | 语义化版本（`MAJOR.MINOR.PATCH`） |
| `plugin.description` | 简短描述（建议不超过 80 字符） |
| `plugin.author` | 作者 GitHub 用户名或组织名 |
| `plugin.category` | 分类（见下方） |
| `command.program` | 可执行文件名 |
| `command.args` | 参数列表 |
| `report.parser` | 报告解析器标识 |
| `report.output_path` | 输出路径 |

### 分类（category）

| 值 | 含义 |
|----|------|
| `quality` | 代码质量（构建、测试、代码风格） |
| `security` | 安全检查（漏洞、许可证、unsafe） |
| `deps` | 依赖分析 |
| `perf` | 性能分析 |
| `compat` | 兼容性检查 |

---

## 报告解析器（parser）

- `builtin::<name>` — 使用 rust-checker 内置解析器
- `raw` — 捕获原始输出，不解析
- `custom::<module_path>` — 使用自定义解析器（需提供实现）

社区插件建议优先使用 `raw` 或基于已有 `builtin::` 解析器，以保证兼容性。

---

## 依赖声明

- `dependencies.required` — 必须满足，否则插件无法运行
- `dependencies.optional` — 可选，缺失时插件降级运行
- 每项需提供 `name`（工具名）和 `install`（安装命令）

---

## CI 验证

Pull Request 合并前会自动运行以下检查：

1. **schema 合规** — 验证 `plugin.toml` 必填字段是否完整
2. **registry 一致性** — 确认 `registry.toml` 中的条目与 `plugins/` 目录一致
3. **TOML 格式** — 使用 `taplo` 校验 TOML 语法
4. **命名规范** — 检查插件名称是否符合命名规则

---

## 版本升级

- 修改已有插件时需同步升级 `plugin.version`
- 破坏性变更（command / parser 变更）需升级 MAJOR 版本
- 新增字段视为 MINOR 升级
- 修复描述、文档视为 PATCH 升级

---

## 行为准则

请遵守 [Rust 社区行为准则](https://www.rust-lang.org/policies/code-of-conduct)。
