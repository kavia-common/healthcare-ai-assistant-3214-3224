"""
OpenAI integration utilities for dual-agent conversation.
"""

from typing import Tuple
import httpx
from .config import get_settings

# Using REST call to OpenAI chat completions to avoid requiring new SDKs
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def _headers():
    settings = get_settings()
    if not settings.openai_api_key:
        # In absence of key, return None and the caller should handle mock response
        return None
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }


async def _post_chat(
    messages,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> str:
    """
    Call OpenAI Chat Completions API and return the assistant message content.
    If OPENAI_API_KEY is not set, return a deterministic mock response.
    """
    headers = _headers()
    if not headers:
        # Mock response for local dev without key
        prompt = " ".join(
            [m.get("content", "") for m in messages if m.get("role") == "user"]
        )
        return f"[MOCK AI] Based on your input: {prompt[:100]}..."

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # Extract assistant message content with readable wrapping
        choice = data["choices"][0]
        msg = choice["message"]
        content = msg["content"]
        return content


# PUBLIC_INTERFACE
async def get_dual_agent_responses(user_message: str) -> Tuple[str, str]:
    """Get responses from Agent 1 (triage/questions) and Agent 2 (medicine recommendation)."""
    # Agent 1 prompt
    agent1_messages = [
        {
            "role": "system",
            "content": (
                "You are Agent 1, a compassionate healthcare intake assistant. "
                "Ask clarifying health-related questions, summarize symptoms succinctly, "
                "and capture relevant medical history if appropriate."
            ),
        },
        {"role": "user", "content": user_message},
    ]
    agent1_reply = await _post_chat(agent1_messages, temperature=0.3)

    # Agent 2 prompt uses both user input and Agent1 summary
    agent2_messages = [
        {
            "role": "system",
            "content": (
                "You are Agent 2, a healthcare assistant that suggests over-the-counter medicine "
                "or next steps. Provide general guidance, dosage cautions, and advise consulting a "
                "professional when necessary. Avoid diagnosing definitively."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Patient said: {user_message}\n"
                f"Agent1 summary: {agent1_reply}"
            ),
        },
    ]
    agent2_reply = await _post_chat(agent2_messages, temperature=0.4)

    return agent1_reply, agent2_reply
