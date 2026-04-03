FROM python:3.11-slim

WORKDIR /app

# need to give the file path since its going to be building from the project root
COPY api/requirements.txt .

# don't have to give the file path since its now in the container
RUN pip install --no-cache-dir -r requirements.txt

# copy everything from the api dir into the container
COPY api/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]