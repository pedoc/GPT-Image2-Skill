# GPT Image Skills

[English](README.md) | [中文](README.zh.md)

两个可独立安装的 Agent Skill，用于图片生成、编辑与提示词提取。

| Skill | 用途 |
| --- | --- |
| [`gpt-image`](skills/gpt-image/SKILL.md) | 使用自带的 uv 脚本生成、编辑图片 |
| [`get-prompt-from-image`](skills/get-prompt-from-image/SKILL.md) | 从用户提供的参考图提取可复用提示词 |

## 安装 Skill

将完整的 `skills/gpt-image/` 或 `skills/get-prompt-from-image/` 目录复制到 Agent 运行时的 skills 目录。保留其中的 `SKILL.md`、`references/`、`agents/` 及 `scripts/`，包括脚本锁文件。可以单独安装，也可以同时安装两个 Skill。

生图 Skill 需要 `uv`、Python 3.11+ 和图片服务 API Key。提示词提取 Skill 由具备图片理解能力的 Agent 执行，本身不需要 Python 环境。

## 一次配置图片服务

为运行 Agent 的用户创建 `~/.config/GPT-Image2-Skill/config.toml`。Windows 下通常为 `C:\Users\<用户名>\.config\GPT-Image2-Skill\config.toml`。同一用户安装的各份 Skill 共用这个文件，不依赖当前项目目录。仓库提供了[配置模板](skills/gpt-image/config.example.toml)：

```toml
base_url = "https://gateway.example/v1"
api_key = "你的图片服务密钥"
model = "gpt-image-2"
timeout = 600
```

`base_url` 填网关的 API 基地址，包含其要求的路径前缀。脚本会追加 `/images/generations` 或 `/images/edits`；网关需要兼容 OpenAI Images API，编辑还需要支持 multipart 上传，仅支持文字 Chat/Responses 的网关不适用。`model` 可以填写网关提供的准确图片模型别名；`timeout` 为 API 请求超时秒数。

各字段独立解析，优先级从左到右：

| 配置项 | 命令行 | 图片专用环境变量 | TOML 字段 | 兼容回退 |
| --- | --- | --- | --- | --- |
| API Key | — | `GPT_IMAGE_API_KEY` | `api_key` | `OPENAI_API_KEY` |
| Base URL | `--base-url` | `GPT_IMAGE_BASE_URL` | `base_url` | `OPENAI_BASE_URL`，再到 OpenAI 官方地址 |
| 模型 | `--model` | `GPT_IMAGE_MODEL` | `model` | `gpt-image-2` |
| 超时 | `--timeout` | `GPT_IMAGE_TIMEOUT` | `timeout` | 600 秒 |

图片配置文件优先于通用 `OPENAI_*` 值，避免宿主 Agent 的文字模型密钥和地址覆盖图片服务。建议将图片密钥和地址一起配置。原有 `.env` 加载顺序保持为：进程环境、当前目录 `.env`、用户目录 `~/.env`，已有变量优先。

可以通过 `--config /path/to/config.toml` 或 `GPT_IMAGE_CONFIG` 选择其他文件，命令行优先。显式指定的文件不存在或配置无效时，会在请求前报错停止；默认文件不存在时继续使用兼容回退。`--help` 不读取配置，也不发送请求。

用户目录以脚本实际运行用户为准；容器或远程 Agent 使用那边的用户目录，需要挂载文件或指定路径。脚本不读取其他 Agent 的主模型设置，也不会自动读取 Skill 安装目录下的配置。真实配置保存在仓库之外，不要打印密钥。

## 通过 Agent 使用

告诉 Agent 使用 `gpt-image` 并描述生图或编辑需求，或使用 `get-prompt-from-image` 附上参考图提取提示词。支持 `$skill-name` 的运行时也可使用 `$gpt-image` 和 `$get-prompt-from-image`。生图默认使用已配置的模型，用户指定其他模型时覆盖，并直接执行自身的 `scripts/generate.py`。

可选模型包括 `gpt-image-2`、`gpt-image-2.5-flare` 和 `gpt-image-2.5-sunburst`。参数兼容性与验证范围见 Skill 的[模型说明](skills/gpt-image/references/models.md)。

## 直接运行自带脚本

在仓库根目录执行：

```bash
uv run --locked skills/gpt-image/scripts/generate.py --help

# 使用已保存的图片连接和模型
uv run --locked skills/gpt-image/scripts/generate.py -p "一张植物海报"

# 生成一张图片
uv run --locked skills/gpt-image/scripts/generate.py \
  --model gpt-image-2.5-flare -p "一张标题为 GARDEN 的植物海报" \
  --size portrait --quality medium -f poster.png

# 编辑用户提供的参考图
uv run --locked skills/gpt-image/scripts/generate.py \
  --model gpt-image-2.5-sunburst -p "将天空替换为极光" \
  -i photo.jpg -f aurora.png
```

使用已安装的 Skill 时，替换为自身脚本的实际路径。`uv` 根据脚本内联声明及相邻的 `generate.py.lock` 准备依赖。

临时覆盖地址可传 `--base-url https://gateway.example/v1`，使用其他连接可传 `--config /path/to/config.toml`，均不会修改已保存的文件。API 调用可能产生费用，禁止提交密钥及私有输入、输出图片。

更多选项包括可重复的 `-i`、透明度掩码 `-m`、`--format` 和 `--background`，详见 `--help` 与 [SKILL.md](skills/gpt-image/SKILL.md)。成功时打印输出路径，错误写入 stderr；退出码 `0` 表示成功，`1` 表示 API 失败，`2` 表示参数错误或缺少凭据。

## 仓库结构

```text
skills/gpt-image/              生图、编辑 Skill，自带脚本和参考资料
skills/get-prompt-from-image/  图片反推提示词 Skill 和分析指南
tests/                        脚本与凭据的离线测试
pyproject.toml                uv 项目依赖声明
uv.lock                       仓库与测试环境锁文件
```

提示词参考资料采用纯文本，按需加载。编辑示例使用用户自行提供的输入图片。仓库不保存生成图片和样张运行记录。

## 开发与校验

```bash
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m py_compile skills/gpt-image/scripts/generate.py
git diff --check
```

修改依赖时，同步更新 `pyproject.toml` 与脚本内联声明，再执行 `uv lock` 和 `uv lock --script skills/gpt-image/scripts/generate.py`。

其他约定见 [CONTRIBUTING.md](CONTRIBUTING.md)、[SECURITY.md](SECURITY.md) 和 [LICENSE](LICENSE)。
