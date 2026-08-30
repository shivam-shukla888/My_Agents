"""
Product Query Agent built with LangChain (v1.3+), Groq (ChatGroq), and custom tools.
Assists users with product inquiries, comparisons, stock checks, and discount lookups.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

# Ensure package directory is in sys.path when running directly
current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from agentic_ai.tools import PRODUCT_TOOLS
from agentic_ai.products_data import PRODUCTS, DISCOUNTS

# Load environment variables from .env files
load_dotenv(current_file.parent / ".env")
load_dotenv(src_dir.parent / ".env")


SYSTEM_PROMPT = """You are an intelligent, helpful, and courteous Product Query and Shopping Assistant.
Your mission is to provide accurate, up-to-date, and detailed product recommendations, technical specifications, comparisons, stock availability, and discount savings to customers.

### YOUR CAPABILITIES & TOOLS:
1. **search_products**: Find products matching keywords, category filters, and budget limits.
2. **get_product_details**: Look up complete specifications, warranty, user rating, and overview for a specific product.
3. **compare_products**: Perform side-by-side technical, feature, and pricing comparisons between 2 or more products.
4. **check_inventory_and_delivery**: Check warehouse stock status, delivery days, and shipping costs.
5. **get_active_discounts**: Retrieve valid discount coupon codes and special promotional offers.

### GUIDELINES:
- **Be Factual & Grounded**: Always query your tools for specifications, pricing, stock levels, and discounts. Never invent or hallucinate product details.
- **Proactive Savings**: When discussing product prices, check if any active coupon codes or discounts can save the customer money!
- **Structured & Elegant Presentation**: Use markdown headers, bullet points, bold highlights, and comparison tables when presenting specs or options.
- **Friendly & Consultative**: If a customer's query is broad (e.g. "I want a laptop"), search and offer the best options tailored to different use cases (budget, performance, portability).
"""


def get_groq_llm(
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.2,
    api_key: Optional[str] = None,
) -> ChatGroq:
    """
    Initialize and return the ChatGroq model instance.
    """
    groq_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found! Please set it in your .env file or pass it to get_groq_llm()."
        )

    return ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=groq_api_key,
        max_retries=2,
    )


def create_product_agent(
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.2,
    api_key: Optional[str] = None,
    debug: bool = False,
):
    """
    Constructs and returns the Product Query Agent graph using LangChain's create_agent.

    Args:
        model_name: Groq model to use (default: 'llama-3.3-70b-versatile').
        temperature: Sampling temperature for the model.
        api_key: Optional Groq API Key override.
        debug: Whether to print internal graph execution logs.

    Returns:
        CompiledStateGraph agent instance.
    """
    llm = get_groq_llm(model_name=model_name, temperature=temperature, api_key=api_key)

    agent_graph = create_agent(
        model=llm,
        tools=PRODUCT_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        debug=debug,
    )

    return agent_graph


def run_product_query(
    agent_graph,
    user_query: str,
    chat_history: Optional[List[BaseMessage]] = None,
) -> Dict[str, Any]:
    """
    Execute a single user query against the agent with optional chat history.

    Args:
        agent_graph: The compiled agent graph from create_product_agent().
        user_query: Customer question or command.
        chat_history: List of preceding HumanMessage and AIMessage objects.

    Returns:
        Dict with 'output' (final assistant response text), 'messages' (full message trace),
        and 'tool_calls' (all tool invocations and results).
    """
    messages: List[Union[BaseMessage, Dict[str, str]]] = []

    if chat_history:
        messages.extend(chat_history)

    messages.append(HumanMessage(content=user_query))

    response_state = agent_graph.invoke({"messages": messages})
    all_messages = response_state.get("messages", [])

    # Extract final AIMessage content
    final_output = ""
    tool_calls_log = []

    for msg in reversed(all_messages):
        if isinstance(msg, AIMessage) and msg.content:
            final_output = msg.content
            break
        elif hasattr(msg, "role") and msg.role == "assistant" and getattr(msg, "content", None):
            final_output = msg.content
            break

    # Extract tool calls for transparency & inspection
    for msg in all_messages:
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                tool_calls_log.append({
                    "name": tc.get("name"),
                    "args": tc.get("args"),
                    "id": tc.get("id"),
                })

    return {
        "output": final_output,
        "messages": all_messages,
        "tool_calls": tool_calls_log,
    }


def interactive_cli():
    """
    Run an interactive command-line interface for the Product Query Agent.
    """
    print("=" * 70)
    print("🛒 Welcome to the Product Query AI Agent (powered by Groq & LangChain)")
    print("=" * 70)
    print("Example questions you can ask:")
    print(" • 'What laptops do you have under $1200, and are there discount coupons?'")
    print(" • 'Compare iPhone 16 Pro and Samsung Galaxy S25 Ultra specs and prices.'")
    print(" • 'Check stock and delivery estimate for Sony WH-1000XM5 to ZIP 90210.'")
    print(" • 'What are the specs for Dell UltraSharp 27 4K Monitor?'")
    print("\nType 'exit', 'quit', or 'q' to end.\n")

    try:
        agent = create_product_agent()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return

    chat_history: List[BaseMessage] = []

    while True:
        try:
            user_input = input("👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\n👋 Thank you for shopping with us! Have a great day!")
                break

            print("\n🤖 Agent is querying tools...")
            response = run_product_query(agent, user_input, chat_history)

            answer = response.get("output", "No response generated.")
            print(f"\n🛒 Assistant:\n{answer}\n")
            print("-" * 70)

            # Update chat history
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=answer))

        except KeyboardInterrupt:
            print("\n\n👋 Session ended. Goodbye!")
            break
        except Exception as err:
            print(f"\n❌ An error occurred: {err}")


if __name__ == "__main__":
    interactive_cli()
