from typing import NamedTuple

import pytest
import requests


class Request(NamedTuple):
    lang: str
    content: str

class Response(NamedTuple):
    stdout: str
    stderr: str

class Case(NamedTuple):
    req: Request
    resp: Response


cases = [
    # Simple print statement
    Case(
        req=Request(
            lang="python3.9",
            content="print(\"Hello World\")",
        ),
        resp=Response(
            stdout="Hello World\n",
            stderr="",
        ),
    ),
    # Arithmetic operation
    Case(
        req=Request(
            lang="python3.9",
            content="print(2 + 2)",
        ),
        resp=Response(
            stdout="4\n",
            stderr="",
        ),
    ),
    # Syntax error
    Case(
        req=Request(
            lang="python3.9",
            content="print(2 + )",
        ),
        resp=Response(
            stdout="",
            stderr="  File \"<string>\", line 1\n    print(2 + )\n              ^\nSyntaxError: invalid syntax\n",
        ),
    ),
    # Loop with print
    Case(
        req=Request(
            lang="python3.9",
            content="for i in range(3): print(i)",
        ),
        resp=Response(
            stdout="0\n1\n2\n",
            stderr="",
        ),
    ),
    # Variable assignment and print
    Case(
        req=Request(
            lang="python3.9",
            content="x = 5\nprint(x)",
        ),
        resp=Response(
            stdout="5\n",
            stderr="",
        ),
    ),
    # Function definition and call
    Case(
        req=Request(
            lang="python3.9",
            content="def greet(name):\n    print(f\"Hello, {name}!\")\ngreet(\"Alice\")",
        ),
        resp=Response(
            stdout="Hello, Alice!\n",
            stderr="",
        ),
    ),
    # Division by zero error
    Case(
        req=Request(
            lang="python3.9",
            content="print(1 / 0)",
        ),
        resp=Response(
            stdout="",
            stderr="Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nZeroDivisionError: division by zero\n",
        ),
    ),
    # Import and use a module
    Case(
        req=Request(
            lang="python3.9",
            content="import math\nprint(math.sqrt(16))",
        ),
        resp=Response(
            stdout="4.0\n",
            stderr="",
        ),
    ),
    # List comprehension
    Case(
        req=Request(
            lang="python3.9",
            content="print([x * 2 for x in range(5)])",
        ),
        resp=Response(
            stdout="[0, 2, 4, 6, 8]\n",
            stderr="",
        ),
    ),
    # Handling exceptions
    Case(
        req=Request(
            lang="python3.9",
            content="try:\n    print(1 / 0)\nexcept ZeroDivisionError as e:\n    print(\"Caught an error:\", e)",
        ),
        resp=Response(
            stdout="Caught an error: division by zero\n",
            stderr="",
        ),
    ),
]


@pytest.mark.parametrize("case", cases)
def test_execute(case):
    url = "http://localhost:8000/api/execute"
    response = requests.post(url, json={
        "lang": case.req.lang,
        "content": case.req.content
    })

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['stdout'] == case.resp.stdout
    assert response_json['stderr'] == case.resp.stderr
