from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from task1.common import (
    DEFAULT_WORKERS,
    TOTAL,
    RunResult,
    arithmetic_sum,
    split_ranges,
    validate_result,
)


def calculate_sum(bounds: tuple[int, int]) -> int:
    start, end = bounds
    return arithmetic_sum(start, end)


def run(total: int = TOTAL, workers: int = DEFAULT_WORKERS) -> RunResult:
    ranges = split_ranges(total, workers)
    started_at = perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        result = sum(executor.map(calculate_sum, ranges))
    elapsed = perf_counter() - started_at
    return validate_result(RunResult("threading", total, workers, result, elapsed))


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--total", type=int, default=TOTAL)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()
    run(args.total, args.workers).print_json()


if __name__ == "__main__":
    main()
