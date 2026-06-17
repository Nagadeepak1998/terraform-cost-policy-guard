FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 8080

CMD ["uvicorn", "terraform_cost_policy_guard.main:app", "--host", "0.0.0.0", "--port", "8080"]
