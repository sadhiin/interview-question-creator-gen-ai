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

from src.helper import llm_pipeline

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
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
async def upload(request: Request, pdf_file: UploadFile = File(...), data: UploadPDF = Depends()):
    base_folder = 'static/docs/'

    if not os.path.isdir(base_folder):
        os.makedirs(base_folder)
    pdf_filename = os.path.join(base_folder, data.filename)

    async with aiofiles.open(pdf_filename, 'wb') as f:
        content = await pdf_file.read()
        await f.write(content)

    response_data = jsonable_encoder({'msg': 'success', 'pdf_filename': pdf_filename})

    return JSONResponse(content=response_data)

def get_csv(file_path):
    question_list, answer_generator_chain = llm_pipeline(file_path)

    base_folder = 'static/output'
    if not os.path.isdir(base_folder):
        os.makedirs(base_folder)

    output_file = os.path.join(base_folder, 'QA.csv')

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Question', 'Answer'])

        for question in question_list:
            print('Question: ', question)
            answer = answer_generator_chain.run(question)
            print('Answer: ', answer)
            print('-' * 50, end='')
            print('\n\n')

            csv_writer.writerow([question, answer])

    return output_file

@app.post('/analyze')
async def chat(request: Request, data: AnalyzePDF = Depends()):
    base_folder = 'static/docs/'
    pdf_file_path = os.path.join(base_folder, data.pdf_filename)

    # Check if the file exists
    if not os.path.isfile(pdf_file_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")

    output_file = get_csv(pdf_file_path)
    response_data = jsonable_encoder({'output_file': output_file})

    return Response(response_data)

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8080, reload=True)