import asyncio
import time

# A coroutine simulating a delayed operation
async def delayed_result(delay_seconds: int, result: str):
    await asyncio.sleep(delay_seconds)  # Pause execution for simulated wait
    return result

# Our asynchronous entry point
async def main():
    # Create tasks and submit them to the asyncio event loop
    task1 = asyncio.create_task(delayed_result(2, "Task 1 Done"))
    task2 = asyncio.create_task(delayed_result(1, "Task 2 Done"))

    # Wait for task1's result, allowing other tasks to run concurrently
    print(await task1)
    # Wait for task2, which likely is already complete.
    print(await task2)

if __name__ == "__main__":
    # Start the asyncio event loop to manage scheduled coroutines
    asyncio.run(main())