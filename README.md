# LLM Code Deployment Project

This project implements a system for automatically building and deploying web applications using LLM-assisted code generation. The student API can receive tasks, generate code based on specifications, create GitHub repositories, enable GitHub Pages deployment, and notify evaluation systems.

## Project Structure

```
project1/
├── PROJECT_SPECIFICATIONS.md    # Complete project requirements
├── README.md                    # This file
├── steps.txt                    # Implementation planning notes
├── .gitignore                   # Git ignore rules
├── instructor/                  # Instructor-side tooling
│   └── send_task.py            # Script to send test tasks
└── student/                     # Student implementation
    ├── main.py                 # FastAPI application for handling tasks
    └── .env                    # Environment variables (secrets)
```

## Features Implemented

### Student API (`/handle_task` endpoint)
- **Secure Authentication**: Validates requests using HMAC-based secret comparison
- **Multi-round Support**: Handles both round 1 (initial build) and round 2 (updates)
- **GitHub Integration**: Automatically creates repositories, pushes code, enables Pages
- **LLM Code Generation**: Generates complete web applications with HTML, CSS, JS
- **Attachment Handling**: Parses and deploys data URI attachments (images, etc.)
- **Evaluation Reporting**: Posts results to evaluation URLs with proper retry logic

### GitHub Automation
- Repository creation with automatic initialization
- MIT license application
- File pushing via GitHub Contents API
- GitHub Pages deployment
- Dynamic username resolution from tokens
- Secure repo naming with email sanitization

### Application Generation
- Complete web applications based on task briefs
- Support for various assignment types (captcha solvers, markdown converters, etc.)
- Responsive design with proper HTML structure
- Architecture that supports round 2 enhancements

## Setup Instructions

### Prerequisites
- Python 3.11+
- GitHub Personal Access Token with `repo` and `pages` permissions
- Internet connection for GitHub API access

### Installation

1. **Clone/download this repository**
2. **Create virtual environment**:
   ```bash
   cd project1/student
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   Create `.env` file in student directory with:
   ```
   GITHUB_TOKEN=your_github_token_here
   TASK_SECRET=your_shared_secret_here
   ```

### Running the Application

1. **Start the API server**:
   ```bash
   cd project1/student
   python main.py
   ```
   Server runs on `http://localhost:8000`

2. **Test the implementation**:
   ```bash
   cd project1/instructor
   python send_task.py
   ```

## API Documentation

### POST `/handle_task`

Accepts JSON payload with the following structure:

```json
{
  "email": "student@example.com",
  "secret": "shared_secret",
  "task": "captcha-solver-...",
  "round": 1,
  "nonce": "unique_nonce",
  "brief": "Description of what the app should do",
  "checks": ["array of evaluation criteria"],
  "evaluation_url": "https://evaluation.server/api",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,..."
    }
  ]
}
```

**Response (HTTP 200)**:
```json
{
  "message": "Round 1 started"
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub PAT with repo permissions | `ghp_xxxxx` |
| `TASK_SECRET` | Secret for request validation | `my_secret_123` |

## Assignment Tasks

The system is designed to handle various assignment types including:
- Captcha solvers (PNG/SVG support)
- Markdown to HTML converters
- GitHub user info display forms
- Data processing and visualization
- Custom web applications

Each task automatically generates appropriate HTML, CSS, JavaScript, and documentation.

## Security Features

- HMAC-based secret validation (timing attack resistant)
- Data URI validation and sanitization
- Repository name sanitization
- No secrets committed to version control (`.gitignore` protection)
- Secure GitHub API token handling

## Deployment Flow

1. **Request Validation**: Verify secret and required fields
2. **Repository Setup**: Create private GitHub repo with MIT license
3. **Code Generation**: Use LLM to generate complete web application
4. **Asset Deployment**: Push HTML, JS, CSS, and attachments to repo
5. **Pages Enablement**: Configure GitHub Pages for deployment
6. **Reporting**: Notify evaluation system with repo details and commit SHA

## Dependencies

- `fastapi[standard]` - API framework and server
- `uvicorn` - ASGI server
- `requests` - HTTP client for GitHub API
- `hmac` - Secure secret comparison (built-in)
- `base64` - Data URI handling (built-in)
- `time` - Retry delays (built-in)
- `re` - Name sanitization (built-in)

## Testing

Run the instructor test script to verify functionality:
```bash
python instructor/send_task.py
```

This sends a sample task to the local API server and verifies:
- Request acceptance
- GitHub repository creation
- Pages deployment
- Evaluation notification

## Compliance

This implementation follows all requirements in `PROJECT_SPECIFICATIONS.md`:
- ✅ Builds and deploys applications automatically
- ✅ Uses LLM-assisted generation
- ✅ Creates GitHub repositories and enables Pages
- ✅ Handles multiple rounds for improvements
- ✅ Posts results to evaluation systems
- ✅ Includes proper error handling and retries
- ✅ Generates comprehensive README and LICENSE files
- ✅ Supports attachment deployment
- ✅ Implements secure secret validation

## Contributing

This is an assignment project. For modifications, ensure changes comply with the project specifications and maintain the required functionality.
