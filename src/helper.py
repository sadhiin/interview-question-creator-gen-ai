import os
import atexit
import gc
from src.prompt import QUESTION_PROMPT_TEMPLATE

from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
# from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline

from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from transformers import pipeline
import torch

# Global variable to store the pipeline
_pipeline_instance = None

def cleanup_resources():
    """Cleanup function to be called at exit"""
    global _pipeline_instance
    if _pipeline_instance is not None:
        try:
            # Clear the pipeline
            _pipeline_instance.model = None
            _pipeline_instance.tokenizer = None
            _pipeline_instance = None

            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Force garbage collection
            gc.collect()

        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

# Register the cleanup function to be called at exit
atexit.register(cleanup_resources)

def get_pipeline():
    """Get or create the pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            max_length=150,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            num_return_sequences=1,
            device="cpu"
        )
    return _pipeline_instance

def single_file_processing(file_path):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    raw_data = loader.load()

    print(f"Processing PDF with {len(raw_data)} pages...")

    # Use smaller chunk sizes to avoid token length issues
    question_splitter = TokenTextSplitter(
        encoding_name="gpt2",
        chunk_size=200,
        chunk_overlap=20
    )

    # Process pages in batches to handle large PDFs
    question_chunks = []
    total_pages = len(raw_data)
    batch_size = 10  # Process 10 pages at a time

    for i in range(0, total_pages, batch_size):
        batch_pages = raw_data[i:min(i + batch_size, total_pages)]
        print(f"Processing pages {i+1} to {min(i + batch_size, total_pages)}...")

        for page in batch_pages:
            # Extract page number for context
            page_num = page.metadata.get('page', 0) + 1
            # Add page number to content for better context
            page_content = f"Page {page_num}: {page.page_content}"
            chunks = question_splitter.split_text(page_content)
            question_chunks.extend([Document(page_content=t, metadata={'page': page_num}) for t in chunks])

    # Create smaller chunks for answer retrieval
    answer_splitter = TokenTextSplitter(
        encoding_name="gpt2",
        chunk_size=200,
        chunk_overlap=20
    )
    answer_chunks = answer_splitter.split_documents(question_chunks)

    return question_chunks, answer_chunks

def llm_pipeline(file_path):
    try:
        # Process the file into document chunks
        document_question_chunks, document_answer_chunks = single_file_processing(file_path)

        # Get the pipeline instance
        hf_pipeline = get_pipeline()
        llm_model = HuggingFacePipeline(pipeline=hf_pipeline)

        # Create prompt templates using your external definitions
        QUESTION_PROMPT = PromptTemplate(
            template=QUESTION_PROMPT_TEMPLATE,
            input_variables=["text"]
        )

        # Process chunks in batches for question generation
        all_questions = []
        batch_size = 3  # Reduced batch size for better processing

        for i in range(0, len(document_question_chunks), batch_size):
            batch_chunks = document_question_chunks[i:i + batch_size]
            print(f"Generating questions for chunks {i+1} to {min(i + batch_size, len(document_question_chunks))}...")

            try:
                # Combine the batch chunks content with proper formatting
                combined_text = "\n".join([
                    f"Content from page {chunk.metadata.get('page', '?')}:\n{chunk.page_content}\n"
                    for chunk in batch_chunks
                ])

                # Generate questions directly using the LLM
                prompt = QUESTION_PROMPT.format(text=combined_text)
                response = llm_model.invoke(prompt)

                if isinstance(response, str):
                    raw_questions = response
                else:
                    raw_questions = response[0]['generated_text'] if response else ""

                print("Raw questions generated for batch:", raw_questions)

                # Process questions from this batch
                for q in raw_questions.split('\n'):
                    q = q.strip()
                    if q and q.endswith('?') and len(q) > 10:
                        # Add page context if available
                        page_nums = [str(chunk.metadata.get('page', '')) for chunk in batch_chunks]
                        page_context = f" (From page(s) {', '.join(set(page_nums))})"
                        all_questions.append(q + page_context)

            except Exception as e:
                print(f"Error processing batch {i}: {str(e)}")
                continue

        # If no questions generated, try fallback approach
        if not all_questions:
            print("No questions generated, trying fallback approach...")
            for chunk in document_question_chunks[:5]:  # Try first 5 chunks
                try:
                    prompt = f"Generate one specific question from this text: {chunk.page_content[:200]}"
                    response = llm_model.invoke(prompt)

                    if isinstance(response, str):
                        fallback_question = response
                    else:
                        fallback_question = response[0]['generated_text'] if response else ""

                    if fallback_question.strip().endswith('?'):
                        page_num = chunk.metadata.get('page', '')
                        all_questions.append(f"{fallback_question.strip()} (From page {page_num})")
                except Exception as e:
                    print(f"Error in fallback generation: {str(e)}")
                    continue

        # Ensure we have unique questions and limit the total number
        unique_questions = []
        seen = set()
        for q in all_questions:
            # Remove page numbers for comparison
            base_q = q.split(" (From page")[0]
            if base_q not in seen:
                seen.add(base_q)
                unique_questions.append(q)

        ques_list = unique_questions[:15]  # Keep top 15 questions
        print(f"Final filtered questions: {ques_list}")

        # Use a more reliable embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'}
        )
        vector_store = FAISS.from_documents(document_answer_chunks, embeddings)

        # Set up a RetrievalQA chain with more specific parameters
        answer_generator_chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_kwargs={"k": 2}  # Reduced to top 2 chunks to avoid token length issues
            ),
            return_source_documents=False,
            verbose=True
        )

        return ques_list, answer_generator_chain
    except Exception as e:
        print(f"Error in question generation: {str(e)}")
        cleanup_resources()  # Ensure cleanup on error
        raise

## Example usage:
if __name__ == "__main__":
    import os
    base_folder = 'static/docs/'
    ROOT = '/teamspace/studios/this_studio/interview-question-creator/'
    base_folder = os.path.join(ROOT, base_folder)
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
