import argparse
from dataclasses import dataclass
from langchain.vectorstores.chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
#from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
#from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import shutil
import requests
import fitz
import openai

CHROMA_PATH = "chroma"
DATA_PATH = "data/DomainData"

PROMPT_TEMPLATE = """
Based on the following context:

{context}

---

Answer the question and provide the answer in 4 bullet points: {question}
"""


def main():
    # Create CLI. Create a parser for the user query text so we can enter it
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    #Asun
    openai.api_key = os.getenv('OPENAI_API_KEY')
    print(openai.api_key)
    #Asun
    embedding_function = OpenAIEmbeddings(openai_api_type=openai.api_key)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB. k=5 to show 5 results in a tuple, the text and the relevance score
    results = db.similarity_search_with_relevance_scores(query_text, k=5)
 # Check if results are empty
    if not results:
        print("No results found in DB.")
    else:   
        #Asun print results of similarity function
        for rank, (document, relevance_score) in enumerate(results, start=1):
            print(f"Rank {rank}:")
            print(f"Relevance Score: {relevance_score}")
            print(f"Document Content:\n{document.page_content}\n---\n")


    # if there are no results or relevance score of the 1st result is below 0.7, then return early
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results. Relevance score must be >=0.7 to be considered")
        context_text=None
    else:  
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    # Iterate through the results and print the context_text and score
         
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
     # Print content for each page
    print(f"This is the RAG prompt:",prompt)

    model = ChatOpenAI()
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()
