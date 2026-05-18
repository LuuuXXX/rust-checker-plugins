# rust-checker-plugins

> `rust-checker` 官方插件注册表 — 收录内置工具的插件描述文件，并作为社区插件的发布中心。

---

## 目录结构

```
rust-checker-plugins/
├── registry.toml           # 插件注册索引
├── plugins/                # 各插件目录
│   ├── build/
│   │   └── plugin.toml
│   ├── test/
│   │   └── plugin.toml
│   ├── coverage/
│   │   └── plugin.toml
│   ├── clippy/
│   │   └── plugin.toml
│   ├── fmt/
│   │   └── plugin.toml
│   ├── doc/
│   │   └── plugin.toml
│   ├── audit/
│   │   └── plugin.toml
│   ├── deny/
│   │   └── plugin.toml
│   ├── geiger/
│   │   └── plugin.toml
│   ├── msrv/
│   │   └── plugin.toml
│   ├── semver/
│   │   └── plugin.toml
│   ├── udeps/
│   │   └── plugin.toml
│   ├── bench/
│   │   └── plugin.toml
│   ├── bloat/
│   │   └── plugin.toml
│   ├── flamegraph/
│   │   └── plugin.toml
│   ├── binary/
│   │   └── plugin.toml
│   ├── deps/
│   │   └── plugin.toml
│   └── metrics/
│       └── plugin.toml
└── CONTRIBUTING.md
```

---

## 快速上手

### 安装插件

```bash
# 安装单个插件
rust-checker plugin add clippy

# 查看已安装插件
rust-checker plugin list

# 更新所有插件
rust-checker plugin update

# 卸载插件
rust-checker plugin remove clippy
```

安装后插件文件存放于项目的 `.localcheck/plugins/<name>/plugin.toml`。

---

## plugin.toml 规范

每个插件由一个 `plugin.toml` 文件描述，包含以下字段：

```toml
[plugin]
name        = "<plugin-name>"        # 插件唯一标识符（小写字母 + 连字符）
version     = "0.1.0"               # 语义化版本
description = "<描述>"              # 简短说明
author      = "<author>"            # 作者
category    = "<category>"          # 分类：quality / security / deps / perf / compat
tags        = ["tag1", "tag2"]      # 可选标签

[command]
program = "cargo"                   # 可执行文件
args    = ["<arg1>", "<arg2>"]      # 参数列表（支持 {target} 等占位符）
env     = { KEY = "VALUE" }         # 可选环境变量

[report]
parser      = "builtin::<name>"     # 报告解析器（builtin:: 前缀为内置，custom:: 为自定义）
output_path = "<category>/<name>.md" # 输出路径（相对于 .localcheck/reports/）

[[output_schema.fields]]
name        = "<field>"             # 字段名
type        = "string"              # 类型：string / integer / float / boolean / list
description = "<说明>"             # 字段说明

[[dependencies.required]]
name    = "<dep>"                   # 依赖名称
install = "<install-cmd>"           # 安装命令

[[dependencies.optional]]
name    = "<dep>"
install = "<install-cmd>"
```

详细贡献规范请参阅 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 内置插件列表

| 插件 | 分类 | 命令 | 报告路径 |
|------|------|------|----------|
| build | quality | `cargo build` | `quality/build.md` |
| test | quality | `cargo test` | `quality/test.md` |
| coverage | quality | `cargo llvm-cov` | `quality/coverage.md` |
| clippy | quality | `cargo clippy` | `quality/clippy.md` |
| fmt | quality | `cargo fmt --check` | `quality/fmt.md` |
| doc | quality | `cargo doc --no-deps` | `quality/doc.md` |
| audit | security | `cargo audit` | `security/audit.md` |
| deny | security | `cargo deny check` | `security/deny.md` |
| geiger | security | `cargo geiger` | `security/geiger.md` |
| msrv | compat | `cargo msrv` | `compat/msrv.md` |
| semver | compat | `cargo semver-checks` | `compat/semver.md` |
| binary | compat | `cargo build --release` | `compat/binary.md` |
| deps | deps | `cargo tree` | `deps/deps.md` |
| udeps | deps | `cargo +nightly udeps` | `deps/udeps.md` |
| flamegraph | perf | `cargo flamegraph` | `perf/flamegraph.md` |
| bench | perf | `cargo bench` | `perf/bench.md` |
| bloat | perf | `cargo bloat --release` | `perf/bloat.md` |
| metrics | perf | `cargo geiger` | `perf/metrics.md` |

---

## 贡献插件

欢迎提交社区插件！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解贡献规范与 CI 验证流程。

## License

MIT
