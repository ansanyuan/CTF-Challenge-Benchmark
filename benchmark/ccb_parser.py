import json
import random
import re
from typing import List, Any

import loguru
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

from benchmark.hive_reward import HiveRewardDataset, read


class Conversation(BaseModel):
    hive_reward_dataset: HiveRewardDataset
    response: str
    total_score: float = Field(0.0, ge=0, le=1)

class Conversations(BaseModel):
    conversations: List[Conversation]

def evaluate(conversations: Conversations):
    for conversation in tqdm(conversations.conversations,desc="Evaluating..."):
        conversation.total_score = parse_hive_reward(conversation)

def parse_hive_reward(conversation: Conversation) -> float:
    """
    根据输入的hive-reward.json和response进行打分
    """
    assert len(conversation.response) > 0 , "response不应为空"
    response = conversation.response
    score = 0
    for checkpoint in conversation.hive_reward_dataset.checkpoints.check_points:
        matching_method = checkpoint.matching_method
        keyword = checkpoint.keyword
        checkpoint_score = checkpoint.score
        if matching_method == 'normal':
            score += checkpoint_score if keyword in response else 0
        elif matching_method == 'regex':
            score += checkpoint_score if re.search(keyword,response) else 0
    return score

async def chat_to_conversation(
        conversation: Conversation,
        llm: AsyncOpenAI,
        model: str = "gpt-4o",
        **kwargs: Any
) -> None:
    """
    使用 LLM 对 conversation.hive_reward_dataset.topic 进行提问，
    将生成的回复写入 conversation.response（原地修改）。

    Args:
        conversation: 要修改的 Conversation 实例。
        llm: OpenAI 风格的异步客户端（如 openai.AsyncOpenAI）。
        model: 使用的模型名称，默认为 "gpt-4o"。
        **kwargs: 传递给 llm.chat.completions.create 的额外参数。
    """
    prompt = conversation.hive_reward_dataset.topic
    response = await llm.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )
    generated_text = response.choices[0].message.content or ""
    conversation.response = generated_text.strip()