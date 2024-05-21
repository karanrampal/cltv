FROM europe-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest

WORKDIR /cltv

COPY requirements.txt requirements.txt
COPY ./src .
RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "main"]