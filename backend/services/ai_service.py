import json
import random
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaAIService:
    """Calls a locally running Ollama instance. Zero cost, zero API key."""

    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL

    def chat_completion(self, messages: list[dict], system: str) -> str:
        import ollama

        full_messages = [{"role": "system", "content": system}] + messages
        response = ollama.chat(
            model=self.model,
            messages=full_messages,
            options={"temperature": 0.7},
        )
        return response["message"]["content"]

    def structured_completion(self, prompt: str, system: str) -> dict:
        import ollama

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            format="json",
            options={"temperature": 0.2},
        )
        raw = response["message"]["content"]
        return json.loads(raw)


class MockAIService:
    """Deterministic fallback used when Ollama is not running.
    Returns realistic templated responses so the demo always works."""

    _CHAT_RESPONSES = [
        "Based on your description, I recommend checking the system logs first. Look for error codes starting with 0x or any timeout messages that could indicate the root cause.",
        "This is a common IT issue. Let me walk you through the standard troubleshooting steps: First, restart the affected service. If the issue persists, check network connectivity, then review recent configuration changes.",
        "For this type of issue, the quickest resolution is usually to clear the application cache and restart. If that doesn't work, we'll need to escalate to the Application Support team.",
        "I've seen this pattern before — it often indicates a resource exhaustion issue. Check CPU, memory, and disk usage on the affected system. Use 'top' on Linux or Task Manager on Windows.",
        "Good question. This falls under Access/Authentication issues. The recommended approach is: verify user account status in Active Directory, reset credentials, then confirm MFA configuration is correct.",
    ]

    _MOCK_ANALYSIS = {
        "network": {
            "category": "Network",
            "assignment_group": "Network Operations",
            "troubleshooting_steps": [
                "Check physical network connections and switch port status",
                "Ping gateway and DNS servers to isolate connectivity scope",
                "Review network switch logs for error or flap events",
                "Verify VLAN configuration and routing tables",
                "Escalate to ISP if external connectivity is affected",
            ],
        },
        "security": {
            "category": "Security",
            "assignment_group": "Security Operations Center",
            "troubleshooting_steps": [
                "Immediately isolate affected systems from the network",
                "Preserve system state — do not power off before forensic capture",
                "Alert the Security Operations Center and begin incident response",
                "Review firewall and SIEM logs for indicators of compromise",
                "Follow the organisation's IR runbook for containment and eradication",
            ],
        },
        "default": {
            "category": "Software/Application",
            "assignment_group": "Application Support",
            "troubleshooting_steps": [
                "Collect and review application error logs",
                "Reproduce the issue in a test environment",
                "Check for recent deployments or configuration changes",
                "Review resource utilisation (CPU, memory, disk)",
                "Escalate to the development team if a code defect is suspected",
            ],
        },
    }

    def chat_completion(self, messages: list[dict], system: str) -> str:
        last = messages[-1]["content"].lower() if messages else ""
        if any(w in last for w in ["password", "login", "access", "auth"]):
            return "For authentication issues: verify the account is not locked in Active Directory, reset the password, confirm MFA device registration, and clear browser cookies/cache before retrying."
        if any(w in last for w in ["slow", "performance", "lag", "cpu", "memory"]):
            return "Performance issues typically stem from resource contention. Check top-level metrics first: CPU utilisation, available memory, disk I/O wait, and network latency. Use APM tooling if available to trace bottlenecks to a specific service or query."
        if any(w in last for w in ["network", "internet", "connectivity", "ping", "vpn"]):
            return "Network connectivity issues: start with a ping to the default gateway. If that fails, the problem is local (NIC, cable, switch port). If the gateway responds but internet is down, check upstream routing and DNS resolution. For VPN, verify the client version matches the server and check certificate validity."
        return random.choice(self._CHAT_RESPONSES)

    def structured_completion(self, prompt: str, system: str) -> dict:
        p = prompt.lower()
        if any(w in p for w in ["ransomware", "breach", "malware", "attack", "hack"]):
            profile = self._MOCK_ANALYSIS["security"]
            severity, label, users, eta = "P1", "Critical", 50, "Immediate — follow IR runbook"
        elif any(w in p for w in ["outage", "down", "unreachable", "offline", "switch", "router"]):
            profile = self._MOCK_ANALYSIS["network"]
            severity, label, users, eta = "P2", "High", 30, "2-4 hours"
        else:
            profile = self._MOCK_ANALYSIS["default"]
            severity, label, users, eta = "P3", "Medium", 5, "4–8 hours"

        return {
            "summary": (
                "This incident has been automatically triaged by the AIOps system. "
                "The description indicates a potential service disruption requiring prompt attention. "
                "Immediate investigation is recommended following the steps below."
            ),
            "category": profile["category"],
            "severity": severity,
            "severity_label": label,
            "assignment_group": profile["assignment_group"],
            "troubleshooting_steps": profile["troubleshooting_steps"],
            "estimated_resolution_time": eta,
            "confidence_score": 0.72,
        }


def get_ai_service() -> tuple[object, str]:
    """Return (service_instance, mode_label). Tries Ollama first, falls back to Mock."""
    try:
        import ollama

        ollama.list()  # lightweight connectivity check
        logger.info("Ollama is available — using local LLM (%s)", settings.OLLAMA_MODEL)
        return OllamaAIService(), "ollama"
    except Exception as exc:
        logger.warning("Ollama not reachable (%s) — falling back to mock responses", exc)
        return MockAIService(), "mock"
