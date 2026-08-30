"""
Real Latency & Performance Benchmarking Suite for My Agents.
Measures Cold vs Warm latency, TTFT, and component breakdowns.
"""

import os
import sys
import time
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
    print("=" * 65, flush=True)
    print("🚀 RUNNING PRODUCTION LATENCY BENCHMARKS (REAL TIMINGS)", flush=True)
    print("=" * 65, flush=True)

    # 1. Cold Start Benchmark
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
        ("B. Memory Recall", "Remember that I own an Apple MacBook Air M3 and strictly need a 4K monitor under $600 with 90W USB-C charging."),
        ("C. Product Search", "What 4K monitors do you have in stock under $600 with 90W USB-C charging?"),
        ("D. Grounded Verification", "Verify the exact charging wattage, contrast ratio, and warranty of the Dell UltraSharp 27 4K monitor using verified ground-truth."),
        ("E. RAG Manual Query", "How do I configure dual external monitors on MacBook Air M3 according to the official manual?"),
        ("F. Finance Query", "Convert the price of Sony WH-1000XM5 headphones into EUR, GBP, and INR with 8.5% sales tax."),
        ("G. Invoice Generation", "Generate an official order invoice PDF for customer alex_smith purchasing 1 Dell UltraSharp 27 with code TECHSAVINGS10."),
    ]

    results = []

    for name, query in test_queries:
        print(f"\n--- Testing: {name} ---", flush=True)
        
        # Cold execution
        t0 = time.perf_counter()
        res_cold = agent.invoke_with_trace(query, user_id="alex_smith", thread_id=f"bench_session_{name}")
        cold_lat = round(time.perf_counter() - t0, 3)

        time.sleep(1.0)  # Gentle 1s spacing between test executions

        # Warm execution (same query)
        t1 = time.perf_counter()
        res_warm = agent.invoke_with_trace(query, user_id="alex_smith", thread_id=f"bench_session_{name}")
        warm_lat = round(time.perf_counter() - t1, 3)

        improvement_pct = round(((cold_lat - warm_lat) / cold_lat) * 100, 1) if cold_lat > 0 else 0.0

        results.append({
            "name": name,
            "cold_sec": cold_lat,
            "warm_sec": warm_lat,
            "improvement_pct": improvement_pct,
            "tools_triggered": len(res_warm.get("tool_calls", [])),
            "telemetry": res_warm.get("telemetry", {}),
        })

        print(f"  Cold: {cold_lat}s | Warm: {warm_lat}s | Speedup: {improvement_pct}% | Tools: {len(res_warm.get('tool_calls', []))}", flush=True)
        time.sleep(1.0)

    print("\n" + "=" * 65, flush=True)
    print("📊 BENCHMARK SUMMARY TABLE", flush=True)
    print("=" * 65, flush=True)
    print(f"{'Workflow':<25} | {'Cold (s)':<9} | {'Warm (s)':<9} | {'Speedup':<9} | {'Tools':<6}", flush=True)
    print("-" * 65, flush=True)
    for r in results:
        print(f"{r['name']:<25} | {r['cold_sec']:<9.3f} | {r['warm_sec']:<9.3f} | {r['improvement_pct']:>6.1f}%   | {r['tools_triggered']:<6}", flush=True)

    return results

if __name__ == "__main__":
    run_performance_benchmarks()
