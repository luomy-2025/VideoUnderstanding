# 03 Decision Log

> Record only decisions that have been made. Each entry must include the reason and experimental impact.

## Entry template

### D-YYYYMMDD-01 — Decision title

- **Date:** YYYY-MM-DD
- **Status:** Proposed / Accepted / Rejected / Superseded
- **Decision:**
- **Reason:**
- **Alternatives considered:**
- **Rejected because:**
- **Experimental impact:**
- **Files/configs affected:**
- **Owner:**

## Current decisions

### D-001 — Research task remains long-video MCQ VideoQA

- **Status:** Accepted
- **Decision:** Keep the project focused on long-video multiple-choice VideoQA with Qwen3-VL.
- **Reason:** The contribution concerns evidence selection and evidence use under limited visual budgets.
- **Experimental impact:** Datasets, baselines, and metrics must stay aligned with MCQ VideoQA.

### D-002 — Innovation 1 is the implementation priority

- **Status:** Accepted
- **Decision:** Implement evidence planning and fixed-budget selection before structured evidence reasoning.
- **Reason:** Innovation 1 must be validated independently.
- **Experimental impact:** Preserve step IDs, frame IDs, timestamps, temporal constraints, and option contrasts.

### D-003 — Qwen3-VL is the unified answerer

- **Status:** Accepted
- **Decision:** All fair selector comparisons use the same exact Qwen3-VL checkpoint.
- **Reason:** Accuracy differences should be attributable to the selector.
- **Experimental impact:** Results with different backbones are context only, not causal evidence.

### D-004 — Main datasets

- **Status:** Accepted
- **Decision:** Use LongVideoBench-Val, Video-MME Long, and MLVU-Dev MCQ.
- **Reason:** They provide complementary long-context, temporal, cross-domain, holistic, and multi-detail evaluation.
- **Experimental impact:** LongVideoBench-Val is the main development/ablation dataset.

### D-005 — Main modality setting

- **Status:** Accepted
- **Decision:** Main experiments use frames only, without subtitles or audio.
- **Reason:** The contribution is visual evidence selection.
- **Experimental impact:** Subtitle/audio results are supplementary only.

### D-006 — Main frame budget

- **Status:** Accepted
- **Decision:** Use `K=16` in the main controlled table and test `K=8,32`.
- **Reason:** A fixed budget is required for selector comparison.
- **Experimental impact:** Overview frames and neighbor expansion count toward the same total budget.

### D-007 — AKS is the first published baseline to reproduce

- **Status:** Accepted
- **Decision:** Reproduce AKS before modifying its code.
- **Reason:** It has open code and is closely aligned with query-aware fixed-budget selection.
- **Experimental impact:** The reproduction report must precede `AKS + Qwen3-VL`.

### D-008 — First implementation is training-free

- **Status:** Accepted
- **Decision:** Use a frozen planner, similarity matrices, temporal rules, and greedy set selection first.
- **Reason:** It isolates the hypothesis and reduces implementation risk.
- **Rejected alternatives:** RL, GRPO, end-to-end QKV selector, multi-agent iterative search.
- **Experimental impact:** Trainable selectors are considered only after a positive training-free result.

### D-009 — No correct-answer leakage at inference

- **Status:** Accepted
- **Decision:** The selector sees the question and all options but not the correct option identity.
- **Reason:** Prevent answer leakage.
- **Experimental impact:** Correct answers may later be used only for teacher supervision.

### D-010 — Planner text is hidden from the answerer in the main experiment

- **Status:** Accepted
- **Decision:** The main answerer receives selected frames, the original question, and the original options only.
- **Reason:** Isolate selection gains from language-prompt gains.
- **Experimental impact:** `Ours + Plan text` is a separate ablation.
