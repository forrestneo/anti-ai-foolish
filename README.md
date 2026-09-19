<div align="center">

# anti-ai-foolish

**反AI傻味 · 去AI终检**

🇨🇳 **简体中文** | 🇬🇧 [English](README.en.md)

</div>



**反AI傻味·去AI终检** —— 一个用真实检测报告训练出来的去AI味工具。

不是又一份"AI高频词清单"。这是目前唯一一个在 **52 个腾讯朱雀实测片段（人工标签）** 上做过全量 A/B 验证（95% 置信区间）的去AI味 skill：1108 条规则逐条测试，只有过了统计检验的才标 confirmed。

```
文稿 → preflight 机械筛 → 骨架检查 → 七刀手术 → 复检 → ✅可发 / ❌停下手术
```

---

## 为什么它和市面上的"去AI味"工具不一样

发布前我们评测了 21 个同类 skill（skillhub / clawhub / skills.sh / 虾评四源，含下载量 22 万的头部产品），结论：

| 市售工具的通病 | 本工具 |
|---|---|
| 没有一个见过真实检测标签 | 52 片段朱雀实测语料做回归测试床 |
| 词表堆到几百条，语料上零确认 | 词表类 90+ 条在 A/B 测试中全军覆没——本工具如实标注 |
| 分不开人写和AI写（真人文本 19 分 ≈ AI 稿 23 分） | Z 分分类器：AI 段召回 **97%**（36/37） |
| 教你加口语词、加修辞"更显人味" | 实测这些全是反的（见下） |

## 三条被实测推翻的流行常识

1. **排比是AI味？反了。** 口语重复排比（"车厘子都降价了，耙柑也降价了"）在人写文本里密度更高（r=-0.37 过CI）。真正有害的只有一种变体：论证对称金句（"可以X，却不能Y"×3）。
2. **加"说白了/要我说"能降分？不护体。** r=-0.25，AI 稿也满篇口语锚。装出来的口语（"你品你细品"）实测出现在 0.99 的段落里。
3. **删心理描写很重要？过时了。** AI 已经学会不写"他知道"，这个维度 r=-0.24。

**我们确认的真信号**（95%CI，n=52）：冒号（r=+0.43，最强单项）、概念引用腔（给术语加引号，AI 是人的 5.5 倍）、疑问句密度、破折号——以及决定性的那条 ↓

## 核心发现：骨架-燃料定律

同一作者、同一母题的两篇文章：

- 亲历做骨架（"我过节回老家，亲戚说楼房不交物业费"）→ 朱雀 **0.09**
- 概念体系做骨架、真事当例子 → **0.75 ~ 0.995**

决定分数的不是谁的口吻、用什么词，是**骨架是"谁在做什么"还是"一个概念在推演"**。全部 16 条规律见 `skills/anti-ai-foolish/references/`。

## 实战成绩

- 未手术 AI 稿（朱雀实测 0.91 / 0.93）→ preflight 正确拦截"停下手术" ✓
- 手术后稿件 → 门 7/7 放行 ✓，朱雀复测主体段落进入**人工特征区间**（AIGC 0.14）
- 13 篇存量稿件全流程手术后全部通过机械门

## 仓库内容：两个独立产物

```
anti-ai-foolish-skill/     ① 纯 Skill（标准 Agent Skill 格式）
anti-ai-foolish-plugin/    ② ZCode 插件（.zcode-plugin + skills）
marketplace.json           本地市场清单（指向②）
```

两者内容完全一致，按你的环境二选一。

### ① 作为纯 Skill 安装（Claude Code / Codex / ZCode 等任何支持 Agent Skills 的工具）

把 `anti-ai-foolish-skill/` 整个目录复制进你的技能目录并改名：

```bash
# ZCode
cp -r anti-ai-foolish-skill ~/.zcode/skills/anti-ai-foolish
# Claude Code
cp -r anti-ai-foolish-skill ~/.claude/skills/anti-ai-foolish
```

### ② 作为 ZCode 插件安装（本地市场）

```
Plugin Marketplace → Add → 粘贴本仓库根目录（含 marketplace.json）
→ Personal → anti-ai-foolish → Install
```

依赖：Python 3.8+，纯标准库 + RapidOCR（仅验证语料更新时需要）。规则引擎零依赖、离线运行、不上传任何文本。

## 使用

```bash
# 发文前一键终检（六硬门 + Z分 + 人味弹药 → 可发/改后复检/停下手术）
python pipelines/preflight.py 你的文章.md

# 全规则扫描（AI命中按危级分层，每条带修法与豁免提示）
python engine/scanner.py 你的文章.md

# 语料更新后全量重验（新检测报告OCR进 validation/corpus/ 后跑）
python validation/abtest.py
```

工作流四步：①机械筛（preflight）→ ②人工判据（经历之我vs姿态之我、人是不是主体、论证对称排比——机器测不了的三条）→ ③七刀手术（按块1000-2000字：冒号→概念引用腔→数据罗列→金句对称→结构→词表→装人回填）→ ④复检+平台实测。

## 项目结构

```
anti-ai-foolish-skill/               # 纯 Skill（插件内为同名目录）
├── SKILL.md                         # 四步工作流 + 铁律 + 已反转常识 + 验证声明
├── engine/scanner.py                # 规则引擎（1108规则→扫描→Z分报告）
├── pipelines/preflight.py           # 发文终检管线
├── rules/                           # 13个规则分库（每条带status/evidence/fix/exempt）
├── validation/abtest.py             # 全量规则A/B重验框架（语料更新即重估）
└── references/                      # 方法论、证据链、评测报告、路线图

anti-ai-foolish-plugin/
├── .zcode-plugin/plugin.json        # ZCode 插件清单
└── skills/anti-ai-foolish/          # 同上，插件封装
```

规则五态标注：`confirmed`（过CI的AI/人味信号）/ `reversed`（方向反转）/ `directional` / `no_signal` / `insufficient`——**没验证过的规则不冒充有效**。

## 诚实声明（边界）

- 分类器召回 97%、特异 53%——它是**发布质量门**，宁可误拦不放过；Z<0 不等于"证明是人写的"
- 机械部分的相关系数上限约 0.8，剩余方差靠人工判据（SKILL.md 第二步）
- 语料文体为中文自媒体评论；换文体（网文/公文）请重跑 `validation/abtest.py` 重估
- 本工具做语言层优化，不做事实伪造——所有修法以不改变事实与原意为前提

## ⚠️ 发布前注意（fork/搬运者必读）

`validation/corpus/zhuque_corpus.json` 含检测报告原文片段，`references/` 含内部工作档案。公开发布自己的副本前，请确认这些内容对你和提供语料的合作者无隐私影响，必要时删除这两个目录——工具主体（rules + engine + pipelines + SKILL.md）不依赖它们即可运行。

## License

MIT
