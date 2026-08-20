from __future__ import annotations

import argparse
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, TypedDict, cast

from tqdm import tqdm
from vllm import LLM, SamplingParams


class DatasetItem(TypedDict):
    question_id: str
    question: str
    video_path: NotRequired[str]
    image_path: NotRequired[str]


class MediaUrl(TypedDict):
    url: str


class MediaContent(TypedDict, total=False):
    type: str
    video_url: MediaUrl
    image_url: MediaUrl
    text: str


class ChatMessage(TypedDict):
    role: str
    content: list[MediaContent]


class Prediction(TypedDict):
    prediction: str


class StoredPrediction(Prediction):
    question_id: str
    error: NotRequired[str]


TomlTable = dict[str, object]


@dataclass(frozen=True)
class PathConfig:
    question_file: Path
    video_base_dir: Path
    save_path: Path
    model_path: Path


@dataclass(frozen=True)
class ModelConfig:
    trust_remote_code: bool
    tensor_parallel_size: int
    max_model_len: int
    async_scheduling: bool
    max_pixels: int
    num_frames: int


@dataclass(frozen=True)
class GenerationConfig:
    temperature: float
    top_p: float
    max_tokens: int
    repetition_penalty: float


@dataclass(frozen=True)
class PromptConfig:
    answer_instruction: str


@dataclass(frozen=True)
class BaselineConfig:
    paths: PathConfig
    model: ModelConfig
    generation: GenerationConfig
    prompt: PromptConfig


@dataclass(frozen=True)
class CliArguments:
    config: Path


def require_table(table: TomlTable, key: str) -> TomlTable:
    value = table.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"配置项 [{key}] 必须是表")
    return cast(TomlTable, value)


def require_string(table: TomlTable, key: str, section: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"配置项 [{section}].{key} 必须是非空字符串")
    return value


def require_integer(table: TomlTable, key: str, section: str) -> int:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"配置项 [{section}].{key} 必须是整数")
    return value


def require_positive_integer(table: TomlTable, key: str, section: str) -> int:
    value = require_integer(table, key, section)
    if value <= 0:
        raise ValueError(f"配置项 [{section}].{key} 必须大于 0")
    return value


def require_number(table: TomlTable, key: str, section: str) -> float:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"配置项 [{section}].{key} 必须是数字")
    return float(value)


def require_positive_number(table: TomlTable, key: str, section: str) -> float:
    value = require_number(table, key, section)
    if value <= 0:
        raise ValueError(f"配置项 [{section}].{key} 必须大于 0")
    return value


def require_boolean(table: TomlTable, key: str, section: str) -> bool:
    value = table.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"配置项 [{section}].{key} 必须是布尔值")
    return value


def resolve_path(raw_path: str, config_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return (config_dir / path).resolve()


def load_config(config_path: Path) -> BaselineConfig:
    resolved_config_path = config_path.expanduser().resolve()
    with resolved_config_path.open("rb") as config_file:
        raw_config: object = tomllib.load(config_file)

    if not isinstance(raw_config, dict):
        raise ValueError("配置文件的顶层结构必须是表")

    config = cast(TomlTable, raw_config)
    paths = require_table(config, "paths")
    model = require_table(config, "model")
    generation = require_table(config, "generation")
    prompt = require_table(config, "prompt")
    config_dir = resolved_config_path.parent

    temperature = require_number(generation, "temperature", "generation")
    if temperature < 0:
        raise ValueError("配置项 [generation].temperature 不能小于 0")

    top_p = require_number(generation, "top_p", "generation")
    if not 0 < top_p <= 1:
        raise ValueError("配置项 [generation].top_p 必须在 (0, 1] 范围内")

    return BaselineConfig(
        paths=PathConfig(
            question_file=resolve_path(
                require_string(paths, "question_file", "paths"), config_dir
            ),
            video_base_dir=resolve_path(
                require_string(paths, "video_base_dir", "paths"), config_dir
            ),
            save_path=resolve_path(
                require_string(paths, "save_path", "paths"), config_dir
            ),
            model_path=resolve_path(
                require_string(paths, "model_path", "paths"), config_dir
            ),
        ),
        model=ModelConfig(
            trust_remote_code=require_boolean(
                model, "trust_remote_code", "model"
            ),
            tensor_parallel_size=require_positive_integer(
                model, "tensor_parallel_size", "model"
            ),
            max_model_len=require_positive_integer(
                model, "max_model_len", "model"
            ),
            async_scheduling=require_boolean(
                model, "async_scheduling", "model"
            ),
            max_pixels=require_positive_integer(model, "max_pixels", "model"),
            num_frames=require_positive_integer(model, "num_frames", "model"),
        ),
        generation=GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            max_tokens=require_positive_integer(
                generation, "max_tokens", "generation"
            ),
            repetition_penalty=require_positive_number(
                generation, "repetition_penalty", "generation"
            ),
        ),
        prompt=PromptConfig(
            answer_instruction=require_string(
                prompt, "answer_instruction", "prompt"
            )
        ),
    )


def create_llm(config: BaselineConfig) -> LLM:
    return LLM(
        model=str(config.paths.model_path),
        trust_remote_code=config.model.trust_remote_code,
        tensor_parallel_size=config.model.tensor_parallel_size,
        allowed_local_media_path=str(config.paths.video_base_dir),
        max_model_len=config.model.max_model_len,
        async_scheduling=config.model.async_scheduling,
        mm_processor_kwargs={"max_pixels": config.model.max_pixels},
        media_io_kwargs={"video": {"num_frames": config.model.num_frames}},
    )


