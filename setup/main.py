import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Optional, List, Dict, Any

import loguru
import typer
from openai import AsyncOpenAI, APIError
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from benchmark.ccb_parser import Conversations, evaluate_single_conversation, chat_to_conversation, Conversation
from benchmark.dataset_models import read_dataset

app = typer.Typer(no_args_is_help=True)


class RequestStat:
    def __init__(self, latency: float, success: bool, error: Optional[str] = None):
        self.latency = latency  # in seconds
        self.success = success
        self.error = error


@app.command()
def stress_test(
        datasets_path: Path = Path("rewards"),
        model_name: str = "hive",
        api_key: str = typer.Option(..., envvar="OPENAI_API_KEY"),
        base_url: Optional[str] = typer.Option(None),
        request_timeout: float = 120.0,  # per-request timeout
        max_retries: int = 1,  # retry on failure (0 = no retry)
):
    # Load all conversations once (reuse across concurrency levels)
    loguru.logger.info("Loading dataset...")
    base_conversations: List[Conversation] = []
    for hive_reward_dataset in tqdm(read_dataset(file_path=datasets_path).hive_reward_datasets,
                                    desc='Reading datasets'):
        base_conversations.append(Conversation(
            hive_reward_dataset=hive_reward_dataset,
            response='',
            total_score=0
        ))
    total_reqs = len(base_conversations)
    loguru.logger.info(f"Loaded {total_reqs} conversations for stress testing.")

    llm = AsyncOpenAI(api_key=api_key, base_url=base_url)

    # Concurrency levels: 10 → 20 → ... → 320
    concurrency_levels = [10, 20, 40, 80, 160, 320, 640, 1280]

    report: Dict[str, Any] = {
        "model": model_name,
        "dataset_size": total_reqs,
        "concurrency_levels": {}
    }

    for concurrency in concurrency_levels:
        if concurrency > total_reqs:
            loguru.logger.warning(f"Concurrency {concurrency} > dataset size ({total_reqs}), capping to {total_reqs}")
            concurrency = total_reqs

        loguru.logger.info(f"\n🧪 Starting test at concurrency={concurrency} (total requests={total_reqs})")
        stats = asyncio.run(
            run_concurrent_test(
                llm=llm,
                model_name=model_name,
                base_conversations=base_conversations,
                concurrency=concurrency,
                request_timeout=request_timeout,
                max_retries=max_retries
            )
        )

        # Compute metrics
        latencies = [s.latency for s in stats if s.success]
        success_count = len(latencies)
        error_count = len([s for s in stats if not s.success])
        total_time = max(s.latency for s in stats) if stats else 0  # wall-clock approx
        throughput = success_count / total_time if total_time > 0 else 0

        # Percentiles
        p50 = p90 = p99 = None
        if latencies:
            latencies_sorted = sorted(latencies)
            p50 = statistics.quantiles(latencies_sorted, n=2)[0]  # median
            p90 = statistics.quantiles(latencies_sorted, n=10)[8]  # 9th decile
            p99 = statistics.quantiles(latencies_sorted, n=100)[98] if len(latencies_sorted) >= 100 else max(
                latencies_sorted)

        metrics = {
            "total_requests": len(stats),
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": success_count / len(stats) if stats else 0,
            "avg_latency_sec": statistics.mean(latencies) if latencies else 0,
            "p50_latency_sec": p50,
            "p90_latency_sec": p90,
            "p99_latency_sec": p99,
            "throughput_req_per_sec": throughput,
            "total_duration_sec": total_time,
        }

        report["concurrency_levels"][str(concurrency)] = metrics
        loguru.logger.success(
            f"[Concurrency={concurrency}] "
            f"Success: {success_count}/{len(stats)} ({metrics['success_rate']:.1%}), "
            f"AvgLat: {metrics['avg_latency_sec']:.3f}s, "
            f"P99: {p99:.3f}s, "
            f"Throughput: {throughput:.2f} req/s"
        )

    # Save full report
    report_path = "stress_test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    loguru.logger.info(f"✅ Full report saved to {report_path}")


async def run_concurrent_test(
        llm: AsyncOpenAI,
        model_name: str,
        base_conversations: List[Conversation],
        concurrency: int,
        request_timeout: float,
        max_retries: int,
) -> List[RequestStat]:
    stats: List[RequestStat] = []
    semaphore = asyncio.Semaphore(concurrency)

    async def submit_and_measure(conversation: Conversation) -> RequestStat:
        start = time.perf_counter()
        attempt = 0
        while attempt <= max_retries:
            try:
                async with semaphore:
                    # ⚠️ CRITICAL: You MUST ensure `chat_to_conversation` returns or records latency,
                    # or modify it to accept a timing context.
                    # Here we assume it just *executes* the request and populates `conversation.response`.
                    # We measure wall time externally.
                    await asyncio.wait_for(
                        chat_to_conversation(conversation, llm, model=model_name),
                        timeout=request_timeout
                    )
                latency = time.perf_counter() - start
                return RequestStat(latency=latency, success=True)
            except asyncio.TimeoutError:
                error = f"Request timeout (> {request_timeout}s)"
                loguru.logger.warning(f"Timeout for conversation ID: {id(conversation)}")
            except APIError as e:
                error = f"APIError: {e.type} - {str(e)}"
                loguru.logger.warning(f"API error: {error}")
            except Exception as e:
                error = f"Unexpected error: {type(e).__name__} - {str(e)}"
                loguru.logger.exception("Unexpected exception in request")

            attempt += 1
            if attempt <= max_retries:
                # Optional: add backoff
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

        latency = time.perf_counter() - start
        return RequestStat(latency=latency, success=False, error=error)

    # Clone conversations per request to avoid mutation conflict (critical for concurrency!)
    tasks = [
        submit_and_measure(conversation.model_copy(deep=True))
        for conversation in base_conversations
    ]

    results = await tqdm_asyncio.gather(
        *tasks,
        desc=f"Running at concurrency={concurrency}",
        total=len(tasks),
        disable=None
    )
    return results


def entry():
    app()


if __name__ == '__main__':
    entry()
