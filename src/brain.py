import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.schema import TextNode
from llama_index.core.llms import ChatMessage
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

INDEX_DIR = ".brain"

def configure_gemini():
    """
    Configures Settings with Gemini LLM and Embeddings if API key is present.
    Using latest llama-index-llms-google-genai.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and api_key != "mock_key":
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

def create_or_load_index(data_dir=".", force_refresh=False):
    """
    Creates a new index from the data directory or loads it from the storage if it exists.
    If force_refresh is True, it re-scans the directory and updates the index.
    """
    configure_gemini()

    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)

    index = None
    if force_refresh or not os.listdir(INDEX_DIR) or not os.path.exists(os.path.join(INDEX_DIR, "docstore.json")):
        try:
            # Excluir archivos grandes y binarios para evitar congelamiento
            reader = SimpleDirectoryReader(
                input_dir=data_dir,
                recursive=True,
                exclude_hidden=True,
                required_exts=[".py", ".js", ".ts", ".html", ".css", ".md", ".json", ".txt", ".yml", ".yaml", ".dockerfile", "Dockerfile"]
            )
            documents = reader.load_data()
            if not documents:
                documents = [TextNode(text="Initial project index for monorepo manager.").to_document()]

            if os.environ.get("GOOGLE_API_KEY") == "mock_key":
                 # Mock index for testing without real API
                 print("Mocking index creation for testing.")
                 with open(os.path.join(INDEX_DIR, "index_status.json"), "w") as f:
                    json.dump({"status": "indexed", "engine": "mock"}, f)
                 return None

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

def get_chat_engine(index, system_prompt=None, chat_history_dicts=None):
    """
    Returns a persistent Chat Engine with context from the index.
    Can restore chat history from a list of dictionary objects.
    """
    if not index:
        return None

    if not system_prompt:
        system_prompt = (
            "Eres un Ingeniero de Software Senior en un entorno de monorepo. "
            "HABLA SIEMPRE EN ESPAÑOL. Mantén el contexto de la conversación actual "
            "y utiliza el código del proyecto como referencia. Si te piden un cambio, "
            "analiza los archivos existentes antes de responder."
        )

    chat_history = []
    if chat_history_dicts:
        for msg in chat_history_dicts:
            chat_history.append(ChatMessage(role=msg["role"], content=msg["content"]))

    return index.as_chat_engine(
        chat_mode="context",
        system_prompt=system_prompt,
        chat_history=chat_history
    )

def query_index(index, query_text):
    """
    Legacy query function for non-chat interactions.
    """
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
