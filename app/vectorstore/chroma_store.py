import chromadb

client = chromadb.PersistentClient(path="./data/chroma_db")

collection = client.get_or_create_collection(
    name="research_documents"
)


class ChromaStore:

    @staticmethod
    def add_chunks(
        document_id,
        file_name,
        chunks,
        embedding_model
    ):

        for index, chunk in enumerate(chunks):

            embedding = embedding_model.embed(
                chunk["text"]
            )

            collection.add(
                ids=[f"{document_id}_{index}"],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[
                    {
                        "document_id": document_id,
                        "file_name": file_name,
                        "page_number": chunk["page_number"]
                    }
                ]
            )

    @staticmethod
    def delete_document(document_id):

        results = collection.get(
            where={"document_id": document_id}
        )

        if results["ids"]:
            collection.delete(
                ids=results["ids"]
            )