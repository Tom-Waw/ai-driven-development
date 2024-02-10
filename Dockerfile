FROM python:3.10-slim
LABEL maintainer="Tom Wawerek"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc

# Install pip requirements
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

# LLM Configuration
COPY OAI_CONFIG_LIST.json .

WORKDIR /app
COPY ./src .


# Development Requirements
RUN pip install -r requirements-dev.txt

CMD ["python", "main.py"]
