import json
from dataclasses import asdict, dataclass

TOTAL = 10_000_000_000_000
DEFAULT_WORKERS = 4


@dataclass(frozen=True)
class RunResult:
    approach: str
    total: int
    workers: int
    result: int
    elapsed_seconds: float

    def print_json(self) -> None:
        print(json.dumps(asdict(self), ensure_ascii=False))


def split_ranges(total: int, workers: int) -> list[tuple[int, int]]:
    if total < 1:
        raise ValueError("total must be positive")
    if workers < 1:
        raise ValueError("workers must be positive")
    workers = min(workers, total)
    chunk_size, remainder = divmod(total, workers)
    ranges: list[tuple[int, int]] = []
    start = 1
    for index in range(workers):
        size = chunk_size + (1 if index < remainder else 0)
        end = start + size - 1
        ranges.append((start, end))
        start = end + 1
    return ranges


def arithmetic_sum(start: int, end: int) -> int:
    """Return an inclusive range sum in constant time."""
    count = end - start + 1
    return count * (start + end) // 2


def expected_sum(total: int) -> int:
    return total * (total + 1) // 2


def validate_result(result: RunResult) -> RunResult:
    expected = expected_sum(result.total)
    if result.result != expected:
        raise RuntimeError(f"Incorrect sum: {result.result}, expected: {expected}")
    return result