def create_sampling_params(config: GenerationConfig) -> SamplingParams:
    return SamplingParams(
        temperature=config.temperature,
        top_p=config.top_p,
        max_tokens=config.max_tokens,
        repetition_penalty=config.repetition_penalty,
    )


def build_media_content(
    item: DatasetItem, video_base_dir: Path
) -> list[MediaContent]:
    content: list[MediaContent] = []

    if item.get("video_path"):
        video_full_path = (video_base_dir / item["video_path"]).resolve()
        content.append(
            {
                "type": "video_url",
                "video_url": {"url": video_full_path.as_uri()},
            }
        )

    if item.get("image_path"):
        image_full_path = (video_base_dir / item["image_path"]).resolve()
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_full_path.as_uri()},
            }
        )

    return content


def process_item(
    item: DatasetItem,
    llm: LLM,
    sampling_params: SamplingParams,
    video_base_dir: Path,
    answer_instruction: str,
) -> Prediction:
    prompt = f"{item['question']} \n{answer_instruction}"

    content = build_media_content(item, video_base_dir)
    content.append({"type": "text", "text": prompt})
    messages: list[ChatMessage] = [{"role": "user", "content": content}]

    outputs = llm.chat(
        messages=messages,
        sampling_params=sampling_params,
        use_tqdm=False,
    )
    response = outputs[0].outputs[0].text.strip()
    return {"prediction": response}


def load_existing_outputs(save_path: Path) -> list[StoredPrediction]:
    if not save_path.exists():
        return []
    with save_path.open("r", encoding="utf-8") as json_file:
        try:
            raw_outputs: object = json.load(json_file)
        except json.JSONDecodeError:
            return []

    if not isinstance(raw_outputs, list):
        return []

    outputs: list[StoredPrediction] = []
    for raw_output in raw_outputs:
        if not isinstance(raw_output, dict):
            continue
        output = cast(dict[str, object], raw_output)
        question_id = output.get("question_id")
        prediction = output.get("prediction")
        if not isinstance(question_id, str) or not isinstance(prediction, str):
            continue

        stored_output: StoredPrediction = {
            "question_id": question_id,
            "prediction": prediction,
        }
        error = output.get("error")
        if isinstance(error, str):
            stored_output["error"] = error
        outputs.append(stored_output)
    return outputs


def save_outputs(outputs: list[StoredPrediction], save_path: Path) -> None:
    tmp_path = save_path.with_name(f"{save_path.name}.tmp")
    with tmp_path.open("w", encoding="utf-8") as json_file:
        json.dump(outputs, json_file, indent=3, ensure_ascii=False)
    tmp_path.replace(save_path)


def load_dataset(question_file: Path) -> list[DatasetItem]:
    with question_file.open("r", encoding="utf-8") as json_file:
        raw_data: object = json.load(json_file)

    if not isinstance(raw_data, list):
        raise ValueError("问题文件的顶层结构必须是列表")

    data: list[DatasetItem] = []
    for index, raw_item in enumerate(raw_data):
        if not isinstance(raw_item, dict):
            raise ValueError(f"第 {index} 条问题不是对象")
        item = cast(dict[str, object], raw_item)
        question_id = item.get("question_id")
        question = item.get("question")
        if not isinstance(question_id, str) or not isinstance(question, str):
            raise ValueError(f"第 {index} 条问题缺少字符串类型的 question_id 或 question")

        dataset_item: DatasetItem = {
            "question_id": question_id,
            "question": question,
        }
        video_path = item.get("video_path")
        image_path = item.get("image_path")
        if isinstance(video_path, str):
            dataset_item["video_path"] = video_path
        if isinstance(image_path, str):
            dataset_item["image_path"] = image_path
        data.append(dataset_item)
    return data


def run(config: BaselineConfig) -> None:
    config.paths.save_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_dataset(config.paths.question_file)
    llm = create_llm(config)
    sampling_params = create_sampling_params(config.generation)

    outputs = load_existing_outputs(config.paths.save_path)
    finished_ids = {item["question_id"] for item in outputs}
    bar = tqdm(data)

    for item in bar:
        question_id = item["question_id"]
        bar.set_description("Question Id: " + question_id)

        if question_id in finished_ids:
            continue

        try:
            prediction = process_item(
                item=item,
                llm=llm,
                sampling_params=sampling_params,
                video_base_dir=config.paths.video_base_dir,
                answer_instruction=config.prompt.answer_instruction,
            )
            output: StoredPrediction = {
                "question_id": question_id,
                "prediction": prediction["prediction"],
            }
        except Exception as error:
            print(f"处理失败，question_id={question_id}: {error}")
            output = {
                "question_id": question_id,
                "prediction": "",
                "error": str(error),
            }

        print(f"[{question_id}] prediction: {output.get('prediction', '')}")
        outputs.append(output)
        finished_ids.add(question_id)
        save_outputs(outputs, config.paths.save_path)


def parse_arguments() -> CliArguments:
    parser = argparse.ArgumentParser(description="运行 VideoVista-2 均匀采样基线")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="TOML 配置文件路径",
    )
    namespace = parser.parse_args()
    return CliArguments(config=cast(Path, namespace.config))


def main() -> None:
    arguments = parse_arguments()
    run(load_config(arguments.config))


if __name__ == "__main__":
    main()
