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
| `model` | vLLM 初始化参数、图像像素上限和视频采样帧数 |
| `generation` | 温度、核采样概率、最大生成长度和重复惩罚 |
| `prompt` | 多项选择题的回答格式指令 |
| `logging` | `test.sh` 使用的日志文件路径 |

文件系统路径可以使用绝对路径。相对路径以配置文件所在目录为基准解析。

## 运行与日志

在已经准备好项目依赖和模型运行环境后执行：

```bash
bash scripts/test.sh
```

脚本可以从任意工作目录启动。它会将 `config/baseline/config.toml` 传给 Python 程序，并从同一配置文件的 `logging.log_file` 读取日志路径。运行时的标准输出和标准错误会显示在终端，并追加写入日志文件。每次启动和正常结束都会记录时间。

结果以 JSON 列表写入 `paths.save_path`。程序按 `question_id` 跳过已有结果，并在每道题处理后通过临时文件原子更新结果文件。
