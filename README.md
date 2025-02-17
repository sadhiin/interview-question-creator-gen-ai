# Interview Question Creator (Gen AI)

An intelligent system that automatically generates comprehensive questions and answers from PDF documents using advanced language models and natural language processing.

## 🌟 Features

- **📚 Document Processing**
  - Support for PDF documents of any size
  - Intelligent text chunking and processing
  - Maintains context across document sections

- **🤖 AI-Powered Question Generation**
  - Generates diverse types of questions:
    - Conceptual understanding questions
    - Technical detail questions
    - Analytical questions
    - Application-based questions
  - Context-aware question generation
  - Page reference tracking

- **💡 Smart Answer Generation**
  - Context-aware answer generation
  - Accurate information retrieval
  - Source page references
  - Verification against source content

- **🎯 User Experience**
  - Clean and intuitive web interface
  - Real-time processing feedback
  - Easy document upload
  - CSV export functionality
  - Progress tracking

## 🚀 Technology Stack

- **Backend Framework**: FastAPI
- **AI/ML Components**:
  - LangChain for orchestration
  - HuggingFace models for text generation
  - FAISS for vector similarity search
  - Sentence Transformers for embeddings
- **Frontend**: HTML5, Bootstrap 5, jQuery
- **Document Processing**: PyPDF, TokenTextSplitter
- **Data Format**: CSV for output

## 📋 Prerequisites

- Python 3.11+
- 4GB+ RAM
- Storage space for model caching
- Internet connection for initial model download

## ⚙️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/interview-question-creator.git
   cd interview-question-creator
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv

   # On Windows
   .\venv\Scripts\activate

   # On Unix or MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuration

The system uses several key configurations:

1. **Model Settings**
   - Uses FLAN-T5-small for question generation
   - Sentence-transformers for embeddings
   - Configurable batch sizes and token limits

2. **Processing Parameters**
   - Chunk size: 200 tokens
   - Overlap: 20 tokens
   - Batch processing: 10 pages at a time
   - Maximum 15 questions per document

## 🚀 Usage

1. **Start the Server**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080 --reload
   ```

2. **Access the Application**
   - Web Interface: http://localhost:8080
   - API Documentation: http://localhost:8080/docs

3. **Using the Application**
   1. Upload your PDF document
   2. Wait for processing (time depends on document size)
   3. Review generated questions and answers
   4. Download the CSV output

## 📚 API Endpoints

### `GET /`
- Returns the main web interface
- No parameters required

### `POST /upload`
- Uploads a PDF document
- Parameters:
  - `file`: PDF file (multipart/form-data)
- Returns: Upload confirmation and file path

### `POST /analyze`
- Generates questions and answers from uploaded PDF
- Parameters:
  - `pdf_filename`: Name of the uploaded file
- Returns: Generated Q&A in CSV format

## 📊 Output Format

The generated CSV file contains:
- Questions with page references
- Corresponding answers
- Source page numbers
- Confidence scores (if applicable)

## 🛠️ Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Submit a pull request

## ⚠️ Known Limitations

- Processing very large PDFs (>1000 pages) may take significant time
- Quality of questions depends on document clarity
- Some technical documents may need multiple passes
- GPU acceleration recommended for large documents

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📧 Contact

For questions and feedback, please open an issue in the GitHub repository.

---

Made with ❤️ using Python and Opensource LLM models and tools 🫰🏼