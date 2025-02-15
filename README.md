# Interview-Question-Creator-Gen-AI

Welcome to the Interview-Question-Creator-Gen-AI project! This project leverages the power of FastAPI and advanced language models to generate interview questions and answers from uploaded PDF documents.

## Design
![architecture-image](./figures/design.png)

## Table of Contents  
- [Introduction](#introduction)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Endpoints](#endpoints)  
- [Contributing](#contributing)  
- [License](#license)  

## Introduction  

The **Interview-Question-Creator-Gen-AI** project is designed to help users generate interview questions and answers from **PDF documents**. By uploading a PDF, the application processes the content and generates a **CSV file** containing relevant questions and answers.  

This tool can be particularly useful for **HR professionals, educators, and anyone preparing for interviews**.  

## Features  
- **📂 PDF Upload**: Easily upload PDF documents for analysis.  
- **🤖 Question Generation**: Automatically generate interview questions from the content of the PDF.  
- **📝 Answer Generation**: Provide answers to the generated questions using advanced language models.  
- **📊 CSV Export**: Export the generated questions and answers to a CSV file for easy access and sharing.  

## Prerequisites

- Python 3.10+
- pip

## Installation  

### Clone the repository:  
```bash
git clone https://github.com/sadhiin/interview-question-creator-gen-ai.git
cd interview-question-creator-gen-ai

### Create a virtual environment and activate it:  
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install the required dependencies:  
```bash
pip install -r requirements.txt
```

### Install the Petals library:  
```bash
pip install petals
```

## Usage  

Run the FastAPI application:  
```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

Open your browser and navigate to **[http://localhost:8080](http://localhost:8080)** to access the web application. And the SweigerUI at **[http://localhost:8080/docs](http://localhost:8080/docs)**

## Endpoints  

### `GET /`  
**Renders the index page.**  

### `POST /upload`  
**Uploads a PDF file.**  

#### **Request Parameters:**  
- `pdf_file (bytes)`: The PDF file to upload `file_name.pdf`.  
- `filename (str)`: The name of the file.  

#### **Response:**  
Returns a JSON object containing a success message and the path to the uploaded PDF file.  

### `POST /analyze`  
**Analyzes the uploaded PDF file and generates a CSV file with questions and answers.**  

#### **Request Parameters:**  
- `pdf_filename (str)`: The name of the uploaded PDF file.  

#### **Response:**  
Returns a JSON object containing the path to the generated CSV file.  

## Contributing  

1. **Fork** the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature-branch
   ```
3. Make your changes.  
4. Commit your changes:  
   ```bash
   git commit -m 'Add some feature'
   ```
5. Push to the branch:  
   ```bash
   git push origin feature-branch
   ```
6. Open a **pull request**.  

## License  

This project is licensed under the **MIT License**. See the `LICENSE` file for details.  

---

Thank you for checking out the **Interview-Question-Creator-Gen-AI** project! 🚀  
If you have any questions or feedback, feel free to reach out. **Happy coding!** 😊  
```