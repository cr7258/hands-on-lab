FROM python:3.9-slim as base

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /favoriteservice

#install opentelemetry packages
RUN pip install opentelemetry-distro \
	opentelemetry-exporter-otlp

RUN opentelemetry-bootstrap -a install

# Add the application
COPY . .

EXPOSE 5000
ENTRYPOINT [ "opentelemetry-instrument", "python", "main.py"]