FROM python:3.11-slim

# MALLOC_ARENA_MAX: fewer malloc arenas keeps Streamlit's threads from fragmenting memory
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MALLOC_ARENA_MAX=2 \
    NUMBA_CACHE_DIR=/tmp/numba_cache

# git: face_recognition_models is installed from GitHub
# build-essential: webrtcvad (resemblyzer dependency) has no prebuilt wheels
# libsndfile1: audio decoding for librosa
RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the CPU-only build of PyTorch first so resemblyzer doesn't pull the multi-GB CUDA build
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Render (and most hosts) inject PORT; default to 8501 locally
ENV PORT=8501
EXPOSE 8501

CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0
