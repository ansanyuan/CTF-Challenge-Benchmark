import asyncio
import json
from pathlib import Path
from typing import Optional

import loguru
import typer
from openai import AsyncOpenAI
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from benchmark.ccb_parser import Conversations, evaluate, chat_to_conversation, Conversation
from benchmark.hive_reward import read

app = typer.Typer(
    no_args_is_help=True
)


@app.command()
def benchmark(
        datasets_path: Path = Path("rewards"),
        model_name: str = "hive",
        api_key: str = typer.Option(..., envvar="OPENAI_API_KEY"),
        base_url: Optional[str] = typer.Option(None),
        MAX_CONCURRENT_REQUESTS: int = 10
):
    llm = AsyncOpenAI(api_key=api_key, base_url=base_url)
    conversations = Conversations(conversations=[])
    for hive_reward_dataset in tqdm(read(file_path=datasets_path).hive_reward_datasets, desc='Reading datasets'):
        conversations.conversations.append(Conversation(
            hive_reward_dataset=hive_reward_dataset,
            response='',
            total_score=0
        ))
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def limited_chat(convo: Conversation):
        async with semaphore:
            await chat_to_conversation(convo, llm, model=model_name)

    asyncio.run(
        tqdm_asyncio.gather(
            *(limited_chat(conv) for conv in conversations.conversations),
            desc=f"Benchmarking LLM responses with {MAX_CONCURRENT_REQUESTS} MAX_CONCURRENT_REQUESTS",
            total=len(conversations.conversations),
        )
    )
    evaluate(conversations)
    with open("dump.json", "w", encoding="utf-8") as f:
        json.dump(conversations.model_dump(), f, ensure_ascii=False, indent=2)
    eva_score = 0
    for conversation in conversations.conversations:
        eva_score += conversation.total_score
    eva_score = eva_score / len(conversations.conversations)
    loguru.logger.success(f"总分: {eva_score}")

def entry():
    app()


if __name__ == '__main__':
    entry()
