FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential python3-dev
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python", "draft.py"]
