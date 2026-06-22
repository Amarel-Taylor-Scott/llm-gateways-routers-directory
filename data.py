"""LLM Gateways & Routers Directory — curated registry.

A catalog of **LLM gateways, proxies, and routers** — the layer that sits between
your app and the model providers to give you one unified API, routing,
fallbacks, retries, caching, rate-limiting, and cost control across many LLMs.

This is distinct from the inference engines that *serve* models and from the raw
provider endpoints: these tools *route and manage* calls across providers. Each
entry records: name, org, category, whether it is open source, its license (or
"Proprietary"), a short note, and a canonical link (GitHub repo for OSS, homepage
for hosted services). Uncertain licenses/URLs are omitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(Enum):
    open_source_gateway = "open_source_gateway"
    managed_router_gateway = "managed_router_gateway"

    @property
    def label(self) -> str:
        return {
            "open_source_gateway": "Open-Source Gateways & Routers",
            "managed_router_gateway": "Managed Gateways & Routers",
        }[self.value]


@dataclass(frozen=True)
class Tool:
    name: str
    org: str
    category: Category
    url: str               # GitHub repo for OSS, homepage for hosted services
    open_source: bool
    license: str           # SPDX-ish id, or "Proprietary"
    note: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Registry — curated, public LLM gateways/routers (links only).
# Licenses verified to best effort; uncertain ones omitted.
# ---------------------------------------------------------------------------
TOOLS: list[Tool] = [
    # --- Open-source gateways & routers ---
    Tool("LiteLLM", "BerriAI", Category.open_source_gateway,
         "https://github.com/BerriAI/litellm", True, "MIT",
         note="Proxy + Python SDK to call 100+ LLM APIs via one OpenAI-compatible interface.",
         tags=("proxy", "openai-compatible", "popular")),
    Tool("Portkey AI Gateway", "Portkey", Category.open_source_gateway,
         "https://github.com/Portkey-AI/gateway", True, "MIT",
         note="Fast open-source AI gateway: routing, fallbacks, retries across providers.",
         tags=("gateway", "fallbacks")),
    Tool("Kong AI Gateway", "Kong", Category.open_source_gateway,
         "https://github.com/Kong/kong", True, "Apache-2.0",
         note="AI Gateway plugins on Kong for routing, auth, and rate-limiting LLM traffic.",
         tags=("api-gateway", "plugins")),
    Tool("RouteLLM", "LMSYS", Category.open_source_gateway,
         "https://github.com/lm-sys/RouteLLM", True, "Apache-2.0",
         note="Framework to route between strong/weak models to cut cost.",
         tags=("router", "cost")),
    Tool("One API", "songquanpeng", Category.open_source_gateway,
         "https://github.com/songquanpeng/one-api", True, "MIT",
         note="Self-hosted, OpenAI-compatible gateway/distributor for many model providers.",
         tags=("self-hosted", "distributor")),

    # --- Managed gateways & routers ---
    Tool("OpenRouter", "OpenRouter", Category.managed_router_gateway,
         "https://openrouter.ai", False, "Proprietary",
         note="Unified API that routes across many LLMs/providers with a single key.",
         tags=("router", "unified", "popular")),
    Tool("Eden AI", "Eden AI", Category.managed_router_gateway,
         "https://www.edenai.co", False, "Proprietary",
         note="Single API aggregating many AI/LLM providers and tasks.",
         tags=("aggregator", "api")),
    Tool("Cloudflare AI Gateway", "Cloudflare", Category.managed_router_gateway,
         "https://developers.cloudflare.com/ai-gateway/", False, "Proprietary",
         note="Managed gateway: caching, rate-limiting, and analytics for LLM API calls.",
         tags=("caching", "analytics")),
]
