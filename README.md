# Fabric 提示词中文目录 · Fabric Patterns Chinese Catalog

[danielmiessler/Fabric](https://github.com/danielmiessler/Fabric) 全部 Pattern（提示词）的**中文索引**：
逐个依据每个 Pattern 的 `system.md` 原文撰写中文简介与使用场景，每条附**源仓库原文直达链接**，并**每日自动与上游同步**。

- 📖 在线目录（可搜索）：GitHub Pages `docs/index.html`
- 📄 Markdown 目录：[catalog.md](catalog.md)
- 🧩 机器可读数据：[data/patterns.json](data/patterns.json)（含英文名、中文标题/简介、场景、官方标签、源文件链接、内容哈希）

## 为什么做这个

Fabric 是优秀的开源提示词框架，但它的 260+ 个 Pattern 全是英文、平铺在仓库目录里，
中文用户很难快速判断「哪个 Pattern 是干嘛的、我该用哪个」。
本项目只做一件事：**给每个 Pattern 配一份看得懂的中文说明书和一条直达原文的链接**，
不复制、不改写提示词本体——需要用的时候，点链接回源仓库取原文。

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
  "status": "translated"
}
```

分组（12 组）：安全攻防 / 开发与代码 / 可视化生成 / 摘要总结 / 信息提取 /
AI 与提示词工程 / 商业与产品 / 学习与研究 / 个人成长与身心 / 写作与文本加工 /
分析与批判性思维 / 格式转换与其他。分组按上游官方标签归并，仅作浏览辅助。

## 每日同步机制

GitHub Actions（`.github/workflows/sync.yml`）每天北京时间约 09:17 运行
`scripts/sync_upstream.py`：

1. 拉取上游最新 commit，与 `data/patterns.json` 中记录的 commit 比对，无变化直接结束；
2. 有变化时按每个 `system.md` 的内容哈希做三路 diff：
   - **新增** → 建条目，`status` 标为 `pending_translation`，简介先填官方英文描述占位；
   - **内容变更** → 保留中文简介，`status` 标为 `needs_review`；
   - **删除** → 条目移除；
3. 重新生成 `catalog.md` 与 `docs/index.html`，同步报告写入 `sync_reports/`，自动提交回主分支。

脚本只负责**发现和标记**，中文简介由人工/LLM 补写后把 `status` 改为 `translated`
再运行 `python3 scripts/build_catalog.py` 重新渲染。这样自动同步永远不会把已写好的中文覆盖掉。

本地手动同步：

```bash
python3 scripts/sync_upstream.py            # 联网拉上游比对
python3 scripts/build_catalog.py            # 仅重新渲染目录
```

## 参与贡献

- 发现某个 Pattern 的中文简介不准确 → 直接改 `data/patterns.json` 对应条目，跑一次
  `build_catalog.py`，提 PR（请勿手改 `catalog.md` / `docs/index.html`，它们是生成物）。
- `sync_reports/` 里标出的 `pending_translation` / `needs_review` 条目就是待办清单，欢迎认领。

## 许可与归属

- 上游 Fabric 及其全部 Pattern 为 MIT 许可，版权属于 Daniel Miessler 及贡献者，见 [NOTICE.md](NOTICE.md)。
- 本项目的中文简介、分组与代码为原创，采用 MIT 许可，见 [LICENSE](LICENSE)。
- 本项目与上游无隶属关系，仅为社区索引项目。
