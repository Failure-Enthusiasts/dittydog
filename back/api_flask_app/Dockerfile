FROM --platform=linux/amd64 python:3.8-slim-buster
WORKDIR /app
COPY backend.py helper_functions.py requirements.txt prefix.py redis_helper.py ./
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]