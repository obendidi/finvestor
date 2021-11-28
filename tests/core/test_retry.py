from unittest import mock

import numpy as np
import pytest

from finvestor.core.retry import RandomExponentialSleep, retrier

RANDOM_EXPONENTIAL_SLEEP_KWARGS = dict(
    scale=0.5, max_sleep=10, min_sleep=1, exp_base=2, jitter=1
)
NUM_ATTEMPTS = 20
# fmt: off
RANDOM_EXPONENTIAL_SLEEP_EXPECTED = [0.901, 0.259, 0.819, 1.385, 4.64, 5.047, 7.558,
                                     2.505, 9.828, 9.022, 7.298, 6.84, 1.007, 6.109,
                                     9.666, 8.653, 8.05, 0.14, 3.988, 6.682]
# fmt: on


def test_RandomExponentialSleep():
    sleeper = RandomExponentialSleep(**RANDOM_EXPONENTIAL_SLEEP_KWARGS)
    sleep_times = [round(sleeper(i), 3) for i in range(NUM_ATTEMPTS)]
    assert np.array_equal(sleep_times, RANDOM_EXPONENTIAL_SLEEP_EXPECTED)


async def test_retrier_worker_async(anyio_backend):
    async def _worker(i):
        if i < 15:
            raise Exception(f"{i}")
        return i

    idx = 0
    errors = []
    sleeptimes = []
    with mock.patch("anyio.sleep"):
        async for sleeptime in retrier(
            attempts=NUM_ATTEMPTS, **RANDOM_EXPONENTIAL_SLEEP_KWARGS
        ):
            try:
                result = await _worker(idx)
                break
            except Exception as error:
                errors.append(str(error))
                sleeptimes.append(round(sleeptime, 3))
                idx += 1
        else:
            raise Exception(f"THIS SHOULD NOT BE RAISED: {errors}")

    assert result == 15
    assert errors == [f"{i}" for i in range(15)]
    assert np.array_equal(sleeptimes, RANDOM_EXPONENTIAL_SLEEP_EXPECTED[:15])


async def test_retrier_worker_async_all_retries_fail(anyio_backend):
    async def _worker(i):
        raise Exception(f"{i}")

    class CustomException(Exception):
        pass

    idx = 0
    errors = []
    sleeptimes = []
    with mock.patch("anyio.sleep"):
        with pytest.raises(CustomException):
            async for sleeptime in retrier(
                attempts=NUM_ATTEMPTS, **RANDOM_EXPONENTIAL_SLEEP_KWARGS
            ):
                try:
                    await _worker(idx)
                    break
                except Exception as error:
                    errors.append(str(error))
                    sleeptimes.append(round(sleeptime, 3))
                    idx += 1
            else:
                raise CustomException(f"THIS SHOULD BE RAISED: {errors}")

    assert errors == [f"{i}" for i in range(NUM_ATTEMPTS)]
    assert np.array_equal(sleeptimes, RANDOM_EXPONENTIAL_SLEEP_EXPECTED)
