import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 2. Define the data source and load data with PDFLoader
data_load = PyPDFLoader(
    "https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf"
)

# 3. Split the Text based on Character, Tokens etc.
data_split = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=100,
    chunk_overlap=10
)

# Sample text
data_sample = "Welcome to the most comprehensive AWS Cloud Development Kit (CDK) - V2 on Udemy from an instructor"

# Split the sample text
data_split_test = data_split.split_text(data_sample)

# Print result
print(data_split_test)