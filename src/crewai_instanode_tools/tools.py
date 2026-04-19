"""
tools.py — CrewAI BaseTool subclasses for instanode.dev provisioning.

CrewAI's tool contract:
- Subclass `crewai.tools.BaseTool`.
- Declare `name`, `description` as class attributes.
- Declare `args_schema` pointing at a Pydantic model for structured args.
- Implement `_run(...)` returning a string that the LLM sees.

Each tool is a thin adapter over a method on `instanode.Client`. Errors
are caught and returned as strings (never raised) so a retrying agent
can recover gracefully.
"""

from __future__ import annotations

import os
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

import instanode


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ProvisionDBArgs(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Optional human-readable label shown in the instanode dashboard.",
    )


class _ProvisionWebhookArgs(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Optional label for the webhook receiver.",
    )


class _ProvisionMongoArgs(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Optional label for the MongoDB database.",
    )


class _EmptyArgs(BaseModel):
    """No arguments."""


# ---------------------------------------------------------------------------
# Shared client lifecycle
# ---------------------------------------------------------------------------


def _make_client(api_key: Optional[str], base_url: Optional[str]) -> instanode.Client:
    return instanode.Client(
        api_key=api_key or os.environ.get("INSTANODE_API_KEY"),
        base_url=base_url or os.environ.get("INSTANODE_API_URL"),
    )


# ---------------------------------------------------------------------------
# Tool classes
# ---------------------------------------------------------------------------


class _InstanodeBase(BaseTool):
    """Shared base holding a private client instance."""

    _client: instanode.Client = PrivateAttr()

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **data,
    ) -> None:
        super().__init__(**data)
        self._client = _make_client(api_key, base_url)


class ProvisionPostgresTool(_InstanodeBase):
    name: str = "provision_postgres"
    description: str = (
        "Provision a new Postgres database at instanode.dev and return its "
        "connection URL. Use for structured storage, SQL queries, or vector "
        "embeddings (pgvector is pre-installed). Free-tier databases expire "
        "in 24 hours; paid-tier are permanent."
    )
    args_schema: Type[BaseModel] = _ProvisionDBArgs

    def _run(self, name: Optional[str] = None) -> str:
        try:
            res = self._client.provision_database(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return (
            f"Postgres ready. DSN: {res.connection_url} "
            f"(tier={res.tier}, storage_mb={res.limits.storage_mb}, "
            f"expires_in={res.limits.expires_in})"
        )


class ProvisionWebhookTool(_InstanodeBase):
    name: str = "provision_webhook"
    description: str = (
        "Provision an HTTPS webhook receiver URL. Accepts any POST and stores "
        "the last 100 request bodies for later inspection. Use for GitHub "
        "webhooks, Stripe events, Slack slash commands, or any third-party "
        "callback."
    )
    args_schema: Type[BaseModel] = _ProvisionWebhookArgs

    def _run(self, name: Optional[str] = None) -> str:
        try:
            res = self._client.provision_webhook(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return f"Webhook URL: {res.connection_url} (tier={res.tier})"


class ProvisionMongoTool(_InstanodeBase):
    name: str = "provision_mongo"
    description: str = (
        "Provision a MongoDB database and return a mongodb:// URI. Use for "
        "document/JSON workloads."
    )
    args_schema: Type[BaseModel] = _ProvisionMongoArgs

    def _run(self, name: Optional[str] = None) -> str:
        try:
            res = self._client.provision_mongodb(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return f"MongoDB URI: {res.connection_url} (tier={res.tier})"


class ListResourcesTool(_InstanodeBase):
    name: str = "list_resources"
    description: str = (
        "List every instanode.dev resource owned by the current API key. "
        "Requires INSTANODE_API_KEY. Useful to avoid re-provisioning "
        "something that already exists."
    )
    args_schema: Type[BaseModel] = _EmptyArgs

    def _run(self) -> str:
        try:
            resources = self._client.list_resources()
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        if not resources:
            return "No resources."
        return "Resources:\n" + "\n".join(
            f"- {r.service} ({r.tier}) created {r.created_at}" for r in resources
        )
