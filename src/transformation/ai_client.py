"""AI client wrapper for OpenAI GPT-4 and Anthropic Claude APIs."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import anthropic
from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError
from openai import APIError as OpenAIAPIError

from config.config import settings
from src.utils.logger import logger


@dataclass
class TokenUsage:
    """Track token usage and costs."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, prompt: int, completion: int, cost: float = 0.0):
        """Add token usage."""
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion
        self.cost_usd += cost

    def reset(self):
        """Reset all counters."""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.cost_usd = 0.0


# Pricing per 1M tokens (as of 2024)
PRICING = {
    "openai": {
        "gpt-4": {"prompt": 30.0, "completion": 60.0},  # $30/$60 per 1M tokens
        "gpt-4-turbo": {"prompt": 10.0, "completion": 30.0},
        "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
    },
    "anthropic": {
        "claude-3-opus-20240229": {"prompt": 15.0, "completion": 75.0},
        "claude-3-sonnet-20240229": {"prompt": 3.0, "completion": 15.0},
        "claude-3-haiku-20240307": {"prompt": 0.25, "completion": 1.25},
    },
}


class AIClient:
    """Wrapper for OpenAI and Anthropic APIs with rate limiting and retries."""

    def __init__(
        self,
        primary_provider: str = "openai",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_delay: float = 60.0,
    ):
        """
        Initialize AI client.

        Args:
            primary_provider: Primary provider ("openai" or "anthropic")
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            rate_limit_delay: Delay when rate limited in seconds
        """
        self.primary_provider = primary_provider
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay

        # Initialize clients
        self.openai_client: Optional[OpenAI] = None
        self.anthropic_client: Optional[anthropic.Anthropic] = None

        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Token usage tracking
        self.token_usage = TokenUsage()

        # Rate limiting tracking
        self.last_request_time: Dict[str, float] = {}
        self.min_request_interval = 0.1  # Minimum 100ms between requests

    def _calculate_cost(
        self, provider: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """
        Calculate cost for API usage.

        Args:
            provider: Provider name ("openai" or "anthropic")
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Cost in USD
        """
        pricing = PRICING.get(provider, {}).get(model, {})
        if not pricing:
            logger.warning(f"Unknown pricing for {provider}/{model}, cost tracking disabled")
            return 0.0

        prompt_cost = (prompt_tokens / 1_000_000) * pricing.get("prompt", 0)
        completion_cost = (completion_tokens / 1_000_000) * pricing.get("completion", 0)

        return prompt_cost + completion_cost

    def _rate_limit_check(self, provider: str):
        """
        Check and enforce rate limiting.

        Args:
            provider: Provider name
        """
        current_time = time.time()
        last_time = self.last_request_time.get(provider, 0)

        if current_time - last_time < self.min_request_interval:
            sleep_time = self.min_request_interval - (current_time - last_time)
            time.sleep(sleep_time)

        self.last_request_time[provider] = time.time()

    def _call_openai(
        self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Call OpenAI API.

        Args:
            prompt: User prompt
            model: Model name (defaults to settings.OPENAI_MODEL)
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for OpenAI API

        Returns:
            Response dictionary with content and usage
        """
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Set OPENAI_API_KEY.")

        model = model or settings.OPENAI_MODEL
        self._rate_limit_check("openai")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(self.max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )

                content = response.choices[0].message.content
                usage = response.usage

                # Track usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                cost = self._calculate_cost("openai", model, prompt_tokens, completion_tokens)
                self.token_usage.add(prompt_tokens, completion_tokens, cost)

                logger.debug(
                    f"OpenAI API call: {prompt_tokens} prompt + {completion_tokens} completion = "
                    f"{prompt_tokens + completion_tokens} total tokens, ${cost:.4f}"
                )

                return {
                    "content": content,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    },
                    "cost_usd": cost,
                }

            except OpenAIRateLimitError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"OpenAI rate limit hit, retrying in {self.rate_limit_delay}s...")
                    time.sleep(self.rate_limit_delay)
                else:
                    logger.error(f"OpenAI rate limit exceeded after {self.max_retries} attempts")
                    raise

            except OpenAIAPIError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"OpenAI API error: {e}, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"OpenAI API error after {self.max_retries} attempts: {e}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error calling OpenAI API: {e}")
                raise

    def _call_anthropic(
        self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Call Anthropic Claude API.

        Args:
            prompt: User prompt
            model: Model name (defaults to settings.ANTHROPIC_MODEL)
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for Anthropic API

        Returns:
            Response dictionary with content and usage
        """
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

        model = model or settings.ANTHROPIC_MODEL
        self._rate_limit_check("anthropic")

        for attempt in range(self.max_retries):
            try:
                response = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=kwargs.pop("max_tokens", 4096),
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )

                content = response.content[0].text
                usage = response.usage

                # Track usage
                prompt_tokens = usage.input_tokens
                completion_tokens = usage.output_tokens
                cost = self._calculate_cost("anthropic", model, prompt_tokens, completion_tokens)
                self.token_usage.add(prompt_tokens, completion_tokens, cost)

                logger.debug(
                    f"Anthropic API call: {prompt_tokens} prompt + {completion_tokens} completion = "
                    f"{prompt_tokens + completion_tokens} total tokens, ${cost:.4f}"
                )

                return {
                    "content": content,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    },
                    "cost_usd": cost,
                }

            except anthropic.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Anthropic rate limit hit, retrying in {self.rate_limit_delay}s...")
                    time.sleep(self.rate_limit_delay)
                else:
                    logger.error(f"Anthropic rate limit exceeded after {self.max_retries} attempts")
                    raise

            except anthropic.APIError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Anthropic API error: {e}, retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Anthropic API error after {self.max_retries} attempts: {e}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error calling Anthropic API: {e}")
                raise

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content using AI API (with fallback).

        Args:
            prompt: User prompt
            model: Model name (optional, uses default from settings)
            system_prompt: Optional system prompt
            provider: Provider to use ("openai" or "anthropic"), defaults to primary_provider
            **kwargs: Additional arguments for API

        Returns:
            Response dictionary with content, usage, and cost
        """
        provider = provider or self.primary_provider

        try:
            if provider == "openai":
                return self._call_openai(prompt, model, system_prompt, **kwargs)
            elif provider == "anthropic":
                return self._call_anthropic(prompt, model, system_prompt, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            # Fallback to alternative provider
            if provider == "openai" and self.anthropic_client:
                logger.warning(f"OpenAI failed, falling back to Anthropic: {e}")
                return self._call_anthropic(prompt, model, system_prompt, **kwargs)
            elif provider == "anthropic" and self.openai_client:
                logger.warning(f"Anthropic failed, falling back to OpenAI: {e}")
                return self._call_openai(prompt, model, system_prompt, **kwargs)
            else:
                raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current token usage statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "prompt_tokens": self.token_usage.prompt_tokens,
            "completion_tokens": self.token_usage.completion_tokens,
            "total_tokens": self.token_usage.total_tokens,
            "cost_usd": round(self.token_usage.cost_usd, 4),
        }

    def reset_usage(self):
        """Reset token usage tracking."""
        self.token_usage.reset()

