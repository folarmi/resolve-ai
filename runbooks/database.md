# Database Troubleshooting Runbook

## Common Symptoms

- Connection refused
- Connection timeout
- Database queries failing
- Application returning 500 errors
- Connection pool exhausted

## Common Causes

- Database service is unavailable
- Incorrect connection string
- Invalid credentials
- Network connectivity problems
- Connection pool exhaustion
- Slow or blocked queries

## Investigation Steps

1. Verify the database service is running.
2. Test connectivity from the application host.
3. Verify the database host and port.
4. Validate database credentials.
5. Review active connections and connection pool usage.
6. Inspect slow queries and locks.
7. Review database logs.

## Resolution

Restore the database service, correct connection configuration, resolve network issues, optimize problematic queries, or increase connection capacity when appropriate.
