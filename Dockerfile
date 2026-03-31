FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# main app
COPY ./app /app/app

# mock gateway goes inside /app
COPY ./mock_gateway /app/mock_gateway

COPY ./tests /app/tests

EXPOSE 8000 9000

CMD sh -c "\
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & \
cd /app/mock_gateway && uvicorn main:app --host 0.0.0.0 --port 9000 --reload & \
wait"