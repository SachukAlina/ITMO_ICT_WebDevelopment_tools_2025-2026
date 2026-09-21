import asyncio

from task1.async_sum import run as run_async
from task1.common import expected_sum, split_ranges
from task1.multiprocessing_sum import run as run_multiprocessing
from task1.threading_sum import run as run_threading


def test_ranges_cover_all_numbers_once() -> None:
    assert split_ranges(10, 3) == [(1, 4), (5, 7), (8, 10)]


def test_all_approaches_produce_the_same_sum() -> None:
    expected = expected_sum(10_000)
    assert run_threading(10_000, 3).result == expected
    assert run_multiprocessing(10_000, 3).result == expected
    assert asyncio.run(run_async(10_000, 3)).result == expected
