import argparse
import asyncio
from time import perf_counter

from task1.common import (
    DEFAULT_WORKERS,
    TOTAL,
    RunResult,
    arithmetic_sum,
    split_ranges,
    validate_result,
)


async def calculate_sum(bounds: tuple[int, int]) -> int:
    await asyncio.sleep(0)
    start, end = bounds
    return arithmetic_sum(start, end)


async def run(total: int = TOTAL, workers: int = DEFAULT_WORKERS) -> RunResult:
    ranges = split_ranges(total, workers)
    started_at = perf_counter()
    partial_results = await asyncio.gather(
        *(calculate_sum(bounds) for bounds in ranges)
    )
    elapsed = perf_counter() - started_at
    return validate_result(
        RunResult("asyncio", total, workers, sum(partial_results), elapsed)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=int, default=TOTAL)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()
    asyncio.run(run(args.total, args.workers)).print_json()


if __name__ == "__main__":
    main()
