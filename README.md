# crewai-instanode-tools

[CrewAI](https://crewai.com) tools for [instanode.dev](https://instanode.dev).
Let CrewAI agents provision ephemeral Postgres databases + webhook receivers
mid-task. No Docker, no account for the free tier.

```
pip install crewai-instanode-tools
```

## Usage

```python
from crewai import Agent, Task, Crew
from crewai_instanode_tools import (
    ProvisionPostgresTool,
    ProvisionWebhookTool,
)

db_provisioner = Agent(
    role="Infrastructure provisioner",
    goal="Give the team working database URLs with zero setup.",
    backstory="Spins up Postgres/webhooks via instanode.dev.",
    tools=[ProvisionPostgresTool(), ProvisionWebhookTool()],
)

task = Task(
    description="Stand up a Postgres DB for the embeddings pipeline and report its DSN.",
    agent=db_provisioner,
)

Crew(agents=[db_provisioner], tasks=[task]).kickoff()
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
