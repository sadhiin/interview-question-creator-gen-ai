import os
import json
import csv
import aiofiles
import uvicorn
from fastapi import FastAPI, Form, Request, Response, File, Depends, HTTPException, status, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from src.helper import llm_pipeline

app = FastAPI()
ROOT = '/teamspace/studios/this_studio/interview-question-creator/'
app.mount(os.path.join(ROOT,'/static'), StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UploadPDF(BaseModel):
    filename: str

class AnalyzePDF(BaseModel):
    pdf_filename: str

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})

@app.post('/upload')
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        base_folder = 'static/docs/'
        base_folder = os.path.join(ROOT, base_folder)

        if not os.path.isdir(base_folder):
            os.makedirs(base_folder)

        filename = file.filename
        if filename is None:
            raise HTTPException(status_code=400, detail="Filename is required")

        pdf_filename = os.path.join(base_folder, filename)

        async with aiofiles.open(pdf_filename, 'wb') as f:
            content = await file.read()
            await f.write(content)

        response_data = jsonable_encoder({
            'msg': 'success',
            'pdf_filename': f'/static/docs/{filename}'
        })

        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def get_csv(file_path):
    try:
        question_list, answer_generator_chain = llm_pipeline(file_path)

        base_folder = 'static/output'
        base_folder = os.path.join(ROOT, base_folder)
        if not os.path.isdir(base_folder):
            os.makedirs(base_folder)
        csv_file = datetime.now().strftime('%Y%m%d_%H_%M_%S') + ".csv"
        output_file = os.path.join(base_folder, csv_file)
        qa_pairs = []

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Question', 'Answer'])

            for question in question_list:
                try:
                    answer = answer_generator_chain.run(question)
                    print(f'Q: {question}\nA: {answer}\n{"-"*50}\n')
                    csv_writer.writerow([question, answer])
                    qa_pairs.append({'question': question, 'answer': answer})
                except Exception as e:
                    print(f"Error processing question: {question}\nError: {str(e)}")
                    continue

        return csv_file, qa_pairs
    except Exception as e:
        print(f"Error in get_csv: {str(e)}")
        raise

@app.post('/analyze')
async def chat(request: Request, pdf_filename: str = Form(...)):
    try:
        base_folder = 'static/docs/'
        base_folder = os.path.join(ROOT, base_folder)
        pdf_file_path = os.path.join(base_folder, pdf_filename)

        if not os.path.isfile(pdf_file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")

        output_filename, qa_pairs = get_csv(pdf_file_path)

        if not qa_pairs:
            raise HTTPException(status_code=400, detail="No questions and answers were generated")

        response_data = jsonable_encoder({
            'output_file': f'static/output/{output_filename}',
            'csv_data': qa_pairs
        })

        return JSONResponse(content=response_data)
    except Exception as e:
        print(f'Error in analyze endpoint: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8080, reload=True)