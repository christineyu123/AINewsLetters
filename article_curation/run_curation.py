'''
Suggested steps:
- Make sure you have a .env file with the correct AZURE OpenAI API key and configs (refer to .env.local as example)
- Step to and use raccoons-innov-2023-ai-trends/article_curation as working directory
- cmd to be launched at the working directory: python run_curation.py
- The next time, you can just run the cmd again to reuse the cached results in `curate_output_folder` or delete
    the cached results and run the cmd again to regenerate the results
'''
import json
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain_core.documents import Document

# Step: Load environment variables from .env file
# Access the API key using the variable name defined in the .env file
from article_curation.curation_constants import *
from article_curation.curation_utils import create_summaries, build_retriever, \
    retrieve_relevant_documents_given_query, construct_email_body
from news_feed.application.ai_feed import main as rss_feed

# load OpenAI API keys from .env file
load_dotenv()

# create curate_output_folder if not exists
Path(CURATE_OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

# Create Global value for DB Connection
CONNECTION = sqlite3.Connection(f'{Path(__file__).parent.parent}/ai_trends.db')


def get_user_query_results():
    cursor = CONNECTION.cursor()
    cursor.execute(GET_USER_QUERY)
    return cursor.fetchall()


def main():
    # Step: Get some llms models
    llm_chat = AzureChatOpenAI(
        model_name=AZURE_GPT_3_5_TURBO,
        temperature=0.0

    )
    # Step: Append each entry/article from rss to feed_all
    if os.path.exists(DOCUMENTS_ALL_JSON_PATH):
        documents_all = []
        print(f"Directly load documents_all for {DOCUMENTS_ALL_JSON_PATH}")
        # if yes, load the json file
        with open(DOCUMENTS_ALL_JSON_PATH, "r") as f:
            documents_all_serialized = json.load(f)
        for document_serialized in documents_all_serialized:
            doc = Document(metadata=document_serialized['metadata'], page_content=document_serialized['page_content'])
            documents_all.append(doc)
    else:
        print(f"Create new load documents_all for {DOCUMENTS_ALL_JSON_PATH}")
        documents_all = rss_feed()
        documents_all_serialized = [{'metadata': doc.metadata, 'page_content': doc.page_content} for doc in
                                    documents_all]
        with open(DOCUMENTS_ALL_JSON_PATH, 'w') as f:
            json.dump(documents_all_serialized, f)

    print(f"You have {len(documents_all)} articles in total loaded from the RSS feeds.")

    # Step: do summarization for all documents
    final_url_to_doc_title_summary_url = create_summaries(documents_all=documents_all,
                                                          llm_chat=llm_chat,
                                                          documents_all_summary_list_json_path=DOCUMENTS_ALL_SUMMARY_LIST_JSON_PATH)

    # Step: retrieve relevant parent documents
    retriever = build_retriever(doc_chunk_size_embedding_retrieval=DOC_CHUNK_SIZE_EMBEDDING_RETRIEVAL,
                                doc_chunk_overlap=DOC_CHUNK_OVERLAP,
                                top_k_chunks=TOP_K_CHUNKS,
                                vectordb_path=VECTORDB_PATH,
                                docdb_path=DOCDB_PATH)

    for user_query, destination in get_user_query_results():
        # user_query is the parameter used to retrieve relevant documents with
        # destination is the parameter used to determine the destination to which the content must be delivered.
        retrieved_relevant_parent_docs = retrieve_relevant_documents_given_query(documents_all=documents_all,
                                                                                 retriever=retriever,
                                                                                 user_query=user_query,
                                                                                 vectordb_path=VECTORDB_PATH,
                                                                                 docdb_path=DOCDB_PATH
                                                                                 )

        # Step: compose email body with retrieved_parent_docs
        # use destination to determine where to send the curated content.
        email_body = construct_email_body(final_url_to_doc_title_summary_url=final_url_to_doc_title_summary_url,
                                          retrieved_relevant_parent_docs=retrieved_relevant_parent_docs)
        print(
            f"\n\n ############################## Newsletter fOR USER QUERY: '{user_query}' #################################")
        print(email_body)

    print("All done!")


# create main entry point
if __name__ == "__main__":
    main()
    CONNECTION.close()
