FROM python:3.11-slim

WORKDIR /app

# need to give the file path since its going to be building from the project root
COPY scraper/requirements.txt .

# don't have to give the file path since its now in the container
RUN pip install --no-cache-dir -r requirements.txt

# copy everything from scaper into the container
COPY scraper/ .

CMD ["python", "scraper/scheduler.py"]