"""
Shared Inter-Agent Communication, Security, and Network Orchestration Layer.
"""

from shared.security import SecureWorkspaceVault
from shared.bus import AgentCommunicationBus
from shared.delegation_tools import create_agent_delegation_tools

def __getattr__(name: str):
    if name == "MultiAgentNetwork":
        from shared.orchestrator import MultiAgentNetwork
        return MultiAgentNetwork
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "SecureWorkspaceVault",
    "AgentCommunicationBus",
    "create_agent_delegation_tools",
    "MultiAgentNetwork",
]

