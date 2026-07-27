from app.vectorstore.search import SemanticSearch
from app.llm.ollama_client import OllamaClient
from app.memory.memory_service import ConversationMemory


class RAGService:

    @staticmethod
    def answer(question: str, session_id: str = "default"):

        previous = ConversationMemory.get(session_id)

        if previous:
            question = f"""
Previous Question:
{previous['question']}

Previous Answer:
{previous['answer']}

Follow-up Question:
{question}
"""

        results = SemanticSearch.search(question)

        documents = results["documents"][0]
        metadata = results["metadatas"][0]

        context = ""
        sources = []

        for doc, meta in zip(documents, metadata):

            context += f"""

Document: {meta['file_name']}
Page: {meta['page_number']}

Content:
{doc}

"""

            sources.append(
                {
                    "document": meta["file_name"],
                    "page": meta["page_number"]
                }
            )

        prompt = f"""
You are an AI Research Assistant.

Answer ONLY from the supplied context.

Context:

{context}

Question:

{question}
"""

        answer = OllamaClient.generate(prompt)

        ConversationMemory.save(
            session_id,
            question,
            answer
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }