from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


DEEPINFRA_URL = "https://api.deepinfra.com/v1/openai/chat/completions"


@dataclass
class ProviderResult:
    ok: bool
    content: str
    reasoning_content: str
    response_id: str | None
    finish_reason: str | None
    usage: dict[str, Any]
    latency_ms: int
    http_status: int | None
    error: str | None
    response_body: dict[str, Any] | None


class DeepInfraProvider:
    name = "deepinfra"

    def __init__(self, api_key: str | None = None, timeout_seconds: int = 180):
        self.api_key = api_key or os.environ.get("DEEPINFRA_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPINFRA_API_KEY is not set")
        self.timeout_seconds = timeout_seconds

    def complete(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        seed: int,
        max_tokens: int,
    ) -> ProviderResult:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "stream": False,
        }
        started = time.perf_counter()
        try:
            response = requests.post(
                DEEPINFRA_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            latency_ms = round((time.perf_counter() - started) * 1000)
            try:
                body = response.json()
            except ValueError:
                body = None
            if response.status_code >= 400:
                detail = body if body is not None else response.text[:1000]
                return ProviderResult(
                    False,
                    "",
                    "",
                    None,
                    None,
                    {},
                    latency_ms,
                    response.status_code,
                    f"HTTP {response.status_code}: {detail}",
                    body,
                )
            choices = (body or {}).get("choices") or []
            if not choices:
                return ProviderResult(
                    False,
                    "",
                    "",
                    (body or {}).get("id"),
                    None,
                    (body or {}).get("usage") or {},
                    latency_ms,
                    response.status_code,
                    "response contained no choices",
                    body,
                )
            choice = choices[0]
            message = choice.get("message") or {}
            content = str(message.get("content") or "").strip()
            reasoning = str(message.get("reasoning_content") or "").strip()
            return ProviderResult(
                bool(content),
                content,
                reasoning,
                (body or {}).get("id"),
                choice.get("finish_reason"),
                (body or {}).get("usage") or {},
                latency_ms,
                response.status_code,
                None if content else "empty response content",
                body,
            )
        except requests.RequestException as exc:
            latency_ms = round((time.perf_counter() - started) * 1000)
            return ProviderResult(
                False,
                "",
                "",
                None,
                None,
                {},
                latency_ms,
                None,
                f"{type(exc).__name__}: {exc}",
                None,
            )
