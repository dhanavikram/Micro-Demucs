FROM xserrat/facebook-demucs:latest

ENTRYPOINT []

RUN pip install redis minio requests

COPY worker-server.py /app/worker-server.py

WORKDIR /app

CMD ["python3", "worker-server.py"]