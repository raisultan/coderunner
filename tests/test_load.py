import pytest
import requests
import time
import concurrent.futures

SERVICE_URL = "http://localhost:8000/api/execute"


def send_request(code):
    payload = {
        "lang": "python",
        "content": code
    }
    response = requests.post(SERVICE_URL, json=payload)
    return response


@pytest.mark.parametrize("num_requests", [100, 500, 1000, 2000])
def test_concurrent_requests(num_requests):
    code = "import time; time.sleep(0.1); print('Done')"
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, code) for _ in range(num_requests)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    
    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["stdout"].strip() == "Done" for response in responses)
    
    total_time = end_time - start_time
    requests_per_second = num_requests / total_time
    
    print(f"\n- Completed {num_requests} requests in {total_time:.2f} seconds")
    print(f"- Requests per second: {requests_per_second:.2f}")
