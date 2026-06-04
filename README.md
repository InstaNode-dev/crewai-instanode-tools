# crewai-instanode-tools — provision a database from a CrewAI agent in one call

**CrewAI tools for [instanode.dev](https://instanode.dev).** Let a CrewAI agent
provision a real Postgres database (pgvector pre-installed) or a webhook receiver
mid-task with a single tool call — no signup, no Docker, no setup. Free anonymous
tier (24h TTL). Prefer MCP? Use the [instanode MCP server](https://www.npmjs.com/package/@instanode/mcp)
(Claude Code / Cursor / Copilot / Windsurf) instead.

```bash
pip install crewai-instanode-tools
```

## Use it from a CrewAI agent

```python
from crewai import Agent, Task, Crew
from crewai_instanode_tools import (
    ProvisionPostgresTool,
    ProvisionWebhookTool,
    ListResourcesTool,
)

provisioner = Agent(
    role="Infrastructure provisioner",
    goal="Give the team working database URLs with zero setup.",
    backstory="Spins up Postgres + webhooks via instanode.dev.",
    tools=[ProvisionPostgresTool(), ProvisionWebhookTool(), ListResourcesTool()],
)

task = Task(
    description="Stand up a Postgres DB for the embeddings pipeline and report its DSN.",
    agent=provisioner,
)

Crew(agents=[provisioner], tasks=[task]).kickoff()
```

## Tool catalog

- `ProvisionPostgresTool` — `postgres://` DSN, pgvector pre-installed.
- `ProvisionWebhookTool` — HTTPS receiver URL (stores recent request bodies).
- `ListResourcesTool` — enumerate resources owned by the current API key.

MongoDB, Redis/cache, NATS queue, and heartbeat-monitor tools are on the
roadmap, gated on the matching backend endpoints landing. They live on
the `feature/full-api` branch.

### Paid-tier credentials

Set `INSTANODE_API_KEY` in your environment, or pass explicitly:

```python
ProvisionPostgresTool(api_key="sk_...")
```

## Tier model

| Tier | Postgres | Webhooks | Persistence |
|---|---|---|---|
| Anonymous (no key) | 10 MB / 2 connections | 100 stored | 24 hours |
| Paid | 500 MB / 5 connections | 1000 stored | Permanent |

## Related

- Python SDK: <https://pypi.org/project/instanode/>
- LangChain variant: <https://pypi.org/project/langchain-instanode/>
- LlamaIndex variant: <https://pypi.org/project/llama-index-tools-instanode/>
- MCP server (Claude Code / Cursor): <https://www.npmjs.com/package/@instanode/mcp>
- HTTP API: <https://instanode.dev/llms.txt>

## License

MIT.
