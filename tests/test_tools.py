"""Unit tests — client is stubbed via patching."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import instanode
from crewai_instanode_tools import (
    ListResourcesTool,
    ProvisionMongoTool,
    ProvisionPostgresTool,
    ProvisionWebhookTool,
)


def _fake_result(url: str = "postgres://u:p@h/db") -> SimpleNamespace:
    return SimpleNamespace(
        connection_url=url,
        tier="anonymous",
        limits=SimpleNamespace(storage_mb=10, connections=2, expires_in="24h"),
    )


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_postgres_tool_returns_dsn(client_cls):
    client = MagicMock()
    client.provision_database.return_value = _fake_result("postgres://ok")
    client_cls.return_value = client
    tool = ProvisionPostgresTool()
    out = tool._run()
    assert "postgres://ok" in out


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_postgres_tool_forwards_name(client_cls):
    client = MagicMock()
    client.provision_database.return_value = _fake_result()
    client_cls.return_value = client
    tool = ProvisionPostgresTool()
    tool._run(name="label-xyz")
    client.provision_database.assert_called_once_with(name="label-xyz")


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_webhook_tool_returns_url(client_cls):
    client = MagicMock()
    client.provision_webhook.return_value = _fake_result("https://hook/abc")
    client_cls.return_value = client
    tool = ProvisionWebhookTool()
    assert "https://hook/abc" in tool._run()


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_mongo_tool_returns_uri(client_cls):
    client = MagicMock()
    client.provision_mongodb.return_value = _fake_result("mongodb://ok/db")
    client_cls.return_value = client
    tool = ProvisionMongoTool()
    assert "mongodb://ok/db" in tool._run()


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_error_is_returned_not_raised(client_cls):
    client = MagicMock()
    client.provision_database.side_effect = instanode.InstanodeError(
        429, "rate_limited", "too many requests"
    )
    client_cls.return_value = client
    tool = ProvisionPostgresTool()
    out = tool._run()
    assert out.startswith("ERROR:")
    assert "too many requests" in out


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_list_empty(client_cls):
    client = MagicMock()
    client.list_resources.return_value = []
    client_cls.return_value = client
    tool = ListResourcesTool()
    assert tool._run() == "No resources."


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_list_formatted(client_cls):
    client = MagicMock()
    client.list_resources.return_value = [
        SimpleNamespace(service="postgres", tier="hobby", created_at="2026-04-19T10:00Z")
    ]
    client_cls.return_value = client
    tool = ListResourcesTool()
    out = tool._run()
    assert "postgres" in out and "hobby" in out


@patch("crewai_instanode_tools.tools.instanode.Client")
def test_constructor_accepts_explicit_api_key(client_cls):
    ProvisionPostgresTool(api_key="sk_test")
    # The `api_key` kwarg should reach instanode.Client at construction time.
    client_cls.assert_called_once()
    kwargs = client_cls.call_args.kwargs
    assert kwargs["api_key"] == "sk_test"
