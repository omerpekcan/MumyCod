from core.planner import Planner
from indexing.symbol_index import SymbolIndexer
from retrieval.retriever import CodeRetriever

planner = Planner()

plan = planner.plan(
    "Agent sınıfını düzenle"
)

print("PLAN:")
print(plan)

indexer = SymbolIndexer()
symbols = indexer.build_symbol_index(".")

retriever = CodeRetriever(symbols)

results = retriever.retrieve("Agent")

print("\nDOSYALAR:")
print(results)