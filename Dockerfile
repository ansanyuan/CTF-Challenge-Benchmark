FROM docker.cat/docker/python:3.12
WORKDIR /app
COPY . .
RUN pip install .
CMD ["ccb"]