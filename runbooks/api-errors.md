# API Error Troubleshooting Runbook

## 500 Internal Server Error

### Common Causes

- Unhandled application exceptions
- Invalid configuration
- Database failures
- Missing environment variables
- Dependency failures

### Investigation Steps

1. Review application logs and stack traces.
2. Identify the failing endpoint.
3. Check recent deployments or configuration changes.
4. Verify database and external service connectivity.
5. Confirm required environment variables are configured.

### Resolution

Fix the underlying application exception or configuration issue and redeploy the affected service.

## 502 Bad Gateway

### Common Causes

- Upstream service is unavailable
- Backend application failed to start
- Reverse proxy points to an incorrect host or port
- Network connectivity failure
- Backend service crashed

### Investigation Steps

1. Verify the upstream application is running.
2. Check the backend listening port.
3. Test direct connectivity to the upstream service.
4. Review reverse proxy configuration.
5. Review application and proxy logs.

### Resolution

Restore the upstream service or correct the proxy/network configuration preventing communication.

## 503 Service Unavailable

### Common Causes

- Service overload
- Application maintenance
- Failed health checks
- Insufficient application instances

### Investigation Steps

1. Check service health.
2. Review CPU and memory utilization.
3. Check load balancer health checks.
4. Verify application instances are running.

### Resolution

Restore unhealthy instances, correct health checks, or scale the service when capacity is insufficient.
