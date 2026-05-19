# Changelog

All notable changes to ChatBVP Control Tower will be documented in this file.

this project follows Semantic Versioning.

---

# [v1.0.0] - 2026-05-11

## Added

- Centralized intake request system
- Event-driven workflow orchestration
- Celery + Redis asynchronous processing
- Ollama integration using llama3
- Dashboard for workflow visibility
- Matrix collaboration room support
- SMTP email notification system
- Audit logging system
- Retry workflow functionality
- Team member management module
- Swagger documentation
- Google Cloud VM deployment
- GitHub Actions CI workflow
- Unit and integration testing setup

---

## Changed

- Improved dashboard UI styling
- Updated workflow status handling
- Refined AI response formatting
- Added owner assignment support
- Enhanced audit log visibility

---

## Fixed

- Fixed workflow final status logic
- Fixed retry handling for failed AI workflows
- Fixed dashboard filtering behavior
- Fixed Matrix room link generation
- Fixed email notification formatting

---

## Documentation

- Added detailed README.md
- Added installation and deployment instructions
- Added MIT license

---

## Known Issues

- Ollama inference latency depends on VM resources
- Single VM deployment architecture
- Authentication system not yet implemented
- No Kubernetes orchestration yet
- Limited horizontal scalability

---

## Future Improvements

- Add authentication
- Add Kubernetes deployment
- Add monitoring dashboards
- Add multi-worker scaling
- Add GPU-backed inference support
- Add advanced analytics and reporting