import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.schema import TextNode
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

INDEX_DIR = ".brain"

def configure_gemini():
    """
    Configures Settings with Gemini LLM and Embeddings if API key is present.
    Using latest llama-index-llms-google-genai.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            # Using models/gemini-2.5-flash as requested by user
            llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)
            # Using gemini-embedding-001 as text-embedding-004 is not available for this key/region
            embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=api_key)

            Settings.llm = llm
            Settings.embed_model = embed_model
            print("Gemini 2.5 Flash configured for RAG (Google GenAI).")
            return True
        except Exception as e:
            print(f"Error configuring Gemini: {e}")
    return False

def create_or_load_index(data_dir="."):
    """
    Creates a new index from the data directory or loads it from the storage if it exists.
    """
    configure_gemini()

    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)

    index = None
    if not os.listdir(INDEX_DIR) or not os.path.exists(os.path.join(INDEX_DIR, "docstore.json")):
        try:
            reader = SimpleDirectoryReader(
                input_dir=data_dir,
                recursive=True,
                exclude_hidden=True
            )
            documents = reader.load_data()
            if not documents:
                documents = [TextNode(text="Initial project index for monorepo manager.").to_document()]

            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=INDEX_DIR)
            print("Index created and persisted to .brain")

            with open(os.path.join(INDEX_DIR, "index_status.json"), "w") as f:
                json.dump({"status": "indexed", "engine": "gemini-2.5"}, f)

        except Exception as e:
            print(f"Failed to create index: {e}")
            if not os.path.exists(os.path.join(INDEX_DIR, "index_status.json")):
                with open(os.path.join(INDEX_DIR, "index_status.json"), "w") as f:
                    json.dump({"status": "placeholder"}, f)
    else:
        try:
            storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
            index = load_index_from_storage(storage_context)
            print("Index loaded from .brain")
        except Exception as e:
            print(f"Failed to load index: {e}")

    return index

def query_index(index, query_text):
    if not index:
        return "Index is not initialized. Please check your API keys and try again."
    try:
        query_engine = index.as_query_engine()
        response = query_engine.query(query_text)
        return str(response)
    except Exception as e:
        return f"Error querying index: {e}"

if __name__ == "__main__":
    create_or_load_index()
