"""
Real Latency & Detailed Execution Trace Benchmarking Suite for My Agents.
Measures Cold vs Warm latency, per-request step breakdowns, tool counts, and TTFT.
"""

import os
import sys
import time
import uuid
from pathlib import Path

# Fix Windows console encoding for Unicode/Emojis
sys.stdout.reconfigure(encoding='utf-8')

# Add source directory
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "agents" / "01_product_query_agent" / "src"))
sys.path.insert(0, str(root_dir / "shared"))

from agentic_ai.core import HighLevelAgent
from agentic_ai.connectors import DatabaseConnector, VectorRAGConnector, RESTAPIConnector, PDFConnector, ChromaMemoryConnector
from agentic_ai.plugins import PluginRegistry, CatalogPlugin, RAGSupportPlugin, FinancePlugin, InvoicePlugin, MemoryPlugin

def run_performance_benchmarks():
    print("=" * 70, flush=True)
    print("🚀 RUNNING PHASE 3 EXECUTION TRACE & LATENCY BENCHMARKS", flush=True)
    print("=" * 70, flush=True)

    # 1. Cold Start Initialization Benchmark
    t_init_start = time.perf_counter()
    db = DatabaseConnector()
    rag = VectorRAGConnector()
    api = RESTAPIConnector()
    pdf = PDFConnector()
    chroma = ChromaMemoryConnector()
    for c in [db, rag, api, pdf, chroma]:
        c.connect()
    t_connectors = round((time.perf_counter() - t_init_start) * 1000, 1)
    print(f"📦 Connectors Initialized & Cached: {t_connectors}ms", flush=True)

    t_agent_start = time.perf_counter()
    registry = PluginRegistry()
    registry.register(CatalogPlugin(db_connector=db, enabled=True))
    registry.register(RAGSupportPlugin(vector_connector=rag, enabled=True))
    registry.register(FinancePlugin(api_connector=api, enabled=True))
    registry.register(InvoicePlugin(pdf_connector=pdf, db_connector=db, enabled=True))
    registry.register(MemoryPlugin(chroma_connector=chroma, enabled=True))
    agent = HighLevelAgent(registry=registry, chroma_conn=chroma)
    t_graph_compile = round((time.perf_counter() - t_agent_start) * 1000, 1)
    print(f"⚡ LangGraph Compiled & Cached: {t_graph_compile}ms", flush=True)

    test_queries = [
        ("A. Conversational", "Hello! What can you help me with?"),
        ("B. Memory Recall", "Remember that I own an Apple MacBook Air M3 and need a 4K monitor under $600 with 90W USB-C."),
        ("C. Product Search", "What 4K monitors do you have in stock under $600 with 90W USB-C charging?"),
        ("D. Grounded Verification", "Verify the exact charging wattage and warranty of the Dell UltraSharp 27 4K monitor."),
        ("E. RAG Manual Query", "How do I configure dual external monitors on MacBook Air M3 according to the official manual?"),
        ("F. Finance Query", "Convert $399.99 for Sony WH-1000XM5 headphones into EUR, GBP, and INR with 8.5% sales tax."),
        ("G. Invoice Generation", "Generate an official order invoice PDF for customer alex_smith purchasing 1 Dell UltraSharp 27 with code TECHSAVINGS10."),
    ]

    results = []

    for name, query in test_queries:
        print(f"\n--- Testing: {name} ---", flush=True)
        print(f"  Prompt: \"{query}\"", flush=True)
        
        # Cold execution (isolated thread)
        cold_thread = f"bench_cold_{uuid.uuid4().hex[:8]}"
        t0 = time.perf_counter()
        res_cold = agent.invoke_with_trace(query, user_id="alex_smith", thread_id=cold_thread)
        cold_lat = round(time.perf_counter() - t0, 3)

        time.sleep(1.2)  # Gentle spacing

        # Warm execution (warm thread)
        warm_thread = f"bench_warm_{uuid.uuid4().hex[:8]}"
        t1 = time.perf_counter()
        res_warm = agent.invoke_with_trace(query, user_id="alex_smith", thread_id=warm_thread)
        warm_lat = round(time.perf_counter() - t1, 3)

        speedup_pct = round(((cold_lat - warm_lat) / cold_lat) * 100, 1) if cold_lat > 0 else 0.0
        tools_used = res_warm.get("tool_calls", [])

        results.append({
            "name": name,
            "cold_sec": cold_lat,
            "warm_sec": warm_lat,
            "speedup_pct": speedup_pct,
            "tools_count": len(tools_used),
            "tools": tools_used,
            "telemetry": res_warm.get("telemetry", {}),
        })

        print(f"  ⏱️ Cold: {cold_lat}s | Warm: {warm_lat}s | Speedup: {speedup_pct}% | Tools ({len(tools_used)}): {tools_used}", flush=True)
        time.sleep(1.2)

    print("\n" + "=" * 70, flush=True)
    print("📊 PHASE 3 BENCHMARK & LATENCY AUDIT REPORT", flush=True)
    print("=" * 70, flush=True)
    print(f"{'Workflow':<25} | {'Cold (s)':<9} | {'Warm (s)':<9} | {'Speedup':<9} | {'Tools'}", flush=True)
    print("-" * 70, flush=True)
    for r in results:
        print(f"{r['name']:<25} | {r['cold_sec']:<9.3f} | {r['warm_sec']:<9.3f} | {r['speedup_pct']:>6.1f}%   | {r['tools_count']:<2} ({', '.join(r['tools']) if r['tools'] else 'None'})", flush=True)

    return results

if __name__ == "__main__":
    run_performance_benchmarks()
