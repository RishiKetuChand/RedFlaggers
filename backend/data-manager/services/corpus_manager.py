from vertexai.preview import rag

STARTUP_TO_CORPUS_CACHE = {}

def create_or_get_corpus(startup_name):
  """Creates a new corpus or retrieves an existing one."""
  if startup_name in STARTUP_TO_CORPUS_CACHE:
    return STARTUP_TO_CORPUS_CACHE[startup_name]
  CORPUS_DISPLAY_NAME=startup_name
  embedding_model_config = rag.EmbeddingModelConfig(
      publisher_model="publishers/google/models/text-embedding-004"
  )
  existing_corpora = rag.list_corpora()
  corpus = None
  for existing_corpus in existing_corpora:
    if existing_corpus.display_name == CORPUS_DISPLAY_NAME:
      corpus = existing_corpus
      print(f"Found existing corpus with display name '{CORPUS_DISPLAY_NAME}'")
      break
  if corpus is None:
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=f"A corpus to store {CORPUS_DISPLAY_NAME} startup data",
        embedding_model_config=embedding_model_config,
    )
    print(f"Created new corpus with display name '{CORPUS_DISPLAY_NAME}'")
    STARTUP_TO_CORPUS_CACHE[startup_name] = corpus.name  # corpus.name is corpus_id
  return corpus.name

def upload_gcs_pdf_to_corpus(corpus_id, gcs_path, startup_name):
    #vertexai.init(project=PROJECT_ID, location=GOOGLE_CLOUD_LOCATION)
    
    """Uploads a PDF file from GCS into a Vertex AI RAG corpus with metadata."""
    #print(f"📤 Uploading {display_name} ({gcs_path}) to corpus {corpus_name}...")
    
    try:
        response = rag.import_files(
            corpus_name=corpus_id,
            paths=gcs_path,
        )
        print(f"✅ Successfully imported files {gcs_path} to corpus for the startup {startup_name}")
        return response
    except Exception as e:
        print(f"Error importing files {gcs_path}: {e}")
        return None