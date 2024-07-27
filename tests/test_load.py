import pytest
import time
import statistics
import asyncio
import aiohttp

SERVICE_URL = "http://localhost:8000/api/execute"

async def send_request_async(session, code):
    payload = {
        "lang": "python",
        "content": code
    }
    async with session.post(SERVICE_URL, json=payload) as response:
        return await response.json()

async def run_test(num_requests, code):
    async with aiohttp.ClientSession() as session:
        tasks = [send_request_async(session, code) for _ in range(num_requests)]
        start_time = time.perf_counter()
        responses = await asyncio.gather(*tasks)
        end_time = time.perf_counter()

    total_time = end_time - start_time
    requests_per_second = num_requests / total_time
    return requests_per_second, responses

@pytest.mark.asyncio
@pytest.mark.parametrize("num_requests", [100, 500, 1000, 2000, 5000])
async def test_concurrent_requests(num_requests):
    codes = [
        "print('Quick operation')",
        "import time; time.sleep(0.1); print('I/O bound operation')",
        "sum(range(1000000)); print('CPU bound operation')"
    ]

    # Warm-up
    await run_test(100, "print('warm-up')")
    time.sleep(2)  # Cool-down

    for code in codes:
        results = []
        for _ in range(3):  # Run each test 3 times
            rps, responses = await run_test(num_requests, code)
            results.append(rps)
            assert all(r['stdout'].strip() != '' for r in responses)
            time.sleep(2)  # Cool-down between runs

        avg_rps = statistics.mean(results)
        median_rps = statistics.median(results)

        print(f"\nTest with {num_requests} requests and code: {code}")
        print(f"Average RPS: {avg_rps:.2f}")
