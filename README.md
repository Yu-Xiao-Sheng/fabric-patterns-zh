# Fabric 提示词中文目录 · Fabric Patterns Chinese Catalog

[danielmiessler/Fabric](https://github.com/danielmiessler/Fabric) 全部 Pattern（提示词）的**中文索引 + 全文译版**：
逐个依据每个 Pattern 的 `system.md` 原文撰写中文简介与使用场景，并把提示词全文翻译为中文，
每条附**源仓库原文直达链接**，并**每日自动与上游同步**（新增与变更的译版随同步更新）。

- 📖 在线目录（可搜索）：GitHub Pages `docs/index.html`
- 📄 Markdown 目录：[catalog.md](catalog.md)
- 🇨🇳 中文版提示词：[patterns-zh/](patterns-zh/)（每个 Pattern 一个 `system.zh.md`，与原文一一对应，可直接取用）
- 🧩 机器可读数据：[data/patterns.json](data/patterns.json)（含英文名、中文标题/简介、场景、官方标签、源文件链接、内容哈希、中文版路径）

## 为什么做这个

Fabric 是优秀的开源提示词框架，但它的 260+ 个 Pattern 全是英文、平铺在仓库目录里，
中文用户很难快速判断「哪个 Pattern 是干嘛的、我该用哪个」，把英文提示词直接喂给国内模型时效果也常打折。
本项目做两件事：**给每个 Pattern 配一份看得懂的中文说明书和一条直达原文的链接**，
外加**一份可直接取用的中文版提示词全文**（`patterns-zh/<name>/system.zh.md`，保留原文结构与输出格式约束）。
中文版为上游 MIT 许可文本的翻译衍生，版权归属见 [NOTICE.md](NOTICE.md)。

## 数据长什么样

```json
{
  "name": "extract_wisdom",
  "zh_title": "提取人生智慧",
  "zh_desc": "从文本中提取令人意外、有洞察力的智慧内容……",
  "scenario": "从长内容中淘金提炼时",
  "tags": ["EXTRACT", "WISDOM", "SELF"],
  "group": "信息提取",
  "source_url": "https://github.com/danielmiessler/Fabric/blob/main/data/patterns/extract_wisdom/system.md",
  "upstream_path": "data/patterns/extract_wisdom/system.md",
  "content_hash": "…",
  "zh_prompt": "patterns-zh/extract_wisdom/system.zh.md",
  "zh_base_hash": "…（译版所依据的原文哈希）",
  "status": "translated"
}
```

分组（12 组）：安全攻防 / 开发与代码 / 可视化生成 / 摘要总结 / 信息提取 /
AI 与提示词工程 / 商业与产品 / 学习与研究 / 个人成长与身心 / 写作与文本加工 /
分析与批判性思维 / 格式转换与其他。分组按上游官方标签归并，仅作浏览辅助。

## 每日同步机制

由维护者侧的自动化任务每天运行 `scripts/sync_upstream.py` 并完成翻译：

1. 拉取上游最新 commit，与 `data/patterns.json` 中记录的 commit 比对，无变化直接结束；
2. 有变化时按每个 `system.md` 的内容哈希做三路 diff：
   - **新增** → 建条目，并翻译中文简介与提示词全文；
   - **内容变更** → 重新翻译该条中文版全文（靠 `zh_base_hash` 与 `content_hash` 对账，已是最新版的绝不重译）；
   - **删除** → 条目与对应中文版一并移除；
3. 重新生成 `catalog.md` 与 `docs/index.html`，同步报告写入 `sync_reports/`，自动提交回主分支。

本地手动同步：

```bash
python3 scripts/sync_upstream.py            # 联网拉上游比对（只标记，不翻译）
python3 scripts/build_catalog.py            # 仅重新渲染目录
```

## 参与贡献

- 发现某个 Pattern 的中文简介不准确 → 直接改 `data/patterns.json` 对应条目，跑一次
  `build_catalog.py`，提 PR（请勿手改 `catalog.md` / `docs/index.html`，它们是生成物）。
- 中文版提示词译得不准 → 直接改 `patterns-zh/<name>/system.zh.md` 提 PR。

## 许可与归属

- 上游 Fabric 及其全部 Pattern 为 MIT 许可，版权属于 Daniel Miessler 及贡献者，见 [NOTICE.md](NOTICE.md)。
- 本项目的中文简介、分组与代码为原创，采用 MIT 许可，见 [LICENSE](LICENSE)；中文版提示词（`patterns-zh/`）为上游 MIT 文本的翻译衍生作品，同样以 MIT 提供，原版权归上游作者所有。
- 本项目与上游无隶属关系，仅为社区索引项目。
