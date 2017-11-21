FROM tensorflow/tensorflow:1.4.0
RUN mkdir /app && mkdir /app/logs
COPY distributed.py /app/distributed.py
ENTRYPOINT ["python", "/app/distributed.py"]
