import os
from src.prompt import QUESTION_PROMPT_TEMPLATE, REFINE_TEMPLATE

from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from transformers import pipeline

def single_file_processing(file_path):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    raw_data = loader.load()

    # Concatenate text from all pages
    source_str = ""
    for page in raw_data:
        source_str += page.page_content

    # Use an explicit encoding supported by tiktoken (e.g., "gpt2")
    question_splitter = TokenTextSplitter(
        encoding_name="gpt2",  # explicitly set to avoid tokeniser mapping issues
        chunk_size=512,
        chunk_overlap=50
    )
    chunks_str = question_splitter.split_text(source_str)
    question_chunks = [Document(page_content=t) for t in chunks_str]

    # Further split for answer retrieval
    answer_splitter = TokenTextSplitter(
        encoding_name="gpt2",
        chunk_size=512,
        chunk_overlap=50
    )
    answer_chunks = answer_splitter.split_documents(question_chunks)

    return question_chunks, answer_chunks

def llm_pipeline(file_path):
    # Process the file into document chunks
    document_question_chunks, document_answer_chunks = single_file_processing(file_path)

    # Initialize a Hugging Face text2text-generation pipeline with an open-source model
    hf_pipeline = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_length=512  # adjust this value based on your requirements and GPU memory
    )
    llm_model = HuggingFacePipeline(pipeline=hf_pipeline)

    # Create prompt templates using your external definitions
    QUESTION_PROMPT = PromptTemplate(
        template=QUESTION_PROMPT_TEMPLATE,
        input_variables=["text"]
    )
    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        template=REFINE_TEMPLATE,
        input_variables=["existing_answer", "text"]
    )

    # Build the question generation chain using the refine method
    question_generation_chain = load_summarize_chain(
        llm=llm_model,
        chain_type="refine",
        verbose=True,
        question_prompt=QUESTION_PROMPT,
        refine_prompt=REFINE_PROMPT_QUESTIONS
    )

    # Generate questions from the document chunks
    ques = question_generation_chain.run(document_question_chunks)

    # Use a HuggingFace embedding model (Sentence Transformers) for vectorization
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(document_answer_chunks, embeddings)

    # Process the generated output into a list of questions (filtering by a trailing '?')
    ques_list = [element for element in ques.split('\n') if element.strip().endswith('?')]

    # Set up a RetrievalQA chain to answer questions using the vector store
    answer_generator_chain = RetrievalQA.from_chain_type(
        llm=llm_model,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )

    return ques_list, answer_generator_chain

# Example usage:
if __name__ == "__main__":
    base_folder = 'static/docs/'
    pdf_filename = "1007132.pdf"  # replace with your PDF file name
    pdf_file_path = os.path.join(base_folder, pdf_filename)

    questions, qa_chain = llm_pipeline(pdf_file_path)

    print("Generated Questions:")
    for q in questions:
        print(q)

    # Retrieve an answer for the first question (if available)
    if questions:
        answer = qa_chain.run(questions[0])
        print("\nAnswer to first question:")
        print(answer)
