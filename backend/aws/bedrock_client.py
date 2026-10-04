"""Single entry point for every LLM call (Bedrock, or the offline mock)."""
import json
import logging
import os

from config import env_bool
from aws import mock_llm

log = logging.getLogger("echomind.bedrock")
_client = None


def _get_client():
    global _client
    if _client is None:
        import boto3
        _client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return _client


def llm_mode() -> str:
    return "mock" if env_bool("USE_MOCK_LLM") else "bedrock"


def ask(prompt: str, system: str = "", max_tokens: int = 1024) -> str:
    if env_bool("USE_MOCK_LLM"):
        log.info("MOCK LLM CALL prompt_len=%d", len(prompt))
        return mock_llm.respond(prompt, system)

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    log.info("BEDROCK CALL -> model=%s prompt_len=%d", model_id, len(prompt))
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    resp = _get_client().invoke_model(modelId=model_id, body=json.dumps(body))
    out = json.loads(resp["body"].read())["content"][0]["text"]
    log.info("BEDROCK RESP <- %d chars", len(out))
    return out


def health_check() -> bool:
    if env_bool("USE_MOCK_LLM"):
        return True
    try:
        out = ask("Reply with exactly: OK", max_tokens=10)
        log.info("BEDROCK HEALTH: %s", out)
        return out.strip().upper().startswith("OK")
    except Exception as e:  # noqa: BLE001
        log.error("BEDROCK HEALTH FAILED: %s", e)
        return False
