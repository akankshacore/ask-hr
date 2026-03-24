# 1. Import OS, Document Loader, Text Splitter, Bedrock Embeddings, Vector DB, VectorStoreIndex, Bedrock-LLM

import os
from langchain_community.document_loaders import PyPDFLoader


# 2. Define the data source and load data with PDFLoader
data_load = PyPDFLoader(
    "https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf"
)

data_test = data_load.load_and_split()

print(len(data_test))
print(data_test[0])