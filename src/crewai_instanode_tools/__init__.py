"""
crewai-instanode-tools — CrewAI tools for instanode.dev.

Let CrewAI agents provision ephemeral Postgres databases + webhook
receivers by calling instanode.dev. No Docker, no account for free tier.

Quick start
-----------
    from crewai import Agent
    from crewai_instanode_tools import (
        ProvisionPostgresTool,
        ProvisionWebhookTool,
    )

    db_agent = Agent(
        role="Database provisioner",
        goal="Give teammates working Postgres URLs fast.",
        tools=[ProvisionPostgresTool(), ProvisionWebhookTool()],
    )

Authentication
--------------
Free tier works without credentials. For paid tier, set
INSTANODE_API_KEY in your environment.

Links
-----
- Homepage:   https://instanode.dev
- Python SDK: https://pypi.org/project/instanode/
"""

from crewai_instanode_tools.tools import (
    ProvisionPostgresTool,
    ProvisionWebhookTool,
    ProvisionMongoTool,
    ListResourcesTool,
)

__version__ = "0.1.0"
__all__ = [
    "ProvisionPostgresTool",
    "ProvisionWebhookTool",
    "ProvisionMongoTool",
    "ListResourcesTool",
]
