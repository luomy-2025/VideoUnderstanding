# VideoVista-2 基线

## 文件职责

- `baseline/baseline-videovista2.py`：数据读取、媒体消息构造、模型推理和断点续跑逻辑。
- `config/baseline/config.toml`：数据、模型、结果文件、推理参数和提示词配置。
- `scripts/test.sh`：基线运行入口与日志重定向。

## 配置结构

`config/baseline/config.toml` 包含以下配置表：

| 配置表 | 内容 |
| --- | --- |
| `paths` | 问题文件、视频根目录、结果文件和模型目录 |
| `runtime` | 当前进程可见的 CUDA 物理设备编号 |
| `model` | vLLM 初始化参数、图像像素上限、视频采样帧数和多模态缓存预算 |
| `generation` | 温度、核采样概率、最大生成长度和重复惩罚 |
| `prompt` | 多项选择题的回答格式指令 |
| `logging` | `test.sh` 使用的日志文件路径 |

文件系统路径可以使用绝对路径。相对路径以配置文件所在目录为基准解析。

## CUDA 设备

运行前通过 `nvidia-smi` 查看四张显卡的占用情况，然后将 `runtime.cuda_device` 手动设置为 `0`、`1`、`2` 或 `3`。程序会在导入 vLLM 前设置 `CUDA_VISIBLE_DEVICES`，因此只会使用指定的物理显卡；该显卡在当前进程中会重新编号为 `cuda:0`。

单卡运行时，`model.tensor_parallel_size` 必须保持为 `1`。修改设备编号后直接重新执行 `bash scripts/test.sh` 即可生效。

## 视频编码器缓存

基线保持 `model.num_frames = 180`。180 帧经过当前模型处理后约产生 10800 个视频视觉 token，超过 vLLM 默认预分配的 8192 个编码器缓存 token，因此使用以下配置扩大多模态预算：

```toml
[model.limit_mm_per_prompt]
video = 2
```

该配置会作为 `limit_mm_per_prompt={"video": 2}` 传入 vLLM，不会减少实际采样帧数。提高该值会增加多模态编码器缓存占用，当前配置仅用于覆盖单个 180 帧视频的视觉 token。

## 运行与日志

在已经准备好项目依赖和模型运行环境后执行：

```bash
bash scripts/test.sh
```

脚本可以从任意工作目录启动。它会将 `config/baseline/config.toml` 传给 Python 程序，并从同一配置文件的 `logging.log_file` 读取日志路径。运行时的标准输出和标准错误会显示在终端，并追加写入日志文件。每次启动和正常结束都会记录时间。

结果以 JSON 列表写入 `paths.save_path`。程序按 `question_id` 跳过已有的有效结果；带 `error` 或预测为空的历史记录会在下次启动时自动重试。程序在每道题处理后通过临时文件原子更新结果文件。
