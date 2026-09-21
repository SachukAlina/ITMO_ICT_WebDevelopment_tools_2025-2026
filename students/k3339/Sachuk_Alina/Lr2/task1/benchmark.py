import asyncio
import csv
from pathlib import Path

from task1.async_sum import run as run_async
from task1.common import DEFAULT_WORKERS, TOTAL, RunResult
from task1.multiprocessing_sum import run as run_multiprocessing
from task1.threading_sum import run as run_threading


def main() -> None:
    results: list[RunResult] = [
        run_threading(TOTAL, DEFAULT_WORKERS),
        run_multiprocessing(TOTAL, DEFAULT_WORKERS),
        asyncio.run(run_async(TOTAL, DEFAULT_WORKERS)),
    ]
    output_path = Path(__file__).parents[1] / "results" / "sum_timings.csv"
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["approach", "total", "workers", "result", "elapsed_seconds"])
        for result in results:
            writer.writerow(
                [
                    result.approach,
                    result.total,
                    result.workers,
                    result.result,
                    f"{result.elapsed_seconds:.9f}",
                ]
            )
            result.print_json()


if __name__ == "__main__":
    main()
