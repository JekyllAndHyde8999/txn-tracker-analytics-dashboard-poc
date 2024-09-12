FROM python:3.12

WORKDIR /app

COPY ./src .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "st_integration_test.py", "--server.address=0.0.0.0", "--server.port=8501"]
