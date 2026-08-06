具体做法就是：**把这三份 Markdown 文件作为项目的长期上下文文件维护，而不是每次重新复制整段聊天。**

我已经先给你生成了一套可直接使用的模板：

* [下载三份文件打包版](sandbox:/mnt/data/video_research_context_pack.zip)
* [01_research_context.md](sandbox:/mnt/data/video_research_context_pack/01_research_context.md)
* [02_experiment_protocol.md](sandbox:/mnt/data/video_research_context_pack/02_experiment_protocol.md)
* [03_decision_log.md](sandbox:/mnt/data/video_research_context_pack/03_decision_log.md)

## 一、这三份文件分别管什么

### `01_research_context.md`

这是**长期不频繁变动的研究总纲**，里面放：

* 研究任务；
* 两个科学问题；
* 两个创新点；
* 当前优先实现创新点一；
* 数据集；
* Backbone；
* Baseline；
* 当前拟定的方法流程；
* 不允许偏移的研究边界。

它相当于告诉新窗口：

> 我们研究什么、为什么研究、当前方案是什么、哪些方向不要再讨论。

这份文件只有研究方向发生明显变化时才更新。

---

### `02_experiment_protocol.md`

这是**实验固定配置表**，用于保证所有人跑出来的结果可复现。

里面需要填写：

* Qwen3-VL具体Checkpoint；
* Planner模型；
* CLIP或其他视觉编码器；
* 数据集版本和划分；
* 是否使用字幕和音频；
* 候选帧数`N`；
* 最终帧预算`K`；
* 图像分辨率；
* Prompt；
* 生成参数；
* 答案解析规则；
* AKS代码Commit；
* 你们方法的超参数。

这份文件的原则是：

> 每次正式跑实验之前先更新协议，再运行代码。

例如你们最终确定：

```yaml
answerer: Qwen3-VL-8B-Instruct
candidate_frames: 128
selected_frames: 16
subtitles: false
audio: false
temperature: 0
```

就必须写进去，不能只在聊天或口头会议里说。

---

### `03_decision_log.md`

这是**研究决策记录**，用于防止以后反复讨论已经决定的问题。

每次做出重要决定就增加一条，例如：

```markdown
### D-20260804-01 — 主实验固定使用16帧

- Date: 2026-08-04
- Status: Accepted
- Decision: 主结果固定K=16，补充实验使用K=8和32。
- Reason: 保证Selector公平比较，并控制Qwen3-VL推理成本。
- Alternatives considered: K=32作为主设置。
- Rejected because: 计算成本较高，早期实验迭代较慢。
- Experimental impact: Uniform、AKS、Ours都必须使用16帧。
```

以后有人问：

> 为什么不用32帧作为主实验？

直接查看Decision Log即可，不需要重新争论。

---

# 二、放在哪里

最推荐同时保存两份。

## 方案一：放进GitHub项目

建议目录：

```text
your_project/
├── docs/
│   ├── 01_research_context.md
│   ├── 02_experiment_protocol.md
│   └── 03_decision_log.md
├── configs/
├── datasets/
├── selectors/
├── planner/
├── answerer/
└── evaluation/
```

这样这些文件会和代码一起版本管理。

修改后正常提交：

```bash
git add docs/
git commit -m "update research context and experiment protocol"
git push
```

这是最可靠的保存方式。

---

## 方案二：上传到当前ChatGPT项目

进入当前“视频理解”项目，在项目的来源区域选择添加文件，把这三份文件上传进去。ChatGPT项目支持把文件、聊天和项目指令集中放在同一个工作区，后续项目内的新聊天可以继续使用这些来源。([OpenAI Help Center][1])

官方还支持将某条重要回复直接保存为项目来源，菜单名称可能显示为“Save to project”或“Add to project sources”。([OpenAI Help Center][1])

操作顺序：

1. 下载上面的ZIP；
2. 解压；
3. 打开当前“视频理解”项目；
4. 找到项目来源或添加文件的位置；
5. 上传三个`.md`文件；
6. 在项目内创建新聊天。

---

# 三、新窗口第一句话怎么写

新窗口不要再粘贴所有历史对话，只需要写：

```text
请先阅读项目中的以下三份文件：

1. 01_research_context.md
2. 02_experiment_protocol.md
3. 03_decision_log.md

后续回答必须严格基于这三份文件继续。

当前任务：
请帮助我实现创新点一中的“问题—选项联合证据规划与固定预算集合选帧”，先从Planner JSON和Query–Frame矩阵开始，不要重新讨论研究方向。
```

这样新窗口就会先获取：

* 研究背景；
* 已定实验设置；
* 已做决策；
* 当前具体任务。

---

# 四、日常怎么维护

建议固定一个维护规则。

## 每次导师或师兄开会之后

更新：

```text
03_decision_log.md
```

记录会议中真正确定的事项。

例如：

* 第三个数据集改成MLVU；
* 主预算从16改成32；
* AKS复现结果差异超过2个百分点；
* Planner由文本模型改成Qwen3-VL概览帧模式。

---

## 每次正式实验前

更新：

```text
02_experiment_protocol.md
```

检查：

* 模型版本；
* 数据集版本；
* 帧数；
* Prompt；
* 参数；
  -代码Commit。

---

## 研究方向或方法框架变化时

才更新：

```text
01_research_context.md
```

例如：

* 科学问题重新凝练；
* 创新点一方法发生重大调整；
* 增加或删除数据集；
* 第二创新点正式启动。

不要每天修改这份文件。

---

# 五、推荐再增加一个实验结果文件

后续可以再增加：

```text
04_experiment_results.md
```

结构例如：

```markdown
# Experiment Results

## EXP-001

- Date:
- Git commit:
- Dataset:
- Model:
- Selector:
- N:
- K:
- Accuracy:
- Selection time:
- Answer time:
- Notes:

## Conclusion

- 是否超过Uniform：
- 是否超过AKS：
- 失败原因：
- 下一步：
```

这样四份文件就构成完整研究记录：

```text
01_research_context.md
    研究什么

02_experiment_protocol.md
    实验怎么跑

03_decision_log.md
    为什么这样决定

04_experiment_results.md
    实验跑出了什么
```

当前先把前三份上传到项目和GitHub仓库，然后在新窗口中要求它先读取这三份文件再继续。

[1]: https://help.openai.com/en/articles/10169521-chatgpt-projects?utm_source=chatgpt.com "Projects in ChatGPT | OpenAI Help Center"
