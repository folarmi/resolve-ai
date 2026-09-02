# Authentication Troubleshooting Runbook

## Common Symptoms

- HTTP 401 Unauthorized
- HTTP 403 Forbidden
- Users unexpectedly logged out
- Invalid or expired token errors
- Login requests failing

## Common Causes

- Expired access token
- Invalid JWT signature
- Incorrect authentication credentials
- Missing authorization header
- Incorrect permissions or roles
- Authentication service unavailable

## Investigation Steps

1. Verify the Authorization header is present.
2. Check whether the access token has expired.
3. Validate the token signature and issuer.
4. Confirm the user has the required permissions.
5. Review authentication service logs.
6. Check recent authentication configuration changes.

## Resolution

Refresh expired credentials, correct authentication configuration, restore the authentication service, or update incorrect permissions.
