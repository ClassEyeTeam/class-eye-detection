# Use the official Python image
FROM python:3.11.3-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first
COPY requirements.txt .

# Install dependencies (these layers will be cached unless requirements.txt changes)
RUN pip install --no-cache-dir \
    Flask==3.1.0 \
    pymongo==4.10.1 \
    requests==2.32.3 \
    python-dotenv==1.0.1 \
    pytz==2024.2

RUN pip install --no-cache-dir \
    tensorflow-cpu==2.15.0 \
    scikit-learn==1.6.0 \
    opencv-python-headless==4.5.5.64 \
    mtcnn==0.1.1

RUN pip install --no-cache-dir \
    boto3==1.35.81 \
    python-jose==3.3.0 \
    py-eureka-client==0.11.13

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --no-deps deepface==0.0.93
# Manually install deepface dependencies
# Manually install deepface dependencies
RUN pip install --no-deps --no-cache-dir \
    gdown==5.2.0 \
    retina-face==0.0.17 \
    tqdm==4.65.0 \
    Pillow==9.4.0 \
    numpy==1.24.3 \
    pandas==1.5.3

RUN pip install --no-deps --no-cache-dir \
        filelock==3.9.0
RUN pip install --no-cache-dir \
        bs4==0.0.1 
RUN pip install --no-cache-dir \
        paho-mqtt==2.1.0
RUN pip install --no-cache-dir \
        gunicorn==20.1.0


# Copy application code LAST
COPY . .
EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "180"]