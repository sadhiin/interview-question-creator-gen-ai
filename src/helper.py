import os
from dotenv import load_dotenv
from src.prompt import *

from langchain.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA


# API Authentication
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

def single_file_processing(file_path):
    # loader
    loader = PyPDFLoader(file_path)
    raw_data = loader.load()

    source_str = ""

    for page in raw_data:
        source_str += page.page_content

    question_splitter = TokenTextSplitter(
        model_name='gpt-3.5-turbo',
        chunk_size=10000,
        chunk_overlap=200
    )

    chunks_str = question_splitter.split_text(source_str)

    question_chunks = [Document(page_content=t) for t in chunks_str]

    answer_splitter = TokenTextSplitter(
        model_name='gpt-3.5-turbo',
        chunk_size=1000,
        chunk_overlap=100
    )

    answer_chunk= answer_splitter.split_documents(question_chunks)

    return question_chunks, answer_chunk



def llm_pipeline(file_path):
    document_question_chunks, document_answer_chunks = single_file_processing(file_path)

    llm_model= ChatOpenAI(
        model='gpt-3.5-turbo'
    )

    QUESTION_PROMPT = PromptTemplate(
        template=question_prompt_template,
        input_variables=['text'])

    # here existing_answer is the dictonary output from previous promput output.

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        template=refine_template,
        input_variables=['existing_answer', 'text']
    )

    question_generation_chain = load_summarize_chain(
        llm = llm_model,
        chain_type='refine',
        verbose=True,
        question_prompt= QUESTION_PROMPT,
        refine_prompt= REFINE_PROMPT_QUESTIONS
    )


    ques = question_generation_chain.run(document_question_chunks)

    embeddings = OpenAIEmbeddings()

    vector_store = FAISS.from_documents(document_answer_chunks, embeddings)

    ques_list = ques.split('\n')
    ques_list = [element for element in ques_list if element.endswith('?')]

    answer_generator_chain = RetrievalQA.from_chain_type(
        llm=llm_model,
        chain_type='stuff',
        retriever=vector_store.as_retriever()
    )

    return ques_list, answer_generator_chain