import json
import os
import time

import feedparser
from langchain import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore, create_kv_docstore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

def construct_all_documents(llm_chat, doc_max_size, debug_max_articles, documents_all_json_path):
    # Check if DOCUMENTS_ALL_JSON_PATH exists
    documents_all = []
    if os.path.exists(documents_all_json_path):
        print(f"Directly load documents_all for {documents_all_json_path}")
        # if yes, load the json file
        with open(documents_all_json_path, "r") as f:
            documents_all_serialized = json.load(f)
        for document_serialized in documents_all_serialized:
            doc = Document(metadata=document_serialized['metadata'], page_content=document_serialized['page_content'])
            documents_all.append(doc)
    else:
        print(f"Create new load documents_all for {documents_all_json_path}")
        feed_list = ['https://blog.google/technology/ai/rss/']
        feed_all = []
        for source in feed_list:
            feed = feedparser.parse(source)
            for item in feed.entries:
                # feed_all.append(f'{item.title}\n')
                feed_all.append(f'{item.link}')
        for idx, url in enumerate(feed_all):
            if 1 <= debug_max_articles <= idx:
                break
            loader = WebBaseLoader(
                web_paths=(url,)
            )
            cur_url_document_as_list_len_1 = loader.load()
            cur_url_num_tokens = llm_chat.get_num_tokens(cur_url_document_as_list_len_1[0].page_content)
            print(f"You have {cur_url_num_tokens} in current url.")
            if cur_url_num_tokens < doc_max_size:
                # list of one Document with metadata and page_content (str)
                documents_all.append(cur_url_document_as_list_len_1[0])
            else:
                print(f"Skipping url {url} because it has too many tokens.")

        # Step: store documents_all to disk
        documents_all_serialized = [{'metadata': doc.metadata, 'page_content': doc.page_content} for doc in
                                    documents_all]
        with open(documents_all_json_path, 'w') as f:
            json.dump(documents_all_serialized, f)
    return documents_all


def create_summaries(documents_all, llm_chat, documents_all_summary_list_json_path):
    final_url_to_doc_title_summary_url = {}
    # Check if DOCUMENTS_ALL_SUMMARY_LIST_JSON_PATH exists
    if os.path.exists(documents_all_summary_list_json_path):
        print(f"Directly load final_url_to_doc_title_summary_url for {documents_all_summary_list_json_path}")
        # if yes, load the json file
        with open(documents_all_summary_list_json_path, "r") as f:
            final_url_to_doc_title_summary_url = json.load(f)
    else:
        print(f"Create new final_url_to_doc_title_summary_url for {documents_all_summary_list_json_path}")
        summary_chain = load_summarize_chain(llm=llm_chat, chain_type="stuff",
                                             # verbose=True # Set verbose=True if you want to see the prompts being used
                                             )

        # Define prompt that generates titles for summarized text
        title_prompt_chat = ChatPromptTemplate.from_template(
            "Write an appropriate, clickbaity news article title in less than 70 characters for this text: {text}")
        title_chain_chat = LLMChain(llm=llm_chat, prompt=title_prompt_chat)

        len_documents_all = len(documents_all)
        print(f"Start generating summaries for {len_documents_all} articles")
        for i, parent_doc in enumerate(documents_all):
            # Generate the summary
            summarized_text = summary_chain.run([parent_doc])
            # Generate the title if title not existing in web loader's document metadata
            if 'title' in parent_doc.metadata:
                clickbait_title_chat = parent_doc.metadata['title']
            else:
                clickbait_title_chat = title_chain_chat.run(summarized_text)
            url = parent_doc.metadata['source']

            cur_doc_metadata_dict = {
                "title": clickbait_title_chat,
                "summary": summarized_text,
                "url": url
            }
            print(f"Done: {i + 1}/{len_documents_all}")
            final_url_to_doc_title_summary_url[url] = cur_doc_metadata_dict
            # Sleep for 1 second to avoid hitting the API rate limit
            time.sleep(21)

        # Step: store final_url_to_doc_title_summary_url to disk
        with open(documents_all_summary_list_json_path, 'w') as f:
            json.dump(final_url_to_doc_title_summary_url, f)
    return final_url_to_doc_title_summary_url


def build_retriever(doc_chunk_size_embedding_retrieval, doc_chunk_overlap, top_k_chunks, vectordb_path, docdb_path):
    # This text splitter is used to create the child documents for better embedding retrieval accuracy
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=doc_chunk_size_embedding_retrieval,
                                                    chunk_overlap=doc_chunk_overlap,
                                                    add_start_index=True)
    vectorstore = Chroma(
        collection_name="full_documents",
        embedding_function=AzureOpenAIEmbeddings(),
        persist_directory=vectordb_path
    )
    # The storage layer for the parent documents
    fs = LocalFileStore(docdb_path)
    store = create_kv_docstore(fs)
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        search_kwargs={"k": top_k_chunks}
        # k is the number of top sub chunks to retrieve (might have less than k as number of parent docs since chunks can come from same parent doc)
    )
    return retriever


def retrieve_relevant_documents_given_query(documents_all,
                                            retriever,
                                            user_query,
                                            vectordb_path,
                                            docdb_path):
    # Add documents and embed them if vector db does not exist or doc db does not exist
    # Otherwise, just load the retriever and proceed with similarity retrieval
    if not (os.path.exists(vectordb_path) and os.path.exists(docdb_path)):
        print(f"Did not find existing vector db or doc db. Proceeding with retriever.add_documents()")
        for doc in documents_all:
            retriever.add_documents([doc], ids=None)
            time.sleep(30)
    else:
        print(f"Found existing vector db and doc db. Skip retriever.add_documents()")
    debug_store_keys = list(retriever.docstore.yield_keys())
    print(f"You have {len(debug_store_keys)} docs in your retriever doc store")
    # retrieve from parent docs
    retrieved_relevant_parent_docs = retriever.get_relevant_documents(user_query)
    print(f"You have {len(retrieved_relevant_parent_docs)} articles retrieved given user query: {user_query}")
    return retrieved_relevant_parent_docs


def construct_email_body(final_url_to_doc_title_summary_url, retrieved_relevant_parent_docs):
    email_body = ""
    for idx, doc in enumerate(retrieved_relevant_parent_docs):
        doc_url = doc.metadata['source']
        doc_metadata_dict = final_url_to_doc_title_summary_url[doc_url]
        title = doc_metadata_dict['title']
        summarized_text = doc_metadata_dict['summary']
        url = doc_metadata_dict['url']
        email_body += f"❇️{title}\n\n"
        email_body += f"💬{summarized_text}\n\n"
        email_body += f"🔗{url}\n\n"
    return email_body
