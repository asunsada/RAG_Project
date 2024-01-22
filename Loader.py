# THis code loads pdfs and docs for an entire directory and loads into langchain, chunks, 
# deletes the chromadb and inserts into chrmadb the chunks.
#from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
#from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_community.vectorstores import Chroma
#import chromadb
#from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
import os
import shutil
import requests
import fitz
import openai

#pip install PyMuPDF python-docx
from docx import Document  # python-docx

print(f"Starting program...")
print(f"Libraries imported.")      

URL_FILE_PATH="data/urls/URLs.txt" #External File where all the URLs (domina data) reside
DATA_PATH = "data/DomainData/" #dired=ctory where Langchain stores the PDFs in the file above
CHROMA_PATH = "chroma"

#Additon 2
# Initialize an empty array to store the lines of text. Reads PDF links from a text file "URLs.txt"
pdf_urls1  = []

# Read text from the file where all the URLs (domain data) and store it in the array.
# When I find interesting docs I want the LLM to learn from, I just add them to a text file I have in my laptop
# so I don't have to modify the code.
try:
    with open(URL_FILE_PATH, 'r') as file:
        # Read each line in the file
        for line in file:
            # Append the line to the array
            pdf_urls1.append(line.strip())  # Remove leading and trailing whitespaces
except FileNotFoundError:
    print(f"File '{URL_FILE_PATH}' not found.")

# Print the contents of the array
print("pdf_urls1 :")
print(pdf_urls1 )


print(f"URLs provided and ready to start loading the PDFs from the web in my local directory, DATA_PATH")
# Loop through each PDF URL
for pdf_url in pdf_urls1:
    # Extract the filename from the URL to use as the local path
    local_pdf_path = 'data/DomainData/' + pdf_url.split('/')[-1]

    # Download the PDF
    response = requests.get(pdf_url)

    # Save the PDF locally
    with open(local_pdf_path, 'wb') as pdf_file:
        pdf_file.write(response.content)


text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )

print(f"Locating the domain data loaded by 'domain user' in the directory provided in path:",DATA_PATH )

for filename in os.listdir(DATA_PATH):
        print(f"# of documents in the directory:{len(os.listdir(DATA_PATH))}")    
        file_path = os.path.join(DATA_PATH, filename)
        file_path.replace('\\', '/')
        if filename.endswith(".pdf"):
            print(f"file_path of .pdf file is:",file_path)
            #fitz.open is used to open a PDF document specified by the file_path. The returned object is a fitz.Document object, representing the opened PDF document.
            pdf_document = fitz.open(file_path)
            print(f"# of pages of .pdf is: {len(pdf_document)}")
            # Process PDF document as needed
            # Perform operations on the PDF document, e.g., extracting text for each page
            for page_number in range(pdf_document.page_count):
               page = pdf_document[page_number]
               text = page.get_text()
               print(f"Page {page_number + 1} text:\n{text}\n")
            # Close the PDF document
            pdf_document.close()


        #for doc files
        elif filename.endswith((".docx", ".doc")):
            #Open the doc file
            doc_document = Document(file_path)
            print(f"file_path of .doc / .docx file is:",file_path)
            #print(f"# of pages of .doc is:{page_number + 1}")
            
            # Perform operations on the document, e.g., extracting text
                        #print(f"# of content of .doc is:", content)
                      
              
# Open and load the PDF using PyPDFLoader   
loader = DirectoryLoader(DATA_PATH) 
docs=loader.load()
print({len(docs)})


##### SPLITTING INTO CHUNKS ######
print(f"Starting to split into chunks the domain data docs...")
chunks = text_splitter.split_documents(docs)
print(f"Split {len(docs)} documents (not really # of pages) into {len(chunks)} chunks.") 
document = chunks[1]
print(f"Printing content of chunk 1")
print(document.page_content)
# metadata
print(f"Printing metadata ")
print(document.metadata)


# STORING #######     CHROMA DB Create a new DB from the documents.
print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
openai.api_key = os.getenv('OPENAI_API_KEY')
print(openai.api_key)


# Delete the data in the ChromaDB.  Create a new DB from the documents.
# Replace 'Chromadb.db' with the actual name of your database
database_name = 'Chromadb.db'

# Check if the database file exists before attempting to delete it
if os.path.exists(database_name):
    os.remove(database_name)
    print(f"The '{database_name}' database has been deleted.")
else:
    print(f"The '{database_name}' database does not exist, so we create it.")

# load it into Chroma the embeddings. PLease note you need to have your OPEN AI KEY SET UP as an env variable.
db = Chroma.from_documents(chunks, OpenAIEmbeddings(openai_api_type=openai.api_key), persist_directory=CHROMA_PATH)
db.persist()
print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

# The embeddings
embeddings = OpenAIEmbeddings(openai_api_key = openai.api_key)
embeddings_result = embeddings.embed_documents(text)
print("Total Embeddings:", len(embeddings_result))

