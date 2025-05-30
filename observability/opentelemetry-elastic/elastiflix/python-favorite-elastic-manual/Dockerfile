FROM python:3.9-slim as base

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /favoriteservice


# Add the application
COPY . .

EXPOSE 5000
ENTRYPOINT [ "python", "main.py" ]