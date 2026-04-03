FROM python:3.12-slim

WORKDIR /app

# need to give the file path since its going to be building from the project root
COPY scraper/requirements.txt .

# don't have to give the file path since its now in the container
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scraper/schedulder.py"]