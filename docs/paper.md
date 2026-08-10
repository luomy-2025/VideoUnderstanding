# 第一个创新点：问题—选项联合证据规划与跨模态交互式关键帧检索

## 1. 大模型根据问题和选项生成查询

参考论文：[MSJoE: Jointly Evolving MLLM and Sampler for Efficient Long-Form Video Understanding](https://arxiv.org/pdf/2602.22932)

参考论文实验配置中的提示词，实现创新点中的证据查询生成。

## 2. 完成 180 帧粗粒度选帧

当前实现：[VideoVista-2 均匀采样基线](../baseline/baseline-videovista2.py)

使用与基线相同的 180 帧均匀采样配置。

## 3. 构造证据查询矩阵和视频视觉矩阵

证据查询作为 Q，视频帧作为 K 和 V。

参考论文：[Query-Dependent Video Representation for Moment Retrieval and Highlight Detection](https://arxiv.org/pdf/2303.13874)

开源仓库：[QD-DETR](https://github.com/wjun0830/QD-DETR)

论文流程：

```text
Text Query
     ↓
Cross Attention
     ↕
Video Clips
     ↓
Query-conditioned Video Representation
     ↓
Saliency / Moment Prediction
```

本项目目标：

```text
Evidence Queries
     ↓
Cross Attention
     ↕
180 Video Frames
     ↓
Evidence-conditioned Frame Representation
     ↓
Frame Selector
```

实现时参考 QD-DETR 的跨模态交互结构。

## 4. 计算 QKV 交互

参考论文：待补充。

## 5. 使用注意力生成帧分数

- 计算证据查询与视频帧之间的交叉注意力。
- 参考论文：待补充。
- 使用独立相关性评分头生成证据-帧分数
- 参考论文：待补充。
- 使用证据覆盖式选择器选择最终关键帧。
- 参考论文：待补充。
- 最终选出 `K=90` 帧。

# 第二个创新点：基于问题子步骤和选项支持—反驳关系的结构化证据推理网络

具体方案待补充。
