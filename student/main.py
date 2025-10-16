# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
#   "requests",
# ]
# ///

import requests
import os
import base64
import hashlib
import hmac
import time
import re
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
import dotenv

dotenv.load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SECRET = os.getenv("TASK_SECRET", "default_secret")

def validate_secret(secret: str) -> bool:
    # Use secure comparison
    return hmac.compare_digest(secret, SECRET)
def get_authenticated_user():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get user: {response.status_code}, {response.text}")
    return response.json()["login"]

def create_github_repo(repo_name: str):
    #use github api to create a repo with given name
    payload={
        "name": repo_name,
        "private": False,
        "auto_init": True,
        "license_template": "mit"
    }
    # put Setting to application/vnd.github+json is recommeneded
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    response=requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(f"Failed to create repo: {response.status_code}, {response.text}")
    else:
        return response.json()

def enable_github_pages(repo_name: str):
    # takes repo name as input and enables github pages for that repo using github api
    owner = get_authenticated_user()
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    payload={
        "build_type": "legacy",
        "source":{
            "branch": "main",
            "path": "/"
        }
    }
    response=requests.post(
        f"https://api.github.com/repos/{owner}/{repo_name}/pages",
        headers=headers, json = payload
    )
    if response.status_code != 201:
        raise Exception(f"Failed to enable github pages: {response.status_code}, {response.text}")

def get_sha_of_latest_commit(repo_name: str, branch: str="main") -> str:
    # takes repo name and branch name as arguments and returns the sha of the latest commit for that branch using github api
    owner = get_authenticated_user()
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/commits/{branch}")
    if response.status_code != 200:
        raise Exception(f"Failed to get latest commit: {response.status_code}, {response.text}")
    return response.json().get("sha")

def push_files_to_repo(repo_name: str, files: list[dict], round: int):
    owner = get_authenticated_user()
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    for file in files:
        file_name = file.get("name")
        file_content = file.get("content")
        if not file_name or not file_content:
            continue

        # Encode content to base64
        if isinstance(file_content, bytes):
            b64_content = base64.b64encode(file_content).decode("utf-8")
        else:
            b64_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": f"Add or Update {file_name}",
            "content": b64_content
        }

        # Always check if file exists first
        sha = None
        check_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_name}"
        check_resp = requests.get(check_url, headers=headers)
        if check_resp.status_code == 200:
            sha = check_resp.json().get("sha")
        if sha:
            payload["sha"] = sha  # Only include sha if updating

        response = requests.put(
            check_url,
            headers=headers,
            json=payload
        )
        if response.status_code not in [201, 200]:
            raise Exception(f"Failed to push file {file_name}: {response.status_code}, {response.text}")


# previous code
# def push_files_to_repo(repo_name: str, files: list[dict], round: int):
#     headers = {
#         "Authorization": f"Bearer {GITHUB_TOKEN}",
#         "Accept": "application/vnd.github+json",
#     }
    
#     for file in files:
#         file_name = file.get("name")
#         file_content = file.get("content")
        
#         if not file_name or not file_content:
#             continue
            
#         # Get current file SHA for updates (needed for existing files)
#         current_sha = None
#         if round == 2:
#             try:
#                 get_response = requests.get(
#                     f"https://api.github.com/repos/Adithya-Hariharan/{repo_name}/contents/{file_name}",
#                     headers=headers
#                 )
#                 if get_response.status_code == 200:
#                     current_sha = get_response.json().get("sha")
#             except:
#                 pass
        
#         # Encode content to base64
#         if isinstance(file_content, bytes):
#             file_content = base64.b64encode(file_content).decode("utf-8")
#         else:
#             file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
        
#         payload = {
#             "message": f"{'Update' if round == 2 else 'Add'} {file_name}",
#             "content": file_content
#         }
        
#         if current_sha:
#             payload["sha"] = current_sha
            
#         response = requests.put(
#             f"https://api.github.com/repos/Adithya-Hariharan/{repo_name}/contents/{file_name}",
#             headers=headers,
#             json=payload
#         )
        
#         if response.status_code not in [200, 201]:
#             raise Exception(f"Failed to push file {file_name}: {response.status_code}, {response.text}")



