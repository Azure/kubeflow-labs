FROM tensorflow/tensorflow:1.7.0-gpu
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN mkdir ./output
RUN mkdir ./logs
RUN mkdir ./checkpoints
RUN pip install -r requirements.txt
COPY ./* /app/

ENTRYPOINT [ "python", "/app/main.py" ]