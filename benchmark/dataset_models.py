import json
from dataclasses import Field
from pathlib import Path
from typing import Literal, List

from pydantic import BaseModel


class CheckPoint(BaseModel):
    matching_method: Literal["normal", "regex"] = 'normal'
    keyword: str
    score: float


class CheckPoints(BaseModel):
    check_points: List[CheckPoint]


class HiveRewardDataset(BaseModel):
    topic: str
    checkpoints: CheckPoints


class HiveRewardDatasets(BaseModel):
    hive_reward_datasets: List[HiveRewardDataset]


def read_dataset(file_path: Path) -> HiveRewardDatasets:
    assert file_path.is_dir(), f"Expected a directory, got: {file_path}"

    datasets: List[HiveRewardDataset] = []

    for json_file in file_path.rglob("*.hive-reward.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        topic = data.get("topic", "")
        checkpoint_list = data.get("checkpoint", [])
        matchingmethod_list = data.get("matchingmethod", [])

        check_points: List[CheckPoint] = []
        for item, method in zip(checkpoint_list, matchingmethod_list):
            if not isinstance(item, dict) or len(item) != 1:
                raise ValueError(f"Invalid checkpoint item format in {json_file}: {item}")
            keyword = list(item.keys())[0]
            score = float(item[keyword])
            check_points.append(
                CheckPoint(
                    matching_method=method,
                    keyword=keyword,
                    score=score
                )
            )

        dataset = HiveRewardDataset(
            topic=topic,
            checkpoints=CheckPoints(check_points=check_points)
        )
        datasets.append(dataset)

    return HiveRewardDatasets(hive_reward_datasets=datasets)
