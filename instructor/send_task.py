# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
# ]
# ///

import requests

def send_task():
    payload={
        "email": "student@example.com",
        "secret": "myproject2025", 
        "task": "captcha-solver-...",
        "round": 2,
        "nonce": "ab12",
        "brief": "Create a captcha solver that handles ?url=https://.../image.png. Default to attached sample.",
        "checks": [
            "Repo has MIT license"
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds",
        ],
        "evaluation_url": "https://example.com/notify",
        "attachments": [{
            "name": "sample.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADggGQo/DC0QAAAABJRU5ErkJggg=="
        }]

    }

    response = requests.post("http://localhost:8000/handle_task", json=payload)
    print(response.text )

if __name__ == "__main__":
    send_task()
    
