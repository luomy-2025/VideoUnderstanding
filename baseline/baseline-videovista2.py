from __future__ import annotations

import json
import os
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


QUESTION_FILE: str = os.getenv(
    "QUESTION_FILE",
    "/root/HNLP/VideoVista-2/videovista2_no_answer.json",
)
VIDEO_BASE_DIR: str = os.getenv("VIDEO_BASE_DIR", "/root/HNLP/VideoVista-2")
SAVE_PATH: str = os.getenv(
    "SAVE_PATH",
    "/root/HNLP/ReaonProcess/result/"
    "Baseline-lowtemptaure-30b.json",
)
MODEL_NAME: str = os.getenv("MODEL_NAME", "/root/HNLP/qwen3-vl-30b")


llm: LLM = LLM(
    model=MODEL_NAME,
    trust_remote_code=True,
    tensor_parallel_size=int(os.getenv("TENSOR_PARALLEL_SIZE", "2")),
    allowed_local_media_path=VIDEO_BASE_DIR,
    max_model_len=int(os.getenv("MAX_MODEL_LEN", "256000")),
    async_scheduling=True,
    mm_processor_kwargs={"max_pixels": int(os.getenv("MAX_PIXELS", "230400"))},
    media_io_kwargs={"video": {"num_frames": int(os.getenv("NUM_FRAMES", "180"))}},
)

# 使用确定性生成参数，保证配对实验可复现。
sampling_params: SamplingParams = SamplingParams(
    temperature=0.0,
    top_p=1.0,
    max_tokens=32,
    repetition_penalty=1.0,
)


def build_media_content(item: DatasetItem) -> list[MediaContent]:
    content: list[MediaContent] = []

    if item.get("video_path"):
        video_full_path = os.path.join(VIDEO_BASE_DIR, item["video_path"])
        content.append(
            {
                "type": "video_url",
                "video_url": {"url": f"file://{video_full_path}"},
            }
        )

    if item.get("image_path"):
        image_full_path = os.path.join(VIDEO_BASE_DIR, item["image_path"])
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"file://{image_full_path}"},
            }
        )

    return content


def process_item(item: DatasetItem) -> Prediction:
    question = item["question"]
    prompt = (
        f"{question} \n"
        "Answer the question only with single option's letter. For example: A"
    )

    content = build_media_content(item)
    content.append({"type": "text", "text": prompt})
    messages: list[ChatMessage] = [{"role": "user", "content": content}]

    outputs = llm.chat(
        messages=messages,
        sampling_params=sampling_params,
        use_tqdm=False,
    )
    response = outputs[0].outputs[0].text.strip()
    return {"prediction": response}


def load_existing_outputs() -> list[StoredPrediction]:
    if not os.path.exists(SAVE_PATH):
        return []
    with open(SAVE_PATH, "r", encoding="utf-8") as json_file:
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


def save_outputs(outputs: list[StoredPrediction]) -> None:
    tmp_path = SAVE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as json_file:
        json.dump(outputs, json_file, indent=3, ensure_ascii=False)
    os.replace(tmp_path, SAVE_PATH)


def load_dataset() -> list[DatasetItem]:
    with open(QUESTION_FILE, "r", encoding="utf-8") as json_file:
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


if __name__ == "__main__":
    save_dir = os.path.dirname(SAVE_PATH)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    data = load_dataset()

    outputs = load_existing_outputs()
    finished_ids = {item["question_id"] for item in outputs}
    bar = tqdm(data)

    for item in bar:
        question_id = item["question_id"]
        bar.set_description("Question Id: " + question_id)

        if question_id in finished_ids:
            continue

        try:
            prediction = process_item(item)
            output: StoredPrediction = {
                "question_id": question_id,
                "prediction": prediction["prediction"],
            }
        except Exception as error:
            print(f"Failed question_id={question_id}: {error}")
            output = {
                "question_id": question_id,
                "prediction": "",
                "error": str(error),
            }

        print(f"[{question_id}] prediction: {output.get('prediction', '')}")
        outputs.append(output)
        finished_ids.add(question_id)
        save_outputs(outputs)
