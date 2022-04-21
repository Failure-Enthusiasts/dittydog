FROM python:3.8-slim-buster
WORKDIR /app
COPY poller_pruner.py requirements.txt ./
RUN pip3 install -r requirements.txt
CMD [ "python3", "-u", "poller_pruner.py"]