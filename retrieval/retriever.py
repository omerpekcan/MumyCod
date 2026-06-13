from indexing.symbol_index import SymbolIndexer


class CodeRetriever:

    def __init__(self, symbol_index: dict):
        self.symbol_index = symbol_index

    def retrieve(self, query: str) -> list[str]:

        query = query.lower()

        results = []

        for symbol, path in self.symbol_index.items():

            if query in symbol.lower():
                results.append(path)

        return list(set(results))