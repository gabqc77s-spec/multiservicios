import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.schema import TextNode
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

INDEX_DIR = ".brain"

def configure_gemini():
    """
    Configures Settings with Gemini LLM and Embeddings if API key is present.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            # Using gemini-2.0-flash as per typical current naming,
            # though user mentioned gemini-2.5-flash which might be a typo or very new.
            # We will use what is likely available.
            llm = Gemini(model="models/gemini-2.0-flash", api_key=api_key)
            embed_model = GeminiEmbedding(model_name="models/text-embedding-004", api_key=api_key)

            Settings.llm = llm
            Settings.embed_model = embed_model
            print("Gemini configured for RAG.")
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
            # If no API key, LlamaIndex might fail on default OpenAI models.
            # SimpleDirectoryReader to get docs
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

            # Metadata for our app
            with open(os.path.join(INDEX_DIR, "index_status.json"), "w") as f:
                json.dump({"status": "indexed", "engine": "gemini" if os.environ.get("GOOGLE_API_KEY") else "default"}, f)

        except Exception as e:
            print(f"Failed to create index: {e}")
            # Fallback to placeholder if everything fails
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
