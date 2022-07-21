FROM python:3.8-slim-buster
WORKDIR /app
COPY backend.py helper_functions.py requirements.txt ./
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]