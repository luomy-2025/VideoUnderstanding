# 文档索引

每个知识点只由下表中的一个文件负责维护。其他文档引用该知识点时只添加链接，不重复说明。

| Owner 文件 | 负责内容 | 更新时机 |
| --- | --- | --- |
| [research_context.md](research_context.md) | 研究任务、科学问题、创新点、数据集和公平比较边界 | 研究方向或总体方法发生变化时 |
| [experiment-tree.md](experiment-tree.md) | 创新点一的技术路线、训练边界和模块结构 | 方法设计或模块职责发生变化时 |
| [paper.md](paper.md) | 各实现步骤对应的论文与开源仓库 | 增删参考方法或调整借鉴范围时 |
| [baseline.md](baseline.md) | VideoVista-2 基线的配置、运行方式和输出约定 | 基线配置或运行入口发生变化时 |
| [PROGRESS.md](PROGRESS.md) | 当前开发状态、已知问题和下一步工作 | 开发状态发生变化时 |

实验结果不在参考文档中重复记录，以 `experiments/<name>/summary.json` 为准。
