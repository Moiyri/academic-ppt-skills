# Academic PPT Skills

一个用于论文分享、课题汇报和学位答辩的 Codex 技能。它覆盖新建可编辑PPT、按模板修订已有PPT，以及编写和更新逐页演讲者备注。

## 使用

将仓库内容放到 Codex 可发现的 `academic-ppt` 技能目录，保留 `SKILL.md`、`agents/`、`references/` 和 `scripts/` 的相对位置。例如，可将仓库克隆到项目的 `.agents/skills/academic-ppt`，再从该项目调用 `$academic-ppt`。

> 使用 $academic-ppt，根据论文和已有模板拟一份组会PPT大纲，先给我审阅。

> 使用 $academic-ppt，保留现有幻灯片的正文和版式，先整理逐页讲稿。

新建、局部修订和写备注各有对应流程。生图、PPTX编辑和渲染依赖当前 Codex 环境提供的工具。

## 仓库入口

- [SKILL.md](SKILL.md) 定义技能的适用范围、制作流程和交付检查。
- [叙事与逐页结构](references/narrative.md)、[生图与真实证据](references/images.md)和[重建与验收](references/rebuild.md)提供各阶段的详细说明。
- [逐页讲稿与演讲者备注](references/speaker-notes.md)说明口播写法、科学口径和写回步骤。

## 本地检查

以下辅助脚本使用 Python 标准库。在仓库根目录执行：

```sh
python scripts/outline_batches.py 17
python scripts/inspect_pptx.py path/to/deck.pptx
```

第一个脚本输出连续的分镜页码组。第二个检查PPTX对象结构，视觉效果仍需打开或渲染检查。维护技能时，可用 Codex 自带的 `skill-creator` 校验脚本检查 `SKILL.md`。
