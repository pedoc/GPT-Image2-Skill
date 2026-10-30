# GPT Image Skills

[English](README.md) | [中文](README.zh.md)

两个可独立安装的 Agent Skill，用于图片生成、编辑与提示词提取。

| Skill | 用途 |
| --- | --- |
| [`gpt-image`](skills/gpt-image/SKILL.md) | 使用自带的 uv 脚本生成、编辑图片 |
| [`get-prompt-from-image`](skills/get-prompt-from-image/SKILL.md) | 从用户提供的参考图提取可复用提示词 |

## 安装 Skill

将完整的 `skills/gpt-image/` 或 `skills/get-prompt-from-image/` 目录复制到 Agent 运行时的 skills 目录。保留其中的 `SKILL.md`、`references/`、`agents/` 及 `scripts/`，包括脚本锁文件。可以单独安装，也可以同时安装两个 Skill。

生图 Skill 需要 `uv`、Python 3.11+ 和 `OPENAI_API_KEY`。提示词提取 Skill 由具备图片理解能力的 Agent 执行，本身不需要 Python 环境。

## 通过 Agent 使用

用 `$gpt-image` 描述生图或编辑需求；用 `$get-prompt-from-image` 附上参考图并提取提示词。生图 Skill 确认模型后直接执行自身的 `scripts/generate.py`。

可选模型包括 `gpt-image-2`、`gpt-image-2.5-flare` 和 `gpt-image-2.5-sunburst`。参数兼容性与验证范围见 Skill 的[模型说明](skills/gpt-image/references/models.md)。

## 直接运行自带脚本

在仓库根目录执行：

```bash
uv run --locked skills/gpt-image/scripts/generate.py --help

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

在环境变量中配置 `OPENAI_API_KEY`。脚本依次读取进程环境、当前工作目录 `.env`、用户目录 `~/.env`，已有变量优先。API 调用可能产生费用，禁止提交密钥及私有输入、输出图片。

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
