from abc import abstractmethod


class BaseRetriever:
    """BEIR-compatible retriever interface. All retrievers return {query_id: {doc_id: score}}."""

    @abstractmethod
    def search(self, corpus: dict, queries: dict, top_k: int) -> dict[str, dict[str, float]]:
        raise NotImplementedError

    def name(self) -> str:
        return self.__class__.__name__
