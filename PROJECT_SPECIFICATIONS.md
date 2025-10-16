# Project: LLM Code Deployment

## Overview

This project requires students to build an application that can automatically build, deploy, and update another application based on incoming requests. The system involves LLM-assisted code generation, GitHub repository creation and deployment via GitHub Pages, and evaluation through an API.

## Three Phases

### 1. Build Phase

The student implements an API endpoint that:

- **Receives & Verifies Requests**: Accepts JSON POST requests containing:
  - `email`: Student's email ID
  - `secret`: Student-provided secret for verification
  - `task`: Unique task identifier
  - `round`: Round index (1 for initial build)
  - `nonce`: Random nonce to pass back
  - `brief`: Description of what the app needs to do
  - `checks`: Array of evaluation criteria
  - `evaluation_url`: URL to post results to
  - `attachments`: Array of attachments encoded as data URIs

- **Validates Secret**: Compares request secret against pre-shared value from Google Form submission

- **Returns HTTP 200**: Sends JSON response acknowledging receipt

- **Generates Application**:
  - Parses request JSON and attachments
  - Uses LLM to generate minimal application code based on the brief
  - Frontend application should be buildable/deployable

- **Creates Repository**:
  - Uses GitHub API/CLI with personal access token
  - Creates unique public repository named based on `task`
  - Adds MIT `LICENSE` file at root
  - Commits and pushes generated code
  - Enables GitHub Pages
  - Ensures Pages site returns HTTP 200
  - Prevents secrets leakage using tools like trufflehog/gitlaks

- **Writes Documentation**:
  - Creates comprehensive `README.md` with:
    - Project summary
    - Setup instructions
    - Usage examples
    - Code explanation
    - License information

- **Reports Completion**:
  - Within 10 minutes of request, POSTs JSON to `evaluation_url` with:
    ```json
    {
      "email": "student@example.com",
      "task": "captcha-solver-...",
      "round": 1,
      "nonce": "ab12-...",
      "repo_url": "https://github.com/user/repo",
      "commit_sha": "abc123",
      "pages_url": "https://user.github.io/repo/"
    }
    ```
  - Implements exponential backoff (1, 2, 4, 8... seconds) for failed posts
  - Ensures HTTP 200 response

### 2. Revise Phase

For round 2 and beyond:

- **Receives Second Request**: Similar JSON structure but with `round: 2`+

- **Validates Secret**: Verifies against pre-shared value

- **Returns HTTP 200**: Acknowledges receipt

- **Updates Application**:
  - Modifies existing repository code based on new `brief`
  - Updates `README.md` as needed
  - Commits and pushes changes to redeploy

- **Reports Update**: POSTs to same `evaluation_url` within 10 minutes with updated metadata

### 3. Evaluate Phase

Instructor-side evaluation:

- **Publishes Google Form**: Collects student API endpoints, secrets, and repo URLs

- **Generates Tasks**:
  - Creates unique requests per student submission using task templates
  - Parametrizes templates with seeds based on email and timestamp
  - Tasks expire hourly

- **Posts Requests**: Sends to student endpoints, retries up to 3 times over 3-24 hours on failure

- **Accepts Submissions**: `evaluation_url` API receives repo metadata and validates against task database

- **Evaluates Repositories**:
  - **Repo-level checks**: MIT license presence, creation time validation
  - **LLM checks**: Code and README quality assessment
  - **Dynamic checks**: Uses Playwright to test live application functionality

- **Generates Round 2**: For all round 1 submissions, creates follow-up tasks for improvements

- **Publishes Results**: After deadline, shares evaluation database

## Technical Requirements

### Student Implementation

- **API Endpoint**: Accepts JSON POST at `/api-endpoint`
- **Secret Verification**: Stores and validates pre-shared secret
- **LLM Integration**: Uses AI to generate application code from briefs
- **GitHub Integration**: Creates repos, enables Pages, deploys code
- **Error Handling**: Exponential backoff for API submissions
- **Security**: Prevents credential leaks in repository
- **Timing**: Must complete within 10-minute windows

### Repository Structure

- **Root files**: MIT LICENSE, README.md
- **Generated app**: Appropriate structure (HTML/CSS/JS, etc.)
- **GitHub Pages**: Must be publicly accessible via user.github.io/repo/

### Evaluation Criteria (per task)

- Rule-based checks (repo structure, licensing)
- LLM-based quality assessments
- Dynamic functional tests via Playwright
- Up to 3 rounds of revision requests possible

## Sample Task Templates

### 1. sum-of-sales
**Brief**: Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to "Sales Summary ${seed}", displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.

**Checks**:
- `document.title === "Sales Summary ${seed}"`
- `!!document.querySelector("link[href*='bootstrap']")`
- `Math.abs(parseFloat(document.querySelector("#total-sales").textContent) - ${result}) < 0.01`

**Round 2 Options**:
1. Add Bootstrap table showing product sales breakdown
2. Add currency conversion with rates from attachment
3. Add region filtering functionality

### 2. markdown-to-html
**Brief**: Convert attached Markdown to HTML using marked library, render in #markdown-output, include highlight.js for code blocks.

**Checks**:
- Script includes marked and highlight.js
- Output contains HTML headers

**Round 2 Options**:
1. Add tabs to switch between HTML and raw Markdown views
2. Support loading Markdown from URL parameter
3. Add live word count with number formatting

### 3. github-user-created
**Brief**: Form that fetches GitHub user creation date, displays in YYYY-MM-DD format, optionally uses token query param.

**Checks**:
- Form element with correct ID
- Displays creation date
- Code includes GitHub API call

**Round 2 Options**:
1. Add status alerts for API calls
2. Show account age in years
3. Cache successful lookups in localStorage

## Database Schema (Instructor Side)

### tasks Table
- timestamp, email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret

### repos Table
- timestamp, email, task, round, nonce, repo_url, commit_sha, pages_url

### results Table
- timestamp, email, task, round, repo_url, commit_sha, pages_url, check, score, reason, logs

## Evaluation Scripts

### round1.py
- Processes submissions.csv
- Generates initial tasks from templates with randomization
- Posts requests to student endpoints
- Logs to tasks table

### evaluation_url API
- Receives repo submissions
- Validates against task database
- Stores in repos table

### evaluate.py
- Checks repos for license, timing
- Runs LLM quality evaluations
- Executes Playwright tests based on template checks
- Logs results to results table

### round2.py
- Generates follow-up tasks for completed submissions
- Posts round 2 requests to endpoints
- Logs to tasks table

## Google Form Structure
- Student email
- API endpoint URL
- Secret value
- GitHub repository URL

## Constraints
- Repositories must be public
- GitHub Pages must be enabled and reachable
- No secrets in commit history
- Submissions accepted up to 3 attempts with delays
- Evaluation includes static, dynamic, and LLM-based checking
