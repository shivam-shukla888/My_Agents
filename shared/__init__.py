"""
Shared Inter-Agent Communication, Security, and Network Orchestration Layer.
"""

from shared.security import SecureWorkspaceVault
from shared.bus import AgentCommunicationBus
from shared.delegation_tools import create_agent_delegation_tools
from shared.orchestrator import MultiAgentNetwork

__all__ = [
    "SecureWorkspaceVault",
    "AgentCommunicationBus",
    "create_agent_delegation_tools",
    "MultiAgentNetwork",
]
