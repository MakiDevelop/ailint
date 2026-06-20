# Project Guidelines

## Code Style

All code must follow PEP 8. Use type hints for function signatures. Maximum line length is 120 characters.

## Git Workflow

Create a branch for each feature. Write commit messages in imperative mood. Rebase before merging.

## Testing

Write unit tests for all public functions. Maintain at least 80% code coverage. Run the full test suite before pushing.

## Security

Never commit secrets or API keys. Use environment variables for configuration. Validate all user input at system boundaries.

## Deployment

Deploy to staging first. Run smoke tests after deployment. Roll back immediately if health checks fail.
