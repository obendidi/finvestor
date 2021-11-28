import logging
import random
from typing import AsyncGenerator

import anyio

logger = logging.getLogger(__name__)


class RandomExponentialSleep:
    """Random wait with exponentially widening window.
    An exponential backoff strategy used to mediate contention between multiple
    uncoordinated processes for a shared resource in distributed systems. This
    is the sense in which "exponential backoff" is meant in e.g. Ethernet
    networking, and corresponds to the "Full Jitter" algorithm described in
    this blog post:
    https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    Each retry occurs at a random time in a geometrically expanding interval.
    It allows for a custom scale and an ability to restrict the upper
    limit of the random interval to some maximum value.
    Example::
        RandomExponentialSleep(scale=0.5,  # initial window 0.5s
                                max_sleep=60)          # max 60s timeout
    """

    def __init__(
        self,
        scale: float = 1,
        max_sleep: float = 300,
        exp_base: float = 2,
        min_sleep: float = 0,
        jitter: float = 0,
    ):
        self.scale = scale
        self.min_sleep = min_sleep
        self.max_sleep = max_sleep
        self.exp_base = exp_base
        self.jitter = jitter

    def __call__(self, retry_number: int) -> float:
        high = self._get_high(retry_number)
        return random.uniform(0, high)

    def _get_high(self, retry_number: int) -> float:
        try:
            exp = self.exp_base ** retry_number
            result = self.scale * exp
            if self.jitter:
                result = result + random.uniform(-self.jitter, self.jitter)
        except OverflowError:
            return self.max_sleep
        return max(max(0, self.min_sleep), min(result, self.max_sleep))


async def retrier(
    attempts: int = 5,
    scale: float = 1,
    max_sleep: float = 300,
    exp_base: float = 2,
    min_sleep: float = 0,
    jitter: float = 0,
) -> AsyncGenerator[float, None]:

    sleep_time_generator = RandomExponentialSleep(
        scale=scale,
        max_sleep=max_sleep,
        min_sleep=min_sleep,
        exp_base=exp_base,
        jitter=jitter,
    )

    for attempt in range(attempts):
        sleeptime = sleep_time_generator(attempt)
        yield sleeptime
        if attempt < attempts - 1:
            print(f" ==> SLEEPING for {sleeptime}s")
            await anyio.sleep(sleeptime)
