#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://project1-phi-sepia.vercel.app/api-endpoint"
SECRET = "11BCGJPSA0eqeVRYOKbQY2"

timeouts = {"test_health": 5, "round1": 500, "round2": 500}

test_request_calculator = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "calculator-app-xyz789",
    "round": 1,
    "nonce": "test-nonce-123456",
    "brief": "Create a simple calculator web app that can perform basic arithmetic operations (addition, subtraction, multiplication, division). The interface should be clean and user-friendly with buttons for numbers 0-9 and operation symbols. Display the result clearly.",
    "checks": [
        "Repo has MIT license",
        "README.md is professional and complete",
        "Calculator UI is clean and intuitive",
        "All basic operations work correctly",
        "Result is displayed properly",
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_sales_summary = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "sum-of-sales",
    "round": 1,
    "nonce": "sales-nonce-001",
    "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to 'Sales Summary 12345', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
    "checks": [
        "js: document.title === 'Sales Summary 12345'",
        "js: !!document.querySelector(\"link[href*='bootstrap']\")",
        'js: Math.abs(parseFloat(document.querySelector("#total-sales").textContent) - 15000) < 0.01',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "data.csv",
            "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBLDUwMDAKQiwxMDAwMApDLDUwMDA=",
        }
    ],
}

test_request_github_user = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "github-user-created",
    "round": 1,
    "nonce": "github-nonce-001",
    "brief": "Publish a Bootstrap page with form id='github-user-abc123' that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
    "checks": [
        'js: document.querySelector("#github-user-abc123").tagName === "FORM"',
        'js: document.querySelector("#github-created-at").textContent.includes("20")',
        'js: !!document.querySelector("script").textContent.includes("https://api.github.com/users/")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request_markdown_to_html = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "markdown-to-html",
    "round": 1,
    "nonce": "md-nonce-001",
    "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
    "checks": [
        "js: !!document.querySelector(\"script[src*='marked']\")",
        "js: !!document.querySelector(\"script[src*='highlight.js']\")",
        'js: document.querySelector("#markdown-output").innerHTML.includes("<h")',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [
        {
            "name": "input.md",
            "url": "data:text/markdown;base64,IyBIZWxsbyBXb3JsZAoKVGhpcyBpcyBhIHNhbXBsZSBtYXJrZG93biBmaWxlLgoKYGBgYApjb2RlIGJsb2NrCmBgYAo=",
        }
    ],
}

# Additional example: simple static page with a counter
test_request_counter_app = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "counter-app",
    "round": 1,
    "nonce": "counter-nonce-001",
    "brief": "Publish a static page with a button #increment-btn and a number inside #counter-value that increments by 1 each time the button is clicked.",
    "checks": [
        'js: !!document.querySelector("#increment-btn")',
        'js: !!document.querySelector("#counter-value")',
        'js: (() => { const v = document.querySelector("#counter-value"); const b = document.querySelector("#increment-btn"); const before = parseInt(v.textContent, 10); b.click(); return parseInt(v.textContent, 10) === before + 1; })()',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

# Additional example: static page with a dark mode toggle
test_request_dark_mode = {
    "email": "test@example.com",
    "secret": SECRET,
    "task": "dark-mode-toggle",
    "round": 1,
    "nonce": "darkmode-nonce-001",
    "brief": "Publish a static page with a toggle #dark-mode-toggle that switches the page between light and dark themes, updating the body class.",
    "checks": [
        'js: !!document.querySelector("#dark-mode-toggle")',
        'js: (() => { const t = document.querySelector("#dark-mode-toggle"); const b = document.body; t.click(); return b.classList.contains("dark"); })()',
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": [],
}

test_request = test_request_calculator


def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(
            "https://project1-phi-sepia.vercel.app/health", timeout=timeouts["test_health"]
        )
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Health check failed: {e}")
        return False


def test_deployment(request_data=None):
    if request_data is None:
        request_data = test_request

    print("\n" + "=" * 60)
    print("Testing deployment endpoint...")
    print("=" * 60)

    print("\nSending request:")
    print(json.dumps(request_data, indent=2))

    try:
        response = requests.post(
            API_URL,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=timeouts.get("round1"),  # Give it 2 minutes to complete
        )

        print(f"\nResponse Status: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print(" SUCCESS!")
            print("=" * 60)
            print(f"Repository: {data.get('repo_url')}")
            print(f"GitHub Pages: {data.get('pages_url')}")
            print(f"Commit SHA: {data.get('commit_sha')}")
            print("\nNote: GitHub Pages may take 1-2 minutes to deploy.")
            return True
        else:
            print("\n Request failed")
            return False

    except requests.RequestException as e:
        print(f"\n Request error: {e}")
        return False


def test_round_2(base_request=None, brief=None, example_name=None):
    if base_request is None:
        base_request = test_request
    if brief is None:
        # Provide appropriate Round 2 briefs based on the example
        if example_name == "Counter App":
            brief = "Add a decrement button #decrement-btn that decreases the counter by 1, and a reset button #reset-btn that sets the counter back to 0. Update the UI to be more visually appealing."
        elif example_name == "Calculator App":
            brief = "Update the calculator to also support square root and percentage operations. Add a clear button to reset the calculator."
        elif example_name == "Sales Summary":
            brief = "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render."
        elif example_name == "GitHub User Created":
            brief = "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails."
        elif example_name == "Markdown to HTML":
            brief = "Add a dark mode toggle and improve the styling with better typography and spacing."
        elif example_name == "Dark Mode Toggle":
            brief = "Add smooth transitions between light and dark modes, and save the user's preference in localStorage."
        else:
            brief = "Add new features and improve the user interface."

    print("\n" + "=" * 60)
    print("Testing Round 2 (Revision) endpoint...")
    print("=" * 60)

    round2_request = base_request.copy()
    round2_request["round"] = 2
    round2_request["brief"] = brief
    round2_request["nonce"] = base_request.get("nonce", "test-nonce") + "-round2"

    print("\nSending Round 2 request:")
    print(json.dumps(round2_request, indent=2))

    try:
        response = requests.post(
            API_URL,
            json=round2_request,
            headers={"Content-Type": "application/json"},
            timeout=timeouts.get("round2"),
        )

        print(f"\nResponse Status: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print(" ROUND 2 SUCCESS!")
            print("=" * 60)
            print(f"Repository: {data.get('repo_url')}")
            print(f"GitHub Pages: {data.get('pages_url')}")
            print(f"Commit SHA: {data.get('commit_sha')}")
            return True
        else:
            print("\n Round 2 request failed")
            return False

    except requests.RequestException as e:
        print(f"\n Request error: {e}")
        return False


def select_test_example():
    print("\nAvailable test examples:")
    print("1. Calculator App (basic arithmetic operations)")
    print("2. Sales Summary (CSV parsing, Bootstrap, sum calculation)")
    print("3. GitHub User Created (API fetch, date formatting)")
    print("4. Markdown to HTML (marked, highlight.js)")
    print("5. Counter App (static, button increments value)")
    print("6. Dark Mode Toggle (static, theme switch)")
    print(
        "\nSelect an example (1-6), or press Enter for default (Calculator): ", end=""
    )

    try:
        choice = input().strip()
        if not choice or choice == "1":
            return test_request_calculator, "Calculator App"
        elif choice == "2":
            return test_request_sales_summary, "Sales Summary"
        elif choice == "3":
            return test_request_github_user, "GitHub User Created"
        elif choice == "4":
            return test_request_markdown_to_html, "Markdown to HTML"
        elif choice == "5":
            return test_request_counter_app, "Counter App"
        elif choice == "6":
            return test_request_dark_mode, "Dark Mode Toggle"
        else:
            print("Invalid choice, using default (Calculator App)")
            return test_request_calculator, "Calculator App"
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return None, None


def main():
    print("=" * 60)
    print("LLM Code Deployment System - Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running (python main.py)")

    selected_request, example_name = select_test_example()
    if selected_request is None:
        return

    print(f"\nSelected: {example_name}")
    print("Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return

    if not test_health():
        print("\n Server is not responding. Make sure it's running.")
        return

    print("\n\nStarting deployment test...")
    print("This will create a real GitHub repository and may take 30-60 seconds.")
    print("Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        return

    success = test_deployment(selected_request)

    if success:
        print("\n\nWould you like to test Round 2 (revision)? (y/n)")
        try:
            choice = input().strip().lower()
            if choice == "y":
                test_round_2(selected_request, example_name=example_name)
        except KeyboardInterrupt:
            print("\n\nCancelled.")

    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()