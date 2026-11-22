FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir "poetry>=2.0.0"
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY . /app/
CMD ["python", "main.py"]