FROM python:3.12-slim

WORKDIR /app

COPY apps /app/apps

ENV PYTHONPATH=/app
ENV GROUP_CLASS_BACKEND_HOST=0.0.0.0
ENV GROUP_CLASS_BACKEND_PORT=18000

EXPOSE 18000

CMD ["python", "-m", "apps.group_class_backend.server"]
