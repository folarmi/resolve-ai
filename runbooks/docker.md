# Docker Troubleshooting Runbook

## Common Symptoms

- Container repeatedly restarts
- Container exits immediately
- Application is unreachable
- Port binding errors
- Image build fails

## Common Causes

- Application process crashes
- Missing environment variables
- Incorrect port mapping
- Invalid Docker image
- Resource exhaustion
- Dependency installation failure

## Investigation Steps

1. Check container status.
2. Inspect container logs.
3. Inspect the container exit code.
4. Verify environment variables.
5. Verify exposed and mapped ports.
6. Check CPU and memory usage.
7. Review Docker build output.

## Resolution

Correct the application or container configuration, rebuild the image when necessary, and restart or redeploy the container.