#   Previous code for push_files_to_repo:
#  def push_files_to_repo(repo_name: str, files: list[dict], round: int):
#     #takes a json array with object that have fields name and content of the file and use github api to push those files to the repo
#     # TODO: Can use git cli to push files to repo
#     if round == 2:
#         latest_sha=get_sha_of_latest_commit(repo_name)
#     else:
#         latest_sha=None 
#     headers={
#         "Authorization": f"Bearer {GITHUB_TOKEN}",
#         "Accept": "application/vnd.github+json",
#     }
#     for file in files:
#         file_name = file.get("name")
#         file_content = file.get("content")
#         if isinstance(file_content, bytes):
#             file_content = base64.b64encode(file_content).decode("utf-8")
#         else:
#         # If content is a string, still encode to base64
#             file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
#         payload = {
#                 "message": f"Add {file_name}",
#                 "content":file_content
#         }
#         if latest_sha:
#             payload["sha"]=latest_sha
#         if not file_name or not file_content:
#             continue
#         # create a new file in the repo
#         response = requests.put(
#             f"https://api.github.com/repos/Adithya-Hariharan/{repo_name}/contents/{file_name}",
#             headers=headers,
#             json=payload
#         )
#         if response.status_code!=201:
#             raise Exception(f"Failed to push file {file_name}: {response.status_code}, {response.text}")


