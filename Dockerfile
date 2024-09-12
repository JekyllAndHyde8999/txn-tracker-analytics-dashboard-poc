FROM python:3.12

WORKDIR /app

RUN apt-get update
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y

COPY ./src .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "st_dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
