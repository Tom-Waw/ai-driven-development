FROM python:3.10-slim
LABEL maintainer="Tom Wawerek"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
RUN pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /home/app
COPY ./src .

CMD ["python", "main.py"]
