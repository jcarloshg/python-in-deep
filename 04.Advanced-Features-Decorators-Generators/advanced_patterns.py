"""
advanced_patterns.py

Demonstrates high-level Python: Decorators with closure state and memory-efficient generator pipelines.

- Robust, parameterized retry decorator for error recovery
- Lazy evaluation pipeline with generators, scalable to million-row datasets
- Deep technical explanations: closures, yield/state-machine, comparison with TypeScript and asyncio
"""
from typing import Callable, Any, Iterator, Iterable
from functools import wraps
import time
import logging

logging.basicConfig(level=logging.INFO)

def retry(max_attempts: int = 3, delay: float = 1.0) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Parameterized retry decorator that handles ConnectionError.
    Uses a closure to capture arguments and retry state.
    functools.wraps preserves original function metadata for introspection and doc integrity.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts_left = max_attempts
            while attempts_left > 0:
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    attempts_left -= 1
                    if attempts_left > 0:
                        logging.warning(
                            f"[retry] {func.__name__} failed (attempts left: {attempts_left}, error: {e}). Retrying in {delay} sec..."
                        )
                        time.sleep(delay)
                    else:
                        logging.error(
                            f"[retry] {func.__name__} failed after {max_attempts} attempts. Last error: {e}"
                        )
                        raise
        # The closure here includes max_attempts, delay, and func
        # This is what enables each wrapped function to have its own retry policy and internal state
        return wrapper
    return decorator

# ------ Generator Pipeline ------
def read_large_file(num_lines: int = 1_000_000) -> Iterator[str]:
    """
    Simulates reading a file with a million log lines, using yield (generator).
    No list is ever built in memory: each line is streamed one at a time.
    """
    for i in range(num_lines):
        yield f"logline {i} - status=OK"
        # State of function is frozen at yield until next() is called


def filter_logs(lines: Iterable[str], status: str = "OK") -> Iterator[str]:
    """
    Generator pipeline stage: Select only log entries containing the status keyword.
    Still zero-copy: input is an iterator, output is an iterator.
    """
    for line in lines:
        if f"status={status}" in line:
            yield line


def search_logs(lines: Iterable[str], needle: str) -> Iterator[str]:
    """
    Pipeline stage: Filter log entries containing a keyword (needle).
    Demonstrates chaining of generators for a full pipeline.
    """
    for line in lines:
        if needle in line:
            yield line

# ---- Technical Notes ----
# Closures: In Python, a decorator that returns 'wrapper' is using closure—wrapper keeps direct references
# to all variables from the enclosing scope (like max_attempts, delay, func). This is key for parameterized retry.
# Generators: Every 'yield' causes the function to freeze (state, locals, etc. saved); next() "thaws" and resumes.
# This makes a generator a lightweight state-machine, extremely memory-efficient for long pipelines.
#
# The full pipeline below streams all data with constant/near-zero memory cost—no list of a million lines is built.

# ---- Comparison: Python Decorators vs TypeScript Decorators ----
# """
# Python decorators are functions that operate at runtime: code can perform logic, retry, cache, mutate.
# TypeScript decorators annotate (add metadata), mostly for compile-time tooling, injection, reflection.
# Python's are dynamic, TypeScript's are mostly static.
# """
#
# ---- yield and async programming in Python ----
# """
# 'yield' is the basis for Python's async machinery. 'await' is essentially 'yield from' under the hood (PEP492).
# Coroutines, generators, and async/await are unified by this suspend/resume (freeze/thaw) model,
# enabling scalable I/O and event loops (see: asyncio).
# """

# -- Demo/test area --
if __name__ == "__main__":

    @retry(max_attempts=3, delay=0.5)
    def flaky_network_call(counter: dict) -> str:
        """A simulated function that fails twice, succeeds on third try."""
        if counter['failures'] > 0:
            counter['failures'] -= 1
            raise ConnectionError("Network down!")
        return "Success!"

    state = {'failures': 2}
    print("Result:", flaky_network_call(state))

    # Lazy pipeline demo
    print("\nFirst 5 filtered log lines:")
    logs = filter_logs(search_logs(read_large_file(), "logline"))
    for i, line in enumerate(logs):
        if i >= 5:
            break
        print(line)

    print("\nMemory impact: this pipeline does not store any log lines in memory—each is created, filtered, and discarded one by one.")
    print("Even one million lines can be processed in constant RAM.")
