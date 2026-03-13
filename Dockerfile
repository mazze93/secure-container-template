# syntax=docker/dockerfile:1.7

FROM python:3.12-slim-bookworm@sha256:4c50375fc4b8ea5ca06ac9485186ccb50171c99390b0e9300c2bac871cc2dc3e

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 10001 appuser \
 && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

USER appuser

EXPOSE 8000
CMD ["python", "-m", "src.main"]