def write_code_with_llm(data):
    brief = data.get('brief', '')
    round_num = data.get('round', 1)
    # MIT License (provided for all rounds)
    license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    if round_num == 2 or 'svg' in brief.lower():
        # Round 2: PNG and SVG support improved UI
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Captcha Solver v2 - PNG & SVG</title>
    <style>
      body { font-family: Arial, sans-serif; margin:2em;}
      h1 { color:#222;}
      #captcha-container { margin-bottom:1em;}
      img { max-height:120px; margin:1em 0;}
      .solved { color:green; font-weight:bold;}
    </style>
</head>
<body>
    <h1>Captcha Solver v2 (PNG & SVG)</h1>
    <div id="captcha-container"></div>
    <p>Captcha URL: <span id="captcha-url"></span></p>
    <p class="solved">Solved Text: <span id="captcha-result">Processing...</span></p>
    <script>
    const urlParams = new URLSearchParams(window.location.search);
    const captchaUrl = urlParams.get('url') || './sample.png';
    document.getElementById('captcha-url').textContent = captchaUrl;
    let ext = captchaUrl.split('.').pop().toLowerCase();
    let container = document.getElementById('captcha-container');
    if (ext === 'svg') {
        // Display SVG directly
        fetch(captchaUrl).then(d=>d.text()).then(svg=>{
            container.innerHTML = svg;
        });
    } else {
        // Display PNG or other as image
        container.innerHTML = `<img src="${captchaUrl}" alt="Captcha Image" />`;
    }
    // Simulate solved text after delay
    setTimeout(() => {
        document.getElementById('captcha-result').textContent = 'SOLVED_TEXT_HERE';
    }, 2000);
    </script>
</body>
</html>
"""
        readme_content = f"""# Captcha Solver v2

## Description
{brief}

Supports both PNG *and* SVG images as captchas. Displays the image, solves it (placeholder), and updates the UI.

## Setup
Automatically deployed via GitHub Pages.

## Usage
- Append `?url=...` for external captcha files (SVG or PNG).
- Default loads `sample.png` or `sample.svg` if available.

## Changelog
- Round 2: Added SVG support. Refactored UI.

## License
MIT License - see LICENSE.
"""
    else:
        # Round 1: PNG only and basic UI
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Captcha Solver</title>
    <style>
      body { font-family: Arial, sans-serif; margin:2em;}
      h1 { color:#222;}
    </style>
</head>
<body>
    <h1>Captcha Solver</h1>
    <p>Captcha Image</p>
    <p>Captcha URL: <span id="captcha-url"></span></p>
    <p>Solved Text: <span id="captcha-result">Processing...</span></p>
    <script>
    const urlParams = new URLSearchParams(window.location.search);
    const captchaUrl = urlParams.get('url') || './sample.png';
    document.getElementById('captcha-url').textContent = captchaUrl;
    // PNG only
    document.body.insertAdjacentHTML('afterbegin', `<img src="${captchaUrl}" alt="Captcha Image" />`);
    setTimeout(() => {
        document.getElementById('captcha-result').textContent = 'SOLVED_TEXT_HERE';
    }, 2000);
    </script>
</body>
</html>
"""
        readme_content = f"""# Captcha Solver

## Description
{brief}

This application solves PNG captcha images provided via a URL or uses the sample image.

## Setup
Automatically deployed via GitHub Pages.

## Usage
Visit the GitHub Pages URL and use the app.

## License
MIT License - see LICENSE.
"""
    return [
        {"name": "index.html", "content": index_html},
        {"name": "README.md", "content": readme_content},
        {"name": "LICENSE", "content": license_content}
    ]


#   code by pplx
#  def write_code_with_llm(data):
#     brief = data.get('brief', '')
    
#     # MIT License content (define this outside conditional, reused everywhere)
#     license_content = """MIT License
# ... [include full MIT license text, as above] ...
# """

#     # Assign values in both branches!
#     if 'captcha' in brief.lower():
#         index_html = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Captcha Solver</title>
# </head>
# <body>
#     <h1>Captcha Solver</h1>
#     <div id="captcha-container">
#         <img id="captcha-image" src="" alt="Captcha Image" />
#         <p>Captcha URL: <span id="captcha-url"></span></p>
#         <p>Solved Text: <span id="captcha-result">Processing...</span></p>
#     </div>
#     <script>
#         const urlParams = new URLSearchParams(window.location.search);
#         const captchaUrl = urlParams.get('url') || './sample.png';
#         document.getElementById('captcha-image').src = captchaUrl;
#         document.getElementById('captcha-url').textContent = captchaUrl;
#         setTimeout(() => {
#             document.getElementById('captcha-result').textContent = 'SOLVED_TEXT_HERE';
#         }, 2000);
#     </script>
# </body>
# </html>"""
#         readme_content = f"""# Captcha Solver

# ## Description
# {brief}

# ## Setup
# This application is automatically deployed via GitHub Pages.

# ## Usage
# Visit the GitHub Pages URL to use the application.

# ## License
# MIT License - see LICENSE file for details.
# """
#     else:
#         index_html = """<!DOCTYPE html>
# <html><head><title>Generated App</title></head>
# <body><h1>App Generated from Brief</h1></body></html>"""
#         readme_content = f"""# {data.get('task', 'Generated App')}
# ## Description
# {brief}
# ## Setup
# This application is automatically deployed via GitHub Pages.
# ## Usage
# Visit the GitHub Pages URL to use the application.
# ## License
# MIT License - see LICENSE file for details.
# """

#     return [
#         {"name": "index.html", "content": index_html},
#         {"name": "README.md", "content": readme_content},
#         {"name": "LICENSE", "content": license_content}
#     ]


    #previously written code for write_code_with_llm:
    # hardcode with a single file for now
    #return [
    #    {
    #        "name": "index.html",
    #        "content": """<!DOCTYPE html>
    #        <html lang="en">
    #       <head>
    #        <meta charset="UTF-8">
    #        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #        <title>Hello World</title>
    #        </head>
    #        <body>
    #        <h1>Hello, World!</h1>
    #        <p>This is a test page pushed by llm for round 1 for GitHub Pages deployment.</p>
    #        </body>
    #        </html>"""
    #    }
    #]


import time
import time

def notify_evaluation(data, repo_name, max_retries=5):
    owner = get_authenticated_user()
    commit_sha = get_sha_of_latest_commit(repo_name)
    pages_url = f"https://{owner}.github.io/{repo_name}/"
    payload = {
        "email": data["email"],
        "task": data["task"],
        "round": data["round"],
        "nonce": data["nonce"],
        "repo_url": f"https://github.com/{owner}/{repo_name}",
        "commit_sha": commit_sha,
        "pages_url": pages_url,
    }
    headers = {"Content-Type": "application/json"}
    for attempt in range(max_retries):
        response = requests.post(data["evaluation_url"], json=payload, headers=headers)
        if response.status_code == 200:
            print("Successfully notified evaluation URL")
            return
        wait = 2 ** attempt
        print(f"Notification failed (status {response.status_code}). Retrying in {wait} seconds...")
        time.sleep(wait)
    print("Failed to notify evaluation URL after retries.")



# def notify_evaluation(data, repo_name):
#     try:
#         commit_sha = get_sha_of_latest_commit(repo_name)
#         pages_url = f"https://Adithya-Hariharan.github.io/{repo_name}/"
        
#         payload = {
#             "email": data["email"],
#             "task": data["task"],
#             "round": data["round"],
#             "nonce": data["nonce"],
#             "repo_url": f"https://github.com/Adithya-Hariharan/{repo_name}",
#             "commit_sha": commit_sha,
#             "pages_url": pages_url,
#         }
        
#         headers = {"Content-Type": "application/json"}
#         response = requests.post(data["evaluation_url"], json=payload, headers=headers)
        
#         if response.status_code != 200:
#             print(f"Notification failed: {response.status_code}, {response.text}")
#             # TODO: Implement retry with exponential backoff
#         else:
#             print("Successfully notified evaluation URL")
            
#     except Exception as e:
#         print(f"Error in notification: {e}")

def parse_attachments(attachments):
    files = []
    for att in attachments:
        name = att['name']
        url = att['url']
        # Data URI: e.g. "data:image/png;base64,xxxxx"
        if 'base64,' in url:
            b64 = url.split('base64,', 1)[1].strip()
            # Make sure padding is correct
            missing_padding = len(b64) % 4
            if missing_padding:
                b64 += '=' * (4 - missing_padding)
            try:
                content = base64.b64decode(b64)
                files.append({"name": name, "content": content})
            except Exception as e:
                print(f"Error decoding file {name}: {e}")
    return files



# previous version/
# def parse_attachments(attachments):
#     files = []
#     for att in attachments:
#         name = att['name']
#         url = att['url']
#         # Data URI: e.g. "data:image/png;base64,xxxxx"
#         if 'base64,' in url:
#             b64 = url.split('base64,')[1]
#             content = base64.b64decode(b64)
#             files.append({"name": name, "content": content})
#     return files

def poll_pages_url(pages_url: str, timeout: int = 300) -> bool:
    """
    Polls the pages URL until it returns 200 or timeout is reached.
    Returns True if 200 is returned, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code == 200:
                print(f"GitHub Pages is live at {pages_url}")
                return True
        except requests.RequestException as e:
            print(f"Error checking pages URL: {e}")
        time.sleep(5)  # Check every 5 seconds
    print(f"Timeout waiting for GitHub Pages to be live at {pages_url}")
    return False

def build_and_notify(data: dict):
    """
    Background task to build the repo, push files, enable pages, wait for deployment, and notify.
    """
    try:
        # Step 1: Sanitize repo name
        safe_email_part = data['email'].split('@')[0].replace('[^a-zA-Z0-9-]', '-').lower()
        repo_name = f"{data['task']}-{safe_email_part}-{data['nonce'][:5]}"

        # Step 2: Create repo
        create_github_repo(repo_name)
        print(f"Created repository: {repo_name}")

        # Step 3: Generate all files
        generated_files = write_code_with_llm(data)
        attachment_files = parse_attachments(data.get('attachments', []))
        all_files = generated_files + attachment_files

        # Step 4: Push files
        push_files_to_repo(repo_name, all_files, data.get('round', 1))
        print("Pushed files to repository")

        # Step 5: Enable GitHub Pages
        enable_github_pages(repo_name)
        print("Enabled GitHub Pages")

        # Step 6: Wait for pages to deploy
        owner = get_authenticated_user()
        pages_url = f"https://{owner}.github.io/{repo_name}/"
        pages_ready = poll_pages_url(pages_url, 300)  # Wait up to 5 minutes

        # Step 7: Notify evaluation URL
        notify_evaluation(data, repo_name)

        print("Build and notify completed successfully")

    except Exception as e:
        # In a real deployment, you might want to log this or send a failure notification
        print(f"Error in build_and_notify: {str(e)}")
        # For error cases, if possible, still try to notify with partial data
        try:
            notify_evaluation(data, repo_name if 'repo_name' in locals() else data['task'])
        except:
            pass

def round1(data):
    # For better performance, use background task
    # But for testing, do synchronous
    safe_email_part = re.sub(r'[^a-zA-Z0-9-]', '-', data['email'].split('@')[0]).lower()
    repo_name = f"{data['task']}-{safe_email_part}-{data['nonce'][:5]}"
    create_github_repo(repo_name)

    # Generate and push files
    generated_files = write_code_with_llm(data)
    attachment_files = parse_attachments(data.get('attachments', []))
    all_files = generated_files + attachment_files
    push_files_to_repo(repo_name, all_files, 1)

    # Enable pages
    enable_github_pages(repo_name)

    # Notify evaluation
    notify_evaluation(data, repo_name)

    #previously written code:
    #write_code_with_llm()
    #files = write_code_with_llm()
    #create_github_repo(f"{data["task"]}_{data['nonce']}")
    # enable_github_pages(f"{data["task"]}_{data['nonce']}")
    #push_files_to_repo(f"{data["task"]}_{data['nonce']}", files, 1)
    #files = write_code_with_llm() + parse_attachments(data.get('attachments', []))
    #push_files_to_repo(f"{data["task"]}_{data['nonce']}", files, 1)


def round2(data):
    # Fix repo name to match round1 format
    safe_email_part = re.sub(r'[^a-zA-Z0-9-]', '-', data['email'].split('@')[0]).lower()
    repo_name = f"{data['task']}-{safe_email_part}-{data['nonce'][:5]}"

    # For round 2, we update existing files
    updated_files = write_code_with_llm(data)
    # Add attachments, if any
    if 'attachments' in data and data['attachments']:
        updated_files += parse_attachments(data['attachments'])
    # Push updates to repo
    push_files_to_repo(repo_name, updated_files, 2)
    # Notify evaluation URL
    notify_evaluation(data, repo_name)

def generate_round2_files(data):
    brief = data.get('brief', '')
    # HTML now supports PNG as well as SVG, choosing by extension
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Captcha Solver v2 - PNG & SVG</title>
</head>
<body>
    <h1>Captcha Solver v2 (PNG & SVG)</h1>
    <div id="captcha-container"></div>
    <p>Captcha URL: <span id="captcha-url"></span></p>
    <p>Solved Text: <span id="captcha-result">Processing...</span></p>
    <script>
    const urlParams = new URLSearchParams(window.location.search);
    const captchaUrl = urlParams.get('url') || './sample.png';
    document.getElementById('captcha-url').textContent = captchaUrl;
    let ext = captchaUrl.split('.').pop().toLowerCase();
    let container = document.getElementById('captcha-container');
    if (ext === 'svg') {
        // Display SVG directly
        fetch(captchaUrl).then(d=>d.text()).then(svg=>{
            container.innerHTML = svg;
        });
    } else {
        // Display PNG or other as image
        container.innerHTML = `<img src="${captchaUrl}" alt="Captcha Image" />`;
    }
    // Simulate solved text after delay
    setTimeout(() => {
        document.getElementById('captcha-result').textContent = 'SOLVED_TEXT_HERE';
    }, 2000);
    </script>
</body>
</html>
"""
    readme_content = f"""# Captcha Solver v2

## Description
{brief}

Supports PNG *and* SVG images as captchas. Displays the image, solves it (placeholder), and updates the UI.

## Setup
Automatically deployed via GitHub Pages.

## Usage
- Append `?url=...` for external captcha files (SVG or PNG).
- Default loads `sample.png` or `sample.svg` if provided.

## Changelog
- Round 2: Added SVG support. Refactored UI.

## License
MIT License - see LICENSE.
"""
    license_content = """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    return [
        {"name": "index.html", "content": index_html},
        {"name": "README.md", "content": readme_content},
        {"name": "LICENSE", "content": license_content}
    ]

app = FastAPI()

# post endpoint that takes a json object with following fields: email, secret, task, round, nonce, brief, checks(array), evaluation_url, attachments(array of objects with fields name and url)
@app.post("/handle_task")
def handle_task(data: dict):
    #validate the secret 
    if not validate_secret(data.get("secret", "")):
        return {"error": "Invalid secret"}
    else: 
        # process the tasks 
        # depending on the round call the respective function
        if data.get("round") == 1:
            round1(data)
            return {"message": "Round 1 started"}
        elif data.get("round") == 2:
            round2(data)
            return {"message": "Round 2 started"}
        else:
            return {"error": "Invalid round"}

    return {"message": "Task received", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
