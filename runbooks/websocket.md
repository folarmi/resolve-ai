# WebSocket Troubleshooting Runbook

## Common Symptoms

- WebSocket connection fails
- Connection closes unexpectedly
- Messages are not received
- HTTP upgrade fails
- Frequent reconnections

## Common Causes

- Incorrect WebSocket URL
- Proxy does not support connection upgrade
- Authentication failure
- Firewall or network interruption
- Client subscription error
- Server-side connection failure

## Investigation Steps

1. Verify the WebSocket URL.
2. Confirm the server is reachable.
3. Check HTTP Upgrade and Connection headers.
4. Verify authentication credentials.
5. Review proxy WebSocket configuration.
6. Inspect client and server logs.
7. Verify topic or channel subscriptions.

## Resolution

Correct the WebSocket endpoint, authentication, proxy configuration, network configuration, or subscription logic causing the connection failure.
