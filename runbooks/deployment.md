# Deployment Failure Troubleshooting Runbook

## Common Symptoms

- Application fails immediately after deployment
- New version does not start
- Health checks fail
- Previously working endpoints return errors

## Common Causes

- Missing environment variables
- Invalid application configuration
- Dependency version conflicts
- Database migration failures
- Incorrect build artifacts
- Deployment introduced a regression

## Investigation Steps

1. Review deployment logs.
2. Compare configuration with the previous working release.
3. Verify required environment variables.
4. Check application startup logs.
5. Verify database migrations.
6. Review recent code changes.
7. Check health endpoints.

## Resolution

Correct the deployment configuration or application defect. Roll back to the previous stable release when immediate restoration is required.
