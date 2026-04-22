# gpt-2-image-skill

OpenAI GPT Image 2 skill — curated prompt templates + CLI. Set `OPENAI_API_KEY` in env (or `~/.env`) before use.

## Install

**Claude Code** (plugin):

```shell
/plugin marketplace add wuyoscar/gpt_image_2_skill
/plugin install gpt-image@wuyoscar-skills
```

**Codex / other SKILL.md-aware agent** — clone into the agent's skills directory:

```bash
git clone https://github.com/wuyoscar/gpt_image_2_skill.git
```

Point the agent at `skills/gpt-image/SKILL.md` inside the clone.

**Build your own custom skill on top** — use the [skill-creator](https://github.com/anthropics/claude-skills) skill:

```
/skill-creator
> Please help me create a skill based on https://github.com/wuyoscar/gpt_image_2_skill
```

**CLI anywhere** (no agent needed):

```bash
uvx --from git+https://github.com/wuyoscar/gpt_image_2_skill gpt-image -p "a cat astronaut"

# or install to PATH
uv tool install git+https://github.com/wuyoscar/gpt_image_2_skill
gpt-image -p "a cat astronaut"
```

Requires [`uv`](https://github.com/astral-sh/uv) + Python ≥ 3.11. Deps auto-install.

---

## Showcase

All images produced one-shot at `--quality high`. Every prompt is in [`references/gallery.md`](references/gallery.md); captions below credit the original source so you can trace it.

### Chinese typography & posters

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-tea-poster.png" alt="Chinese tea-launch poster" /><br><em>Chinese tea-launch poster · community (<a href="https://mp.weixin.qq.com/s/ASxig6mFVYxrIE8-8Fthew">卡尔的AI沃茨</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-propaganda-poster.png" alt="1980s propaganda poster" /><br><em>1980s propaganda poster · community (<a href="https://x.com/akokoi1/status/2046558658096738672">@akokoi1</a>) + adapted</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-museum-infographic.png" alt="Museum-catalog infographic (唐代襦裙)" /><br><em>Museum-catalog infographic (唐代襦裙) · community (<a href="https://x.com/MrLarus/status/2045504669401653414">@MrLarus</a>)</em></td>
<td valign="top"><img src="docs/example-song-dynasty-feed.png" alt="Song Dynasty social-media feed (宋朝朋友圈)" /><br><em>Song Dynasty social-media feed (宋朝朋友圈) · community (<a href="https://x.com/Panda20230902/status/2045385588065313057">@Panda20230902</a>)</em></td>
</tr>
</table>

### Editorial & design posters

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-saul-bass-poster.png" alt="Saul-Bass-style thriller poster — THE LAST HEIR" /><br><em>Saul-Bass-style thriller poster · original (Bass lineage)</em></td>
<td width="50%" valign="top"><img src="docs/example-manga-relationship.png" alt="A Tale of Two Cities manga relationship map" /><br><em>Manga relationship map — <em>A Tale of Two Cities</em> · community (<a href="https://x.com/cht0001/status/2046920121239908380">@cht0001</a>)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-vogue-cover.png" alt="Vogue-style fashion magazine cover" /><br><em>Vogue-style fashion magazine cover · original</em></td>
<td valign="top"><img src="docs/example-pulp-scifi-cover.png" alt="1950s Astounding Stories pulp cover" /><br><em>1950s sci-fi pulp cover (Astounding Stories) · original</em></td>
</tr>
</table>

### Anime & manga

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-anime-jjk-action.png" alt="MAPPA-style anime action still (Jujutsu Kaisen aesthetic)" /><br><em>MAPPA-style anime action still · aesthetic ref: Jujutsu Kaisen</em></td>
<td width="50%" valign="top"><img src="docs/example-anime-naruto-clash.png" alt="Naruto-style ninja battle clash" /><br><em>Shōnen battle key-visual · aesthetic ref: Naruto Shippuden</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-manga-spread.png" alt="Shōnen manga two-page spread — basketball slam dunk" width="85%" /><br><em>Shōnen manga two-page spread (basketball dunk) · original, Slam-Dunk tradition</em></td>
</tr>
</table>

### Infographics & field guides

<table>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-encyclopedia-panda.png" alt="Giant Panda encyclopedia-style infographic" width="55%" /><br><em>Encyclopedia field guide (Giant Panda) · community (<a href="https://x.com/MrLarus/status/2046231542817497392">@MrLarus</a>)</em></td>
</tr>
</table>

### Product & food photography

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-product-chocolate-wafer.png" alt="Chocolate wafer JSON-style product render" /><br><em>Chocolate wafer product render (JSON-style) · community (<a href="https://x.com/mehvishs25/status/2020693181730598932">@mehvishs25</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-food-salad-explosion.png" alt="Salad explosion food photography" /><br><em>Salad-explosion food photo (JSON-style) · community (<a href="https://x.com/ChillaiKalan__">@ChillaiKalan__</a>)</em></td>
</tr>
</table>

### Gaming landscapes

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-hitman-openai.png" alt="Hitman-style gameplay at OpenAI HQ" /><br><em>Hitman gameplay — OpenAI HQ · community (<a href="https://x.com/flowersslop/status/2044734896321532390">@flowersslop</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-gta6-beach.png" alt="GTA 6 Vice City beach gameplay" /><br><em>GTA 6 gameplay — Vice City beach · community (<a href="https://x.com/WolfRiccardo/status/2041187268711321735">@WolfRiccardo</a>)</em></td>
</tr>
</table>

### Photorealism & reportage

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-photoreal-subway.png" alt="RAW iPhone subway photorealism" /><br><em>RAW iPhone — 42nd Street subway · community (<a href="https://x.com/WolfRiccardo/status/2041192232623972441">@WolfRiccardo</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-handwritten-notebook.png" alt="Handwritten notebook flatlay" /><br><em>Handwritten notebook flatlay · community (<a href="https://x.com/patrickassale/status/2044569086013718958">@patrickassale</a>)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-chess-midgame.png" alt="Chess board mid-game photorealism" /><br><em>Chess board mid-game · community (<a href="https://x.com/EddGorenstein/status/2046923077993259196">@EddGorenstein</a>)</em></td>
<td valign="top"><img src="docs/example-panorama-jungle.png" alt="360° equirectangular jungle panorama" /><br><em>360° equirectangular panorama · community (<a href="https://x.com/AIimagined/status/2046915800263802880">@AIimagined</a>)</em></td>
</tr>
</table>

### Cinematic & animation

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-pixar-kitchen.png" alt="Pixar-style kitten in kitchen" /><br><em>Pixar-style 3D still (kitten + soufflé) · community style pattern</em></td>
<td width="50%" valign="top"><img src="docs/example-noir-detective.png" alt="1940s film-noir detective photo" /><br><em>1940s film-noir still · original (Alton / Toland lineage)</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-storyboard.png" alt="6-panel film storyboard" width="85%" /><br><em>Professional 6-panel storyboard (Tokyo rooftop chase) · original</em></td>
</tr>
</table>

### Character design

<table>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-character-sheet.png" alt="Cyberpunk engineer character reference sheet" width="85%" /><br><em>Cyberpunk engineer reference sheet · community (<a href="https://x.com/MANISH1027512/status/2045013913901867334">@MANISH1027512</a>)</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-anime-expression-grid.png" alt="16-panel anime expression grid" width="55%" /><br><em>16-panel anime expression grid · community (<a href="https://mp.weixin.qq.com/s/ASxig6mFVYxrIE8-8Fthew">卡尔的AI沃茨</a>)</em></td>
</tr>
</table>

### Research paper figures

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-transformer-arch.png" alt="Transformer encoder-decoder architecture" /><br><em>Transformer encoder–decoder · Vaswani et al., 2017</em></td>
<td width="50%" valign="top"><img src="docs/example-rag-pipeline.png" alt="RAG pipeline diagram" /><br><em>Retrieval-Augmented Generation pipeline · Lewis et al., 2020</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-agent-architecture.png" alt="Multi-agent LLM system architecture" /><br><em>Multi-agent LLM system · AutoGen (Wu et al., 2023) / LangGraph / Managed Agents</em></td>
<td valign="top"><img src="docs/example-diffusion-chain.png" alt="Denoising diffusion chain" /><br><em>Denoising diffusion forward / reverse chain · Ho et al., 2020</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-scaling-curves.png" alt="Empirical scaling laws plot" /><br><em>Empirical scaling laws · Kaplan 2020, Chinchilla (Hoffmann et al., 2022)</em></td>
<td valign="top"><img src="docs/example-benchmark-heatmap.png" alt="Benchmark comparison heatmap" /><br><em>Benchmark comparison heatmap · HELM (Liang et al., 2023)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-ablation-bars.png" alt="Ablation bar chart with error bars" /><br><em>Ablation bar chart · generic reasoning-paper layout</em></td>
<td valign="top"><img src="docs/example-data-sankey.png" alt="Pretraining data-mixture sankey" /><br><em>LLM pretraining data-mixture sankey · GPT-3 / LLaMA / Pile compositions</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-attention-heatmap.png" alt="Multi-head attention heatmaps" /><br><em>Multi-head attention heatmaps · Clark et al., 2019</em></td>
<td valign="top"><img src="docs/example-model-timeline.png" alt="LLM family tree timeline" /><br><em>Frontier LLM lineage, 2018–2026 · community survey format</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-react-trace.png" alt="ReAct reasoning trace" width="60%" /><br><em>ReAct reasoning trace · Yao et al., 2022</em></td>
</tr>
</table>

---

## Acknowledgements

- **OpenAI** — the `gpt-image-2` model.
- [`ZeroLu/awesome-gpt-image`](https://github.com/ZeroLu/awesome-gpt-image) — community prompt archive, CC BY 4.0.
- [`ResearAI/AutoFigure`](https://github.com/ResearAI/AutoFigure) — related LLM scientific-figure project.

Per-image community `@handle` credits and per-prompt research-paper citations live inline in [`references/gallery.md`](references/gallery.md) and in each Showcase caption above — no need to duplicate them here.

---

## License

CC BY 4.0 — see [`LICENSE`](LICENSE).
