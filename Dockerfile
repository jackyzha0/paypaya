# Define Base Image. We'll use Python 3
FROM python:3-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy requirements and .env
COPY .env /
COPY requirements.txt /

# Install any dependencies
RUN pip install -r requirements.txt

# Copy your Python file to the image
COPY *.py /

# Tell Docker how to start your script
ENTRYPOINT [ "python", "./server.py" ]