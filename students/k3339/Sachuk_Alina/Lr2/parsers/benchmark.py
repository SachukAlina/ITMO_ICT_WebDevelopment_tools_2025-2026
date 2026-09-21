import asyncio
import csv
from pathlib import Path

from parsers.async_parser import run as run_async
from parsers.common import BenchmarkResult
from parsers.multiprocessing_parser import run as run_multiprocessing
from parsers.threading_parser import run as run_threading


def main() -> None:
    results: list[BenchmarkResult] = [
        run_threading(),
        run_multiprocessing(),
        asyncio.run(run_async()),
    ]
    output_path = Path(__file__).parents[1] / "results" / "parser_timings.csv"
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["approach", "parsed_count", "workers", "elapsed_seconds"])
        for result in results:
            writer.writerow(
                [
                    result.approach,
                    result.parsed_count,
                    result.workers,
                    f"{result.elapsed_seconds:.6f}",
                ]
            )
            print(result)


if __name__ == "__main__":
    main()
