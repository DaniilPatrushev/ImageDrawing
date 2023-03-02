FROM python:3.9.5

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir /app/images

ADD /app /app

ENV LOCAL_STORAGE_IMAGE_PATH /app/images/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
