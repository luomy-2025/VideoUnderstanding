# 02 Experiment Protocol

> Record only fixed experimental settings here. Update this file before running experiments.

## Version

- Protocol version: `v0.1`
- Last updated: `YYYY-MM-DD`
- Owner:
- Git commit:

## Models

### Answerer

- Model family: Qwen3-VL
- Exact checkpoint: `TBD`
- Precision:
- Inference framework:
- Device:
- Max visual tokens:
- Max text tokens:

### Validation model

- Model family:
- Exact checkpoint:
- Public reference result:
- Source:

### Planner

- Exact checkpoint:
- Text-only or overview-aware:
- Temperature: `0`
- `do_sample`: `false`
- `max_new_tokens`: `512`

### Vision-text encoder

- Exact checkpoint:
- Feature dimension:
- Frame preprocessing:
- Feature normalization:

## Datasets

### LongVideoBench-Val

- Split:
- Number of evaluated samples:
- Use subtitles: `No`
- Use audio: `No`
- Metric: Accuracy
- Evaluation script/version:

### Video-MME Long

- Split: Long
- Number of evaluated samples:
- Use subtitles: `No`
- Use audio: `No`
- Metric: Long Accuracy
- Evaluation script/version:

### MLVU-Dev

- Split: Dev
- Task subset: Multiple-choice only
- Number of evaluated samples:
- Use subtitles: `No`
- Use audio: `No`
- Metric:
- Evaluation script/version:

## Frame protocol

- Candidate pool size `N`: `128`
- Main frame budget `K`: `16`
- Additional budgets: `8, 32`
- Candidate sampling rule:
- Timestamp policy:
- Decode backend:
- Frame resolution:
- Aspect-ratio handling:
- Duplicate-frame handling:

## Unified answer prompt

```text
You are given chronologically ordered video frames.

Question:
{question}

Options:
{options}

Answer with only the option letter.
```

- Timestamp text included: `Yes/No`
- Evidence plan shown to answerer: `No`

## Generation settings

- Temperature:
- Top-p:
- Top-k:
- Repetition penalty:
- Max new tokens:
- Seed:
- Runs per sample:

## Answer parsing

- Allowed outputs:
- Regex:
- Invalid-output policy:
- Tie policy:
- Missing-answer policy:

## Selector settings

### Uniform

- Rule:

### Question-only Top-K

- Query template:
- Similarity:
- Top-K policy:
- Temporal reordering: `Yes`

### Question+Options Top-K

- Query template:
- Similarity:
- Top-K policy:
- Temporal reordering: `Yes`

### AKS

- Repository:
- Commit:
- Config:
- Backbone:
- Frame budget:

### Ours

- Evidence steps: `2–4`
- Relevance weight `alpha`:
- Discriminativeness weight `beta`:
- Temporal weight `gamma`:
- Redundancy weight `lambda`:
- Coverage weight:
- Short-clip neighbor radius:
- Routing rule:

## Required output record

```json
{
  "sample_id": "",
  "video_id": "",
  "question": "",
  "options": [],
  "gold_answer": "",
  "predicted_answer": "",
  "is_correct": false,
  "selector": "",
  "candidate_frame_ids": [],
  "selected_frame_ids": [],
  "selected_timestamps": [],
  "planner_output": {},
  "visual_tokens": 0,
  "feature_time_s": 0.0,
  "selection_time_s": 0.0,
  "answer_time_s": 0.0,
  "total_time_s": 0.0,
  "error_type": ""
}
```

## Reproducibility checklist

- [ ] Exact checkpoint names recorded
- [ ] Git commit recorded
- [ ] Dataset versions recorded
- [ ] Same frame budget across selectors
- [ ] Same prompt across selectors
- [ ] Same answer parser across selectors
- [ ] No subtitles/audio in the main setting
- [ ] Correct option not used at inference
- [ ] Planner output not shown to the answerer in the main setting
- [ ] Invalid outputs logged
- [ ] Latency and visual-token use logged
