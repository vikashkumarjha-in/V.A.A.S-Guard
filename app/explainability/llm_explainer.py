import httpx
import json
from config import settings
from app.models.schemas import ThreatEvent
import logging

logger = logging.getLogger(__name__)

class LLMExplainer:
    async def explain_threat(self, event: ThreatEvent) -> str:
        if settings.LLM_PROVIDER == "openai":
            return await self._explain_openai(event)
        elif settings.LLM_PROVIDER == "anthropic":
            return await self._explain_anthropic(event)
        else:
            return "No LLM provider configured."

    async def _explain_openai(self, event: ThreatEvent) -> str:
        if not settings.OPENAI_API_KEY:
            return "OpenAI API Key missing."

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"Analyze this potential security threat and explain why it was flagged. Event: {event.json()}"

        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json=data, timeout=10.0)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI Error: {e}")
            return f"Failed to get explanation from OpenAI: {str(e)}"

    async def _explain_anthropic(self, event: ThreatEvent) -> str:
        if not settings.ANTHROPIC_API_KEY:
            return "Anthropic API Key missing."

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        prompt = f"Analyze this potential security threat and explain why it was flagged. Event: {event.json()}"

        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json=data, timeout=10.0)
                resp.raise_for_status()
                return resp.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Anthropic Error: {e}")
            return f"Failed to get explanation from Anthropic: {str(e)}"

llm_explainer = LLMExplainer()
