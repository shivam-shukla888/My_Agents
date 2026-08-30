"""
Inter-Agent Communication Bus & Task Message Broker.
Enables Agent 1, Agent 2, and Agent 3 to communicate, delegate sub-tasks, and share execution traces.
"""

from typing import Any, Callable, Dict, List, Optional
from datetime import datetime


class AgentCommunicationBus:
    """
    Central Pub/Sub and direct task delegation bus for the multi-agent network.
    """

    def __init__(self):
        self._registered_agents: Dict[str, Any] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def register_agent(self, agent_id: str, agent_instance: Any, description: str = "") -> None:
        """Register an agent on the communication bus."""
        self._registered_agents[agent_id] = {
            "instance": agent_instance,
            "description": description,
            "registered_at": datetime.now().isoformat(),
        }

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the bus."""
        self._registered_agents.pop(agent_id, None)

    def get_registered_agents(self) -> Dict[str, str]:
        """Return descriptions of all registered agents."""
        return {aid: data["description"] for aid, data in self._registered_agents.items()}

    def send_task(
        self,
        sender_agent: str,
        target_agent: str,
        task_instruction: str,
    ) -> Dict[str, Any]:
        """
        Send a sub-task from one agent to another synchronously and return the result.
        """
        timestamp = datetime.now().isoformat()
        
        if target_agent not in self._registered_agents:
            err_msg = f"Target agent '{target_agent}' is not registered on the communication bus."
            self._audit_log.append({
                "timestamp": timestamp,
                "sender": sender_agent,
                "recipient": target_agent,
                "status": "error",
                "task": task_instruction,
                "error": err_msg,
            })
            return {"status": "error", "message": err_msg}

        agent_obj = self._registered_agents[target_agent]["instance"]

        try:
            # Check if agent has an ask() or invoke() method
            if hasattr(agent_obj, "ask"):
                response_text = agent_obj.ask(task_instruction)
            elif hasattr(agent_obj, "invoke_with_trace"):
                res = agent_obj.invoke_with_trace(task_instruction)
                response_text = res.get("output", str(res))
            else:
                response_text = str(agent_obj(task_instruction))

            entry = {
                "timestamp": timestamp,
                "sender": sender_agent,
                "recipient": target_agent,
                "status": "success",
                "task": task_instruction,
                "response_preview": response_text[:200] + "...",
            }
            self._audit_log.append(entry)

            return {
                "status": "success",
                "sender": sender_agent,
                "recipient": target_agent,
                "response": response_text,
                "timestamp": timestamp,
            }

        except Exception as e:
            err_msg = f"Execution failed in target agent '{target_agent}': {str(e)}"
            self._audit_log.append({
                "timestamp": timestamp,
                "sender": sender_agent,
                "recipient": target_agent,
                "status": "error",
                "task": task_instruction,
                "error": err_msg,
            })
            return {"status": "error", "message": err_msg}

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Return full history of inter-agent messages and delegations."""
        return list(self._audit_log)
