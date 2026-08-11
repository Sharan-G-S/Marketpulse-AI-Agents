"""
MarketPulse — Healthcheck Utility for Docker Containers
Checks application readiness and reports exit code 0 for healthy, 1 for unhealthy.
"""

import sys


def check_health() -> bool:
    try:
        from graph.workflow import build_graph
        g = build_graph()
        return g is not None
    except Exception as e:
        print(f"Healthcheck failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    is_healthy = check_health()
    sys.exit(0 if is_healthy else 1)
