# Repository Guidelines

## 项目结构与职责 (Project Structure & Module Organization)

- `skills/gpt-image/scripts/generate.py` 是完整生成脚本，负责参数校验、请求路由和图片保存。
- `skills/gpt-image/` 包含生成技能与 `references/`；保持单一脚本入口，避免新增独立 CLI 包、命令探测和安装回退。
- `skills/get-prompt-from-image/` 存放图片反推提示词的技能与分析指南。
- `tests/` 存放离线测试；`pyproject.toml` 与 `uv.lock` 管理仓库环境，脚本相邻锁文件管理独立 Skill 的依赖。

调整脚本参数时，同步 `--help` 与技能说明。

## 本地开发与校验命令 (Build, Test, and Development Commands)

使用 Python 3.11+ 和 `uv`，在仓库根目录执行：

仓库是 uv 非打包项目，使用 `pyproject.toml` 与 `uv.lock`；Skill 单独复制时使用脚本内联依赖与 `generate.py.lock`。依赖变更需同步两处声明并重新执行 `uv lock` 和 `uv lock --script skills/gpt-image/scripts/generate.py`。仅检查帮助不会发送生成请求。

| 命令 | 用途 |
| --- | --- |
| `uv sync --locked` | 按锁文件准备仓库环境 |
| `uv run --locked skills/gpt-image/scripts/generate.py --help` | 检查技能脚本 |
| `uv run --locked python -m unittest discover -s tests -v` | 运行全部离线测试 |
| `uv run --locked python -m py_compile skills/gpt-image/scripts/generate.py` | 检查 Python 语法 |
| `git diff --check` | 检查空白字符问题 |

## 编码风格与命名 (Coding Style & Naming Conventions)

Python 使用四空格缩进；函数、变量和模块使用 `snake_case`，类使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`。沿用现有类型注解和标准库优先的写法。仓库未配置专用格式化或 lint 工具，避免引入整文件格式化改动。技能和参考文件使用小写连字符命名，例如 `skills/gpt-image/references/gallery-photography.md`。

## 测试约定 (Testing Guidelines)

测试采用标准库 `unittest`，文件命名为 `tests/test_*.py`，方法命名为 `test_*`。修改脚本时，为参数边界、生成与编辑路由、请求序列化、错误退出码及凭据优先级补充相关回归用例；同时验证脚本复制到仓库外仍可运行。沿用临时目录、假密钥和模拟 HTTP transport，保持测试离线。当前没有覆盖率百分比门槛；真实出图验证需单独记录。

## 参考资料与双语文档 (References & Bilingual Documentation)

遵循 `CONTRIBUTING.md`，安装和使用方式变更时同步 `README.md` 与 `README.zh.md`。提示词存放在技能的 `references/` 分类文件中，维护 `gallery.md` 的索引范围和计数，保留 `Curated` 或 `Author + Source` 署名。仓库仅维护 Skill、脚本和纯文本参考资料，不添加生成图片、预览图库或样张运行记录。检查本地 Markdown 链接，避免遗留已删除资源的引用。

## 提交与 Pull Request (Commit & Pull Request Guidelines)

默认使用中文沟通，Git 提交信息优先中文。历史提交多用简短祈使句，也有 `docs:`、`feat:` 前缀；可使用 `refactor: 精简技能运行入口`。每次提交聚焦一个主题。PR 使用 `.github/PULL_REQUEST_TEMPLATE.md`，说明行为变化、涉及技能、参考资料来源和校验结果，关联相关 issue；脚本改动补充相关回归测试。

## 安全与配置 (Security & Configuration Tips)

禁止提交真实密钥、`.env`、私有图片或含敏感信息的响应。脚本按进程环境、当前目录 `.env`、用户目录 `~/.env` 的顺序读取 `OPENAI_API_KEY`，已有环境变量优先。安全问题按 `SECURITY.md` 私下报告。
