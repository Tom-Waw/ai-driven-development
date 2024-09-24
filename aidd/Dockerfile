FROM python:3.10-slim
LABEL maintainer="Tom Wawerek"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

# Install pip requirements
RUN pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /home/app/app
COPY ./src .

CMD ["python", "main.py"]
