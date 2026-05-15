# ChatBVP Control Tower

**Event-Driven AI Agent Orchestration and Operational Dashboard for Venture Execution**

ChatBVP Control Tower is a production-style operational orchestration platform built with Django, Celery, Redis, PostgreSQL, Ollama, Matrix, and SMTP. It converts user-submitted operational requests into trackable workspaces, processes them asynchronously through an AI workflow, sends automated email responses, creates collaboration rooms, and maintains full auditability across the request lifecycle.

This project is designed as a real-world control layer for teams that need visibility, ownership, collaboration, and recovery around AI-assisted operational workflows.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Core Capabilities](#core-capabilities)
- [Architecture](#architecture)
- [End-to-End Workflow](#end-to-end-workflow)
- [System Components](#system-components)
- [Project Structure](#project-structure)
- [Data Model Overview](#data-model-overview)
- [Failure Handling and Retry Strategy](#failure-handling-and-retry-strategy)
- [Observability and Audit Logging](#observability-and-audit-logging)
- [Local and VM Services](#local-and-vm-services)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Application Routes](#application-routes)
- [Deployment Notes](#deployment-notes)
- [Future Enhancements](#future-enhancements)
- [Resume Summary](#resume-summary)

---

## Problem Statement

Operational teams often receive requests through fragmented channels such as forms, emails, chats, and meetings. Without a centralized orchestration layer, teams face recurring issues:

- No single place to track request status
- Weak ownership and handoff visibility
- Manual follow-up with customers
- No audit trail for workflow execution
- AI outputs not connected to real operational workflows
- Collaboration scattered across external tools

The goal of Control Tower is to centralize intake, automate workflow execution, assign ownership, provide collaboration spaces, and make every step observable.

---

## Solution Overview

Control Tower provides a complete request-to-resolution workflow:

1. A user submits a request through an intake form.
2. The system creates an `OperationalEvent` with a unique correlation ID.
3. Celery processes the event asynchronously.
4. A `Workspace` is created for internal tracking.
5. A Matrix room is created for team collaboration.
6. Ollama generates an AI response using a local LLM.
7. The response is emailed to the requester with internal team members copied.
8. The dashboard displays status, owner, next actions, and audit logs.
9. If AI processing fails, the system sends a fallback email and exposes a retry button.

---

## Core Capabilities

### User Intake

The intake layer captures:

- Request type
- First name
- Last name
- Email
- User question 
- 
Supported request types:

- `NEW_INTAKE`
- `WEEKLY_UPDATE`
- `SUPPORT_REQUEST`

Each submission creates a persistent event and displays a confirmation page with request details and correlation ID.

---

### Event-Driven Workflow Processing

Control Tower uses an event-driven approach where the user request is persisted first and processed asynchronously afterward.

Key characteristics:

- Request submission remains fast
- Long-running AI work does not block the UI
- External integrations run inside Celery workers
- Workflow state is persisted in PostgreSQL
- Failures are logged and recoverable

---

### AI Integration with Ollama

The system integrates with Ollama using the `llama3` model.

AI behavior:

- Generates direct answers for simple user questions
- Produces structured workflow output for operational requests
- Uses strict JSON response formatting
- Stores generated output in the workspace
- Posts AI summaries to Matrix
- Sends AI-generated responses by email

Expected structured output:

```json
{
  "summary": "Detailed summary of the response",
  "answer_to_user": "Detailed answer for the requester",
  "answer_items": [],
  "next_action": "NONE or actionable next step",
  "steps": [],
  "risks": []
}
```

---

### Dashboard

The dashboard acts as the internal operational control panel.

It provides:

- Event type
- Current status
- Requester first name
- Requester last name
- Requester email
- Assigned owner
- Next actions
- Matrix room reference
- Workspace detail view
- Audit log access
- Retry workflow button on failure

Supported status values include:

- `IN_PROGRESS`
- `DONE`
- `AI_FAILED`

---

### Team Member Management

The team module supports internal member lifecycle management:

- Add team member
- Edit team member
- Delete team member
- Enable team member
- Disable team member
- Filter active and inactive members
- Send notification emails for team actions

When a workspace is created, the system can assign an active team member as owner. The owner name is preserved even if the member is later disabled or deleted.

---

### Matrix Collaboration

Control Tower creates a Matrix room for each workflow.

Matrix is used for:

- Workflow collaboration
- AI response visibility
- Email status updates
- Internal team discussion
- Audio/video collaboration through Matrix clients

The dashboard exposes an `Open` button that navigates to the Matrix room.

---

### Email Automation

The system sends emails using SMTP.

Requester email behavior:

- Sends AI-generated answer to the requester
- CCs configured internal team members
- Sends fallback response when AI fails
- Logs email success or failure in audit logs

Team member email behavior:

- Sends email when a member is added
- Sends email when member details are edited
- Sends email when a member is deleted
- Sends email when a member is disabled
- Sends email when a member is enabled again

---

## Architecture

```text
┌─────────────────────┐
│   User Intake Form  │
│  first/last/email   │
│  request message    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Django Web App    │
│  Forms, Views, UI   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Operational Event  │
│ correlation_id      │
│ payload + status    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Redis Broker      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Celery Worker     │
│ workflow executor   │
└──────┬──────┬────────┘
       │      │
       │      ├─────────────────────┐
       │                            ▼
       │                  ┌─────────────────────┐
       │                  │ Ollama / llama3     │
       │                  │ AI response engine  │
       │                  └─────────────────────┘
       │
       ├────────────────────────────▼
       │                  ┌─────────────────────┐
       │                  │ Matrix Synapse      │
       │                  │ collaboration room  │
       │                  └─────────────────────┘
       │
       ├────────────────────────────▼
       │                  ┌─────────────────────┐
       │                  │ SMTP Email          │
       │                  │ customer response   │
       │                  └─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ PostgreSQL Database │
│ Workspace + logs    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Internal Dashboard  │
│ status, owner, logs │
└─────────────────────┘
```

---

## End-to-End Workflow

```text
User submits request
        ↓
IntakeRequest saved
        ↓
OperationalEvent created with correlation_id
        ↓
Celery task queued through Redis
        ↓
Workspace created or refreshed
        ↓
Owner assigned from active team members
        ↓
Matrix room created
        ↓
Ollama generates structured AI response
        ↓
Response stored in Workspace
        ↓
AI response posted to Matrix
        ↓
Email sent to requester with internal CC
        ↓
Audit logs updated
        ↓
Dashboard shows final status and next actions
```

---

## System Components

### `intake`

Responsible for the customer-facing request submission flow.

Main responsibilities:

- Render intake form
- Validate request fields
- Save `IntakeRequest`
- Build event payload
- Create `OperationalEvent`
- Trigger background workflow

---

### `events`

Responsible for event creation and persistence.

Main responsibilities:

- Store event type
- Store event payload
- Generate correlation ID
- Track event status

Core model:

- `OperationalEvent`

---

### `workflows`

Responsible for orchestration and async processing.

Main responsibilities:

- Celery task execution
- Workspace creation and refresh
- Owner assignment
- Matrix room creation
- Ollama AI processing
- Email dispatch
- Failure handling
- Audit logging

Core task:

- `process_event`

---

### `adapters`

Responsible for external system integration.

Main integrations:

- `matrix_client.py`
  - Create Matrix rooms
  - Invite users
  - Post messages

- `ollama_client.py`
  - Call Ollama
  - Extract model response
  - Parse structured JSON
  - Build strict JSON prompts

This separation keeps external service logic isolated from workflow orchestration logic.

---

### `dashboard`

Responsible for internal operations UI.

Main responsibilities:

- List workspaces
- Filter dashboard records
- Display request details
- Show AI answer
- Open Matrix room
- Expose retry workflow action
- Assign owner if missing

Core model:

- `Workspace`

---

### `team`

Responsible for internal team management.

Main responsibilities:

- Add/edit/delete members
- Enable/disable members
- Send lifecycle notification emails
- Maintain active/inactive member lists
- Support owner assignment

Core model:

- `TeamMember`

---

### `audit`

Responsible for observability.

Main responsibilities:

- Persist workflow execution logs
- Display logs by correlation ID
- Provide API representation of logs

Core model:

- `AuditLog`

---

### `controltower`

Contains additional event APIs, Swagger UI support, and earlier direct event-agent execution views.

Main responsibilities:

- API endpoints for event creation and agent execution
- Swagger UI rendering
- OpenAPI YAML serving

---

### `config`

Django project configuration.

Main responsibilities:

- URL routing
- WSGI/ASGI config
- Celery app initialization
- Django project settings

---

## Project Structure
#only Important files and folders are listed here for brevity. 
```text
chatbvp-control-tower/
│
├── adapters/
│   ├── matrix_client.py
│   └── ollama_client.py
│
├── audit/
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── celery.py
│   ├── urls.py
│   ├── settings.py
│   └── wsgi.py
│
├── controltower/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── swagger_views.py
│
├── dashboard/
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── events/
│   ├── models.py
│   └── services.py
│
├── intake/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── team/
│   ├── email_utils.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── templates/
│   └── base.html
│
├── workflows/
│   └── tasks.py
│
├── manage.py
├── requirements.txt
└── openapi.yaml
```

---

## Data Model Overview

### IntakeRequest

Stores raw user submission.

Fields include:

- `request_type`
- `first_name`
- `last_name`
- `email`
- `message`
- `created_at`

---

### OperationalEvent

Represents the event that drives workflow processing.

Fields include:

- `correlation_id`
- `event_type`
- `payload`
- `status`
- `created_at`

---

### Workspace

Represents the internal operational unit visible in the dashboard.

Fields include:

- `correlation_id`
- `event_type`
- `status`
- `matrix_room_id`
- `webui_session_id`
- `latest_summary`
- `next_actions`
- `requester_first_name`
- `requester_last_name`
- `requester_email`
- `owner_name`
- `structured_output`

---

### TeamMember

Represents internal team members.

Fields include:

- `first_name`
- `last_name`
- `email`
- `is_active`

---

### AuditLog

Stores workflow execution history.

Fields include:

- `correlation_id`
- `step_name`
- `status`
- `message`
- `created_at`

---

## Failure Handling and Retry Strategy

Control Tower is designed to make failures visible and recoverable.

### AI Failure

If Ollama fails or the model response cannot be generated:

- Workspace status becomes `AI_FAILED`
- Structured output is cleared
- Summary is updated to indicate AI failure
- Next action becomes retry or investigate audit logs
- Fallback email is sent to the requester
- Retry button becomes visible on the workspace detail page

Fallback customer message:

```text
We received your request, but the AI service failed to generate a response.
A team member will follow up shortly.
```

### Retry Flow

When the user clicks `Retry Workflow`:

1. The system finds the latest `OperationalEvent` for the workspace correlation ID.
2. Workspace status is updated to `IN_PROGRESS`.
3. Retry is logged in `AuditLog`.
4. Celery re-queues the workflow.
5. Ollama is called again.
6. Email and Matrix updates are attempted again.

This prevents failures from being silent and gives operators a recovery path.

---

## Observability and Audit Logging

Every important workflow step is logged using the audit module.

Common audit steps:

- `REQUESTER`
- `EVENT_RECEIVED`
- `EVENT_STATUS`
- `WORKSPACE_CREATED`
- `MATRIX_ROOM_CREATE`
- `MATRIX_POST_START`
- `AI_SESSION_CREATE`
- `AI_RESPONSE_GENERATED`
- `MATRIX_POST_AI`
- `EMAIL_SENT`
- `EMAIL_FAILED`
- `MATRIX_POST_EMAIL`
- `RETRY_REQUESTED`
- `WORKSPACE_STATUS`
- `WORKFLOW_EXCEPTION`

Audit logs are accessible by correlation ID and allow the team to debug failures, verify execution, and explain the lifecycle of a request.

---

## Local and VM Services

The project runs as a multi-service system.

Startup script example:

```bash
~/start-all.sh
```

Services started:

```text
Starting PostgreSQL...
Starting Redis...
Starting Ollama...
Starting Docker...
Starting Matrix...
Starting Celery...
Starting Django...
ALL SERVICES STARTED
```

Service responsibilities:

| Service | Responsibility |
| Django | Web UI, APIs, forms, dashboard |
| PostgreSQL | Persistent storage |
| Redis | Celery message broker |
| Celery | Background workflow execution |
| Ollama | Local LLM inference |
| Docker | Runs Matrix Synapse |
| Matrix Synapse | Collaboration rooms |
| SMTP | Customer and team email notifications |
| Google Cloud VM | Public deployment host |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd chatbvp-control-tower
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file or configure values in your deployment environment.

Required services include:

- PostgreSQL
- Redis
- Ollama
- Matrix Synapse
- SMTP email configuration

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start required services

```bash
~/start-all.sh
```

Or start services individually:

```bash
redis-server
ollama serve
celery -A config worker -l info
python manage.py runserver 0.0.0.0:8000
```

---

## Environment Variables

Example environment configuration:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain-or-ip

# Database
DB_NAME=controltower
DB_USER=ctuser
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Celery / Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Matrix
MATRIX_HOMESERVER_URL=http://localhost:8008
MATRIX_ACCESS_TOKEN=your-matrix-access-token
MATRIX_WEB_URL=http://localhost:8080
MATRIX_DEFAULT_INVITEES=[]

# Email / SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com
```


---

## Application Routes

| Route | Description |
| `/` | User intake form |
| `/dashboard/` | Internal dashboard |
| `/dashboard/ws/<id>/` | Workspace detail |
| `/dashboard/ws/<id>/retry/` | Retry failed workflow |
| `/audit/<correlation_id>/` | Audit logs |
| `/team/members/` | Team member management |
| `/swagger/` | Swagger UI |
| `/api/openapi.yaml` | OpenAPI specification |

---

## Deployment Notes

The project has been deployed on a Google Cloud Compute Engine VM and exposed publicly through the VM external IP.

Current deployment approach:

- Single VM deployment
- Django app running on VM
- PostgreSQL running on VM
- Redis running on VM
- Celery worker running on VM
- Ollama running locally on VM
- Matrix Synapse running through Docker
- SMTP used for outbound email

This is suitable for prototype and demo environments.

For production hardening, the system can be evolved into a containerized or managed-service architecture.

---

## Future Enhancements

Potential improvements:

- Docker Compose for all services
- Kubernetes deployment
- Role-based access control
- Login/authentication for dashboard
- Advanced reporting dashboard
- Matrix invite management from UI
- Configurable CC emails from database
- Admin-controlled AI model selection


---

## Engineering Highlights

This project demonstrates:

- Modular Django application design
- Event-driven workflow orchestration
- Asynchronous background processing
- External service integration through adapters
- Local LLM integration using Ollama
- Matrix-based collaboration workflow
- SMTP-based customer communication
- Persistent audit logging
- Failure recovery with retry mechanism
- Cloud VM deployment
- Production-style service orchestration

---


---

## Testing

The project includes automated unit and integration tests covering core system components and workflow execution.

### Test Structure

tests/
├── test_intake.py
├── test_events.py
├── test_dashboard.py
├── test_team.py
├── test_workflows.py


### Test Coverage

- Intake form validation and constraints  
- Operational event creation and correlation ID generation  
- Workspace creation and dashboard logic  
- Team member model and ownership behavior  
- End-to-end workflow execution  

### Integration Testing

The workflow test simulates:

- Event creation  
- Celery workflow execution  
- AI response generation (mocked)  
- Matrix room creation (mocked)  
- Email sending (mocked)  
- Workspace updates  

External dependencies such as Ollama, Matrix, and SMTP are mocked to ensure deterministic testing.


## API Documentation

The project includes Swagger/OpenAPI documentation for all major APIs.

Swagger UI:

```text
http://127.0.0.1:8000/swagger/

## OpenAPI Specification:
/api/openapi.yaml


Documented API categories include:

Intake APIs
Event APIs
Workspace APIs
Team Management APIs
Audit APIs


### Run Tests

```bash
python manage.py test UnitTestCases



## Resume Summary

Built and deployed an event-driven AI orchestration platform using Django, PostgreSQL, Redis, Celery, Ollama, Matrix, and SMTP. The system captures customer requests, creates trackable operational workspaces, generates AI-assisted responses, sends automated emails, enables real-time team collaboration, and provides full audit logging with retry-based failure recovery.

---

## Author

**Brahmendra Jayaraju**  
ChatBVP Control Tower  
Bison Venture Partners Project

---

## License

This project can be distributed under the MIT License.

