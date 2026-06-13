from indexing.symbol_index import SymbolIndexer
from retrieval.retriever import CodeRetriever

indexer = SymbolIndexer()

symbols = indexer.build_symbol_index(".")

print("Bulunan sembol sayısı:", len(symbols))

retriever = CodeRetriever(symbols)

print(retriever.retrieve("Agent"))