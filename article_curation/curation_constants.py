import os

USER_QUERY = "conversation on ai with artist"
DOC_CHUNK_SIZE_EMBEDDING_RETRIEVAL = 1000  # default chunk size 1000 when split text for embedding retrieval
DOC_CHUNK_OVERLAP = 200  # default overlap 200 when split text for embedding retrieval
DOC_MAX_SIZE = 4097 - 256  # based on text-davinci-003 and 256 tokens for completion, summary chain with "stuff" type can only take those short texts without map_reduce RPM limitaiton
TOP_K_CHUNKS = 20  #DOC_CHUNK_SIZE_EMBEDDING_RETRIEVAL and DOC_MAX_SIZE play a role to determine what is the final number of retrieved documents
DEBUG_MAX_ARTICLES = 2  # for debugging, only process the first 5 articles; if 0 or -1 no debug limitation
CURATE_OUTPUT_FOLDER = "./curate_output_folder"
DOCUMENTS_ALL_JSON_PATH = os.path.join(CURATE_OUTPUT_FOLDER, "documents_all.json")
DOCUMENTS_ALL_SUMMARY_LIST_JSON_PATH = os.path.join(CURATE_OUTPUT_FOLDER,
                                                    "documents_all_summary_list.json")
VECTORDB_PATH = os.path.join(CURATE_OUTPUT_FOLDER, "chroma_db")
DOCDB_PATH = os.path.join(CURATE_OUTPUT_FOLDER, "chroma_db_filestore")
GPT_3_5_TURBO = "gpt-3.5-turbo"
GPT_3_5_TURBO_16K = "gtp-35-turbo-16k-0613"
AZURE_GPT_3_5_TURBO = "gpt-35-turbo"
AZURE_GPT_3_5_TURBO_16K = "gpt-35-turbo-16k-0613"
AZURE_TEXT_EMB = "text-embedding-ada-002"

# DB Queries
GET_USER_QUERY = "SELECT q.query, u.destination FROM queries q JOIN users u ON u.id = q.user_id"
