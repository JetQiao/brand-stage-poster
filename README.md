# Brand Stage Poster · 品牌舞台海报

[![Tests](https://github.com/JetQiao/brand-stage-poster/actions/workflows/test.yml/badge.svg)](https://github.com/JetQiao/brand-stage-poster/actions/workflows/test.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/JetQiao/brand-stage-poster)](https://github.com/JetQiao/brand-stage-poster/releases/latest)

**填好需求，上传图片，生成你的品牌舞台海报。**

默认白色发光巨字、红色背光、超宽舞台与镜面反射；也可切换暗红立体字。适合品牌发布、团队亮相和活动主视觉，支持人物比例协调、四角文字、自由度调整与连续修改。

![默认白字红光品牌舞台](assets/preview.png)

*AI 生成的无人物示例，使用通用占位文案。[查看实际提示词](examples/preview-prompt.md)。有原始 Logo 时可加入中央标志，没有 Logo 也能制作。*

这是开源 Skill，需要在**支持 Skill 且具备图像生成／编辑能力的宿主**中使用。Skill 负责把需求整理成制作规则；生图能力和额度由宿主提供。普通出图无需安装 Python，也无需填写 JSON。

## 第一步：安装一次

在支持 Skill 安装的 Codex 环境中，复制下面这段发送：

```text
$skill-installer
请安装 https://github.com/JetQiao/brand-stage-poster 中的 Skill。
入口 SKILL.md 在仓库根目录，仓库内路径为 .，安装名称为 brand-stage-poster。
安装到我的个人目录 ~/.agents/skills/brand-stage-poster。
如果已经安装，请告诉我实际路径和版本，不要重复安装。
```

安装成功后，在下一条消息中使用 `$brand-stage-poster`。未出现时重启宿主再试。安装位置、自动发现和调用方式参见 [OpenAI 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)。其他支持 Agent Skills 的宿主，按其安装说明使用本仓库。

<details>
<summary>手动安装：Git 或下载 ZIP</summary>

macOS / Linux 有 Git 时可执行：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/JetQiao/brand-stage-poster.git ~/.agents/skills/brand-stage-poster
```

不使用 Git 时，前往 [最新版本](https://github.com/JetQiao/brand-stage-poster/releases/latest)，下载附件中的 `brand-stage-poster-v版本号.zip` 并解压，把整个 `brand-stage-poster` 文件夹放进个人 Skill 目录。

- macOS / Linux：`~/.agents/skills/brand-stage-poster/`
- Windows：用户目录下的 `.agents\skills\brand-stage-poster\`
- 仅当前项目使用：项目的 `.agents/skills/brand-stage-poster/`

最终应直接存在 `brand-stage-poster/SKILL.md`，不要多嵌套一层文件夹。只选一个安装位置；旧环境可能装在 `~/.codex/skills/`，已有安装请沿用实际路径。

</details>

## 第二步：准备图片

| 你想做什么 | 需要上传什么 | 怎样说明 |
| --- | --- | --- |
| 只有品牌文字的舞台 | 无需图片 | 写准确的主文字，并说“无人物” |
| 用自己的团队 | 清晰合照，或每人的单独照片 | 说明总人数、从左到右的顺序；分开上传时标注图 1、图 2 分别是谁 |
| 加入已有 Logo | 清晰原始 Logo，优先透明背景 PNG | 写“这张是 Logo”；宿主支持时也可用 SVG |
| 接近某种背景 | 一张风格参考图 | 写“这张只参考背景和灯光” |
| 修改上一张海报 | 待修改的海报 | 写“这张是编辑底图”，再说明哪里要改 |

人物面部尽量清楚、无遮挡。希望做全身海报时优先给全身照；只有半身照也可以制作，但新增的下半身是生成补全。Logo、人物原照和风格参考可以一起发送，注明各自用途即可。

## 第三步：复制模板，填好后连同图片发送

### 简单版：第一次用这段就够了

把 `【】` 中的内容替换为自己的需求，不需要的项删除或填“无”。

```text
$brand-stage-poster
品牌／主题：【你的品牌名】
主文字：【希望画面上准确出现的文字】
人物：【无，或合照中的两人／图1和图2各一人】
Logo：【无，或已上传的哪张图】
请用白字红光舞台，人物身材比例自然协调，其他按默认生成一张。
```

例如，**无需任何图片**就能发送：

```text
$brand-stage-poster
品牌：NOVA LAB
主文字：左侧 NOVA，右侧 LAB
人物：无
Logo：无
请按默认生成一张品牌舞台海报。
```

未填写时默认：**1 张、约 2.22:1 超宽横版、白字红光、自由度 50、无人物、四角无文字**。指定人物时，新建海报默认自然协调身材比例、保留原有衣着。

### 完整版：按需控制每个细节

可整段复制，只改需要的部分。示例占位说明不会作为画面文案；未填写的可选项采用默认值。

```text
$brand-stage-poster
请根据以下参数和我上传的图片制作海报。

品牌／主题：【品牌名称或活动主题】
主文字：【准确文字；可指定“左侧…，右侧…”】
人物：【无，或人数及对应照片】
人物顺序：【从左到右；不填则沿用合照】
Logo：【无，或对应附件】
背景参考：【无，或对应附件，仅参考背景风格】

背景风格：白字红光
画幅：2.22:1
自由度：50
身材比例：自然协调
服装：保留原照
张数：1

左上文字：【可不填】
右上文字：【可不填】
左下文字：【可不填】
右下文字：【可不填】

必须保持：【例如人物长相、眼镜、发型、Logo结构、指定文字】
其他要求：【例如改冷蓝灯光、全身站姿、保留搭肩动作】
```

| 参数 | 怎样填写 | 不填时 |
| --- | --- | --- |
| 品牌／主题、主文字 | 使用准确中英文和大小写；可分别指定左、右主字 | 品牌内容不明确时会补问 |
| 人物、顺序 | “无”“合照两人”“图 2 在左，图 1 在右” | 无人物；使用合照时沿用原左右顺序 |
| Logo、背景参考 | 指出对应附件；两者用途分开 | 无图形 Logo，使用默认舞台 |
| 背景风格 | “白字红光”或“暗红立体字” | 白字红光 |
| 画幅 | `2.22:1`、`16:9`、`1:1`、`9:16` 等 | 新建约 2.22:1；编辑保留底图比例 |
| 自由度 | 0–100，或“严格／平衡／探索” | 50，平衡 |
| 身材比例 | “自然协调”“保持原样”或具体要求，如“略显修长，保持相对身高” | 新建有人物时自然协调；局部编辑沿用原样 |
| 服装 | “保留原照”或指定款式、颜色 | 保留原照 |
| 四角文字 | 按左上／右上／左下／右下填写，可只填一角 | 空白、无、未替换的占位说明均不添加 |
| 张数 | 1，或明确要几个方向 | 1 |
| 必须保持 | 想锁定的脸部特征、文字、动作、颜色、服装等 | 保留准确品牌内容及人物身份特征 |

这些是给助手看的需求参数，不是图像 API 的数值选项。画幅为构图要求，实际分辨率以输出文件为准。

## 人物比例怎么调

默认“自然协调”会适度调整头身视觉关系、肩身关系、四肢透视、姿态和站位，让人物融入舞台；保留可辨认的长相和原有相对身高，不自动瘦脸或夸张拉腿。可以直接追加：

```text
人物身材比例保持原样，只修改背景。
```

或：

```text
两人身材略显修长，肩身比例自然，保留两人的相对身高和原有长相。
```

明确锁定身体或只改文字、背景时，不会因为默认比例选项而额外改动身体。生成模型仍可能重绘面部，出图后应对照原照检查；身材调整不是像素级保护。

## 四角文字怎么填

可以只用一两个角，也可以填满四角。例如：

```text
左上文字：NOVA LAB
右上文字：MAKE IDEAS REAL
左下文字：DESIGN / TOOLS / PEOPLE
右下文字：TEAM 2026
```

文字按位置排版、留出边距，字号低于主文字，不遮住人脸和 Logo。需要多行时说明换行位置。公司全称、网址、日期、平台名等请填写准确内容，不会自动照抄风格参考。

没有想好文案，也可以说“帮我写四角文案，主题是让创意成为现实”。只有明确要求代写时才会创作，并记录实际采用的文字；不会杜撰公司信息或网址。

## 风格与自由度怎么选

| 风格 | 视觉特征 | 示例 |
| --- | --- | --- |
| **白字红光，默认** `white-red` | 白色发光巨字、红背光、分层灯带、明亮红白镜面反射 | [图片](assets/preview.png) · [提示词](examples/preview-prompt.md) |
| 暗红立体字 `dark-red` | 暗红实体字、明显立体侧面、深黑空间、克制反射 | [图片](assets/preview-dark-red.png) · [提示词](examples/preview-dark-red-prompt.md) |

| 档位 | 数值／常用值 | 适合什么情况 |
| --- | --- | --- |
| 严格 | 0–30／20 | 尽量接近参考的布局、视角和氛围 |
| 平衡 | 31–70／50 | 保持风格，调整字与人物尺度、灯光和舞台深度 |
| 探索 | 71–100／80 | 探索更明显的构图、空间和材质变化 |

风格、自由度与锁定分别控制。自由度高不会自动改写文案、换人或解除你锁定的颜色；数字也不代表准确率。切换风格时，具体颜色、材质要求仍然优先。

## 出图后，直接在同一对话里修改

不用重填全部参数；保留或重新附上编辑底图，说明变化即可。

```text
只把右侧主字改成 STUDIO，其他文字、人物、服装和背景保持。
```

```text
把右上文字改成 BUILD SOMETHING GREAT，其他三角和主文字不变。
```

```text
两人换同款黑色连帽卫衣，身材自然协调，保留长相、眼镜、发型和搭肩动作。
```

```text
给我两个新构图，自由度 80。人物、Logo、全部文字和白字红光配色保持。
```

满意后需要大尺寸文件，可以说：

```text
不重新生成，把这张 PNG 保持比例导出长边 4096。
```

仅导出使用本地重采样，不改变海报内容；不是原生 4K 或 AI 超分。一般先确认内容，再导出尺寸。

## 更新 Skill

复制下面一段给助手即可，不需要重新填写海报需求：

```text
请将已安装的 brand-stage-poster 更新到最新版本。
官方仓库：https://github.com/JetQiao/brand-stage-poster
先确认实际安装位置和当前版本，再按 Git 或 ZIP 安装方式更新。
保留我的自定义修改、人物素材和历史输出，更新后告诉我新旧版本及实际路径。
```

新版本也可用 `$brand-stage-poster` 发起上述请求。助手需具备本地文件和联网能力才能执行；它会在更新前识别安装方式。已有本地修改时先保留并说明冲突，不会直接覆盖。普通出图不会自动更新 Skill。

<details>
<summary>手动更新，以及查看当前版本</summary>

**Git 安装：** 先检查实际安装目录的来源和改动。下面以个人目录为例；若装在别处，替换为实际路径。

```bash
git -C ~/.agents/skills/brand-stage-poster remote get-url origin
git -C ~/.agents/skills/brand-stage-poster status --short --branch
```

确认来源是 `JetQiao/brand-stage-poster`、当前分支是 `main`，且没有本地改动或自建提交后执行：

```bash
git -C ~/.agents/skills/brand-stage-poster pull --ff-only origin main
```

如果显示冲突或无法快进，保留现场，让助手处理，不使用强制重置。

**ZIP / 下载式安装：** 下载 [最新 Release 附件](https://github.com/JetQiao/brand-stage-poster/releases/latest)，解压到临时目录；先把旧安装完整备份到 Skill 扫描目录之外，再用新版本替换官方文件。自定义内容、素材和输出需要保留；存在同名修改时先合并，不直接覆盖。只有 Skill Installer 安装记录、没有 Git 元数据时也按此方式处理。

**查看版本：** 打开实际安装目录的 `SKILL.md`，查看开头 `metadata.version`。更新后可让助手重新读取它；宿主未显示新内容时再重启。详细执行规则见 [更新流程](references/updating.md)。

</details>

从本次 **v1.1.1** 起，后续更新按补丁号递增：`1.1.1 → 1.1.2 → 1.1.3`，已发布的版本标签保持不变。

## 常见问题

| 问题 | 怎么处理 |
| --- | --- |
| 安装后找不到 Skill | 检查是否直接存在 `brand-stage-poster/SKILL.md`，避免重复嵌套和重复安装；重启宿主再试 |
| 只有提示词，没有图片 | 当前宿主可能没有图像工具；需在具备生图能力的环境中使用，安装 Skill 本身不会增加生图功能 |
| 人不像、身体比例不合适 | 提供更清晰原照，指出具体偏差；可以要求保持原身材或只调整姿态，避免反复整图重绘 |
| 文字错误或太小 | 给准确文字与位置，减少过长小字，明确只修该处；生成后仍要逐字检查 |
| 想保持原图完全不变 | 普通生图无法保证未编辑区域逐像素不变；仅尺寸导出不调用生图工具 |
| 想换蓝光、换衣服 | 直接写具体要求，例如“白字冷蓝光”“同款黑色圆领卫衣”，其优先级高于默认风格 |

## 独立使用尺寸导出工具

只有本地尺寸导出需要 **Python 3.10+ 和 Pillow**。在仓库目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/export_4k.py \
  --input /path/to/poster.png \
  --output-dir ./output \
  --prefix my-brand \
  --long-edge 4096
```

Windows 可使用 `py -m venv .venv`，随后在 PowerShell 执行 `.venv\Scripts\Activate.ps1`。

- 输出 `<prefix>_long-edge-4096.png` 和 `<prefix>_export.json`，横竖图按长边缩放。
- 加 `--uhd`，额外生成 3840×2160 的 `<prefix>_uhd.png`，保持比例、居中加黑边，不裁切。
- 默认拒绝覆盖已有输出；`--overwrite` 允许替换输出，始终禁止覆盖输入文件。
- 使用 Lanczos 重采样；报告记录实际尺寸、是否缩放和留边。

## 包内结构与贡献

```text
SKILL.md                       代理执行入口
agents/openai.yaml             名称与默认调用示例
references/                    风格控制、制作流程、提示词、验收与更新
scripts/export_4k.py            独立尺寸导出
assets/                        公开风格示例、README 收款码
examples/                      示例的实际提示词与来源说明
tests/                         导出与包结构测试
```

生成任务的记录、图片和素材保存在任务输出目录；`output/`、`private/` 和 `dist/` 默认被 Git 忽略。仓库不附带团队原照、私人品牌包或密钥；收款码由作者明确提供，仅用于 README 支持入口。

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

测试验证导出行为、输入保护和包内引用，不调用生图服务。真实出图仍需视觉核验，示例不能证明所有人物、品牌或自由度档位都稳定成功。欢迎通过 Issue 或 PR 反馈，附上宿主、提示词、预期和实际结果，并只提交有权公开的素材。

## License

[MIT](LICENSE) © 2026 JetQiao。代码和文档按 MIT 协议开放；项目作者对仓库内 AI 示例图可许可的权益也按同一协议提供。第三方商标、肖像与用户自行提供的素材不属于本仓库的许可范围。

## 请我喝杯咖啡

如果对您有帮助，可以请我喝杯咖啡

<a href="assets/wechat-coffee.jpg"><img src="assets/wechat-coffee.jpg" alt="微信收款码：请我喝杯咖啡" width="280"></a>
