import json
import random
import re
from typing import List, Any

import loguru
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

from benchmark.dataset_models import HiveRewardDataset, read


class Conversation(BaseModel):
    hive_reward_dataset: HiveRewardDataset
    response: str
    total_score: float = Field(0.0, ge=0, le=1)

class Conversations(BaseModel):
    conversations: List[Conversation]

def evaluate_single_conversation(conversations: Conversations):
    for conversation in tqdm(conversations.conversations,desc="Evaluating..."):
        conversation.total_score = parse_hive_reward(conversation)

def parse_hive_reward(conversation: Conversation) -> float:
    """
    根据输入的hive-reward.json和response进行打分
    """
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
        llm_client: AsyncOpenAI,
        model: str = "gpt-4o",
        prefix: str = "",
        suffix: str = "",
        system_prompt = "You are a helpful assistant.",
        enable_thinking: bool = False,
        **kwargs: Any
) -> None:
    """
    使用 llm(AsyncOpenAI) 对 conversation.hive_reward_dataset.topic 进行提问，
    将生成的回复写入 conversation.response（原地修改）。

    Args:
        conversation: 要修改的 Conversation 实例。
        llm_client: OpenAI 风格的异步客户端（如 openai.AsyncOpenAI）。
        model: 使用的模型名称，默认为 "gpt-4o"。
        prefix: 前缀
        suffix: 后缀
        system_prompt: 系统提示词
        enable_thinking: 是否启用思考模式
        **kwargs: 传递给 llm.chat.completions.create 的额外参数。
    """
    prompt = prefix + conversation.hive_reward_dataset.topic + suffix
    response = await llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system" , "content" : system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=8192,
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": enable_thinking},
        },
        **kwargs
    )
    generated_text = response.choices[0].message.content or ""
    conversation.response = generated_text.strip()