# Repository Guidelines

## 项目结构与职责 (Project Structure & Module Organization)

- `src/gpt_image_cli/cli.py` 是 CLI 的核心实现，负责参数校验、请求路由和图片保存。
- `skills/gpt-image/` 包含生成技能、`references/` 和 `scripts/generate.py` 启动器；启动器复用 CLI，避免复制业务逻辑。
- `skills/get-prompt-from-image/` 存放图片反推提示词的技能与分析指南。
- `tests/` 存放离线测试；`docs/<category-slug>/` 存放图库图片；`.claude-plugin/` 存放插件元数据。

调整 CLI 参数时，同步 `--help` 与技能说明。

## 本地开发与校验命令 (Build, Test, and Development Commands)

使用 Python 3.11+ 和 `uv`，在仓库根目录执行：

`uv run` 会按 `pyproject.toml` 准备依赖；仅检查帮助不会发送生成请求。

| 命令 | 用途 |
| --- | --- |
| `uv run gpt-image --help` | 准备项目环境并检查 CLI 入口 |
| `uv run python skills/gpt-image/scripts/generate.py --help` | 检查技能启动器 |
| `uv run python -m unittest discover -s tests -v` | 运行全部离线测试 |
| `uv run python -m py_compile src/gpt_image_cli/cli.py src/gpt_image_cli/__init__.py` | 检查 Python 语法 |
| `uv build` | 使用 setuptools 构建 wheel 和源码包，输出到 `dist/` |
| `git diff --check` | 检查空白字符问题 |

## 编码风格与命名 (Coding Style & Naming Conventions)

Python 使用四空格缩进；函数、变量和模块使用 `snake_case`，类使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`。沿用现有类型注解和标准库优先的写法。仓库未配置专用格式化或 lint 工具，避免引入整文件格式化改动。新增图片和分类使用小写连字符命名，例如 `docs/photography/natural-sns-portrait.png`。

## 测试约定 (Testing Guidelines)

测试采用标准库 `unittest`，文件命名为 `tests/test_*.py`，方法命名为 `test_*`。修改 CLI 时，为参数边界、生成与编辑路由、请求序列化、错误退出码及凭据优先级补充相关回归用例。沿用临时目录、假密钥和模拟 HTTP transport，保持测试离线。当前没有覆盖率百分比门槛；真实出图验证需单独记录。

## 图库与双语文档 (Gallery & Bilingual Documentation)

遵循 `CONTRIBUTING.md`，同时更新 `README.md` 和 `README.zh.md`，保持条目编号、顺序及图片路径一致；增删条目后同步索引范围和图库总数。图片放在分类子目录，原创标记 `Original`，外部提示词保留 `Author + Source`。检查本地图片引用、重复锚点和分隔线；涉及技能参考内容时同步相应 `skills/*/references/` 文件。

## 提交与 Pull Request (Commit & Pull Request Guidelines)

默认使用中文沟通，Git 提交信息优先中文。历史提交多用简短祈使句，也有 `docs:`、`feat:` 前缀；可使用 `docs: 添加仓库贡献指南`。每次提交聚焦一个主题。PR 使用 `.github/PULL_REQUEST_TEMPLATE.md`，说明变更、涉及分类、图片来源和校验结果，关联相关 issue；图库改动附图片预览。

## 安全与配置 (Security & Configuration Tips)

禁止提交真实密钥、`.env`、私有图片或含敏感信息的响应。CLI 按进程环境、当前目录 `.env`、用户目录 `~/.env` 的顺序读取 `OPENAI_API_KEY`，已有环境变量优先。安全问题按 `SECURITY.md` 私下报告。
