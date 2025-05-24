FROM python:3.13-slim
WORKDIR /app

COPY pyproject.toml .
RUN pip install uv
RUN uv pip install --no-cache-dir --system -r pyproject.toml

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
