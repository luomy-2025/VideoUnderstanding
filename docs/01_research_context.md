# 01 Research Context

## Research task

Long-video multiple-choice VideoQA.

- Input: long video `V`, question `Q`, candidate options `O={O1,...,Oc}`
- Backbone: Qwen3-VL
- Goal: under a fixed frame/visual-token budget, select answer-discriminative evidence and support structured reasoning.

## Scientific questions

### SQ1 — Select the right evidence

Existing methods mainly use uniform sampling, fixed FPS, or question-frame relevance. But:

> Question relevance is not equal to answer discriminativeness.

We study how to jointly understand the question and all options, convert option differences into observable evidence requirements, and select a low-redundancy evidence set that covers key subgoals under a fixed visual budget.
凝练1：现有长视频问答方法中，均匀采样缺乏问题导向，
而基于相关性的检索采样容易产生证据集中，难以在有限视觉预算下完整覆盖回答问题所需的关键证据。

### SQ2 — Use the selected evidence well

Selected frames are often concatenated chronologically without explicitly modeling:

- reasoning substeps;
- frames/clips;
- temporal relations;
- candidate options;
- support, refutation, conflict, complementarity, precedence, and causality.

The current phase focuses on SQ1 while preserving `step_id`, frame index, timestamp, option contrast, temporal constraint, and evidence type for SQ2.
凝练2：现有长视频问答方法通常对视觉证据进行扁平化拼接与聚合，
缺乏对证据间逻辑关系及证据与问题子目标之间关联的深层推理。

## Innovation 1

**Chinese:** 选项对比式证据规划与固定预算集合选帧  
**English:** Option-Contrastive Evidence Planning and Budgeted Set Selection

### Core novelty

Jointly analyze visually observable differences among all candidate options, convert them into structured and executable evidence requirements, and select a compact evidence set that:

- covers evidence subgoals;
- discriminates among options;
- satisfies temporal constraints;
- reduces redundancy;
- stays within a fixed frame budget.
  


### Do not claim as novelty by itself

- generating multiple queries;
- using candidate options;
- building a query-frame matrix;
- ordinary QKV attention;
- diversity-aware sampling;
- CLIP Top-K retrieval.

## Minimum viable method

```text
Video + Question + All Options
        ↓
One-shot evidence planning
        ↓
2–4 executable evidence subgoals
        ↓
Query–Frame relevance matrix
+
Option-Hypothesis–Frame matrix
        ↓
Budgeted set selection:
coverage + discriminativeness + temporal complementarity - redundancy
        ↓
K selected frames
        ↓
Qwen3-VL answers the original MCQ
```

## Innovation 2


## Datasets

1. LongVideoBench-Val — main development and ablation set
2. Video-MME Long — cross-domain generalization; no subtitles/audio
3. MLVU-Dev multiple-choice subset — holistic/single-detail/multi-detail

## Baselines

### External published baselines

- AKS
- BOLT
- MDP3
- Q-Frame, if reproducible

### Internal controls/ablations

1. Uniform Sampling
2. Question-only Top-K
3. Question+Options Top-K
4. Planning + Independent Top-K
5. Planning + Option Discriminativeness
6. Planning + Temporal Constraints
7. Planning + Set-wise Selection
8. Full Ours

## Fair-comparison constraints

All controlled selector comparisons use the same:

- Qwen3-VL checkpoint
- dataset split
- candidate frame pool
- final frame budget
- resolution
- prompt
- generation settings
- answer parser
- subtitle/audio setting

## Engineering route

1. Reproduce AKS with its official setup.
2. Validate the evaluation pipeline with a model that has public results.
3. Replace the answerer with Qwen3-VL.
4. Obtain `AKS + Qwen3-VL`.
5. Implement Uniform, Question-only, and Question+Options.
6. Add evidence planning.
7. Add option-discriminative scoring.
8. Add temporal constraints.
9. Add fixed-budget set-wise selection.
