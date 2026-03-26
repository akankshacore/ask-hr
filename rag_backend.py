import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Any, List, Optional

from langchain.llms.base import LLM
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

AWS_PROFILE = "default"
AWS_REGION  = "ap-south-1"
EMBED_MODEL = "amazon.titan-embed-text-v2:0"

# ✅ Full ARN — required for newer Claude models in ap-south-1
LLM_ARN = "arn:aws:bedrock:ap-south-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"

PDF_URL = "https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf"


# ==============================
# CUSTOM BOTO3 LLM WRAPPER
# Bypasses all LangChain provider detection issues
# ==============================
class BedrockClaudeLLM(LLM):
    model_arn: str
    region: str
    profile: str
    max_tokens: int = 1000
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "bedrock-claude-custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        session = boto3.Session(profile_name=self.profile, region_name=self.region)
        client  = session.client("bedrock-runtime")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = client.invoke_model(
            modelId=self.model_arn,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]


# ==============================
# CHECK AWS
# ==============================
def check_aws_access():
    try:
        session  = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        identity = session.client("sts").get_caller_identity()
        return True, f"Connected as: {identity['Arn']}"
    except NoCredentialsError:
        return False, "AWS credentials not found. Run `aws configure`."
    except ClientError as e:
        return False, f"AWS error: {e.response['Error']['Message']}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


# ==============================
# VECTOR INDEX
# ==============================
def hr_index():
    documents = PyPDFLoader(PDF_URL).load_and_split(
        RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    )
    embeddings = BedrockEmbeddings(
        credentials_profile_name=AWS_PROFILE,
        region_name=AWS_REGION,
        model_id=EMBED_MODEL
    )
    return FAISS.from_documents(documents, embeddings)


# ==============================
# LLM
# ==============================
def hr_llm():
    return BedrockClaudeLLM(
        model_arn=LLM_ARN,
        region=AWS_REGION,
        profile=AWS_PROFILE,
        max_tokens=1000,
        temperature=0.7
    )


# ==============================
# RAG RESPONSE
# ==============================
def hr_rag_response(index, question):
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an HR assistant. Use ONLY the context below to answer.
If not found, say: "I couldn't find that in the HR policy document."

Context: {context}

Question: {question}

Answer:"""
    )
    chain = RetrievalQA.from_chain_type(
        llm=hr_llm(),
        retriever=index.as_retriever(search_kwargs={"k": 4}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )
    return chain.invoke({"query": question})["result"]