FROM python:3.11-slim
WORKDIR /app

# Add build argument to help invalidate cache for static files
ARG BUILD_DATE
ARG VCS_REF
ARG CACHE_BUST

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY config.py ./
COPY auth.py ./
COPY docs ./docs
COPY frontend ./frontend
COPY templates ./templates

# Copy static files last and add build info to help with caching
# Use CACHE_BUST to force cache invalidation
COPY static ./static
# Add build metadata to help with cache invalidation
RUN echo "Build Date: ${BUILD_DATE:-$(date -u +'%Y-%m-%dT%H:%M:%SZ')}" > /app/build-info.txt && \
    echo "Git Commit: ${VCS_REF:-unknown}" >> /app/build-info.txt && \
    echo "Cache Bust: ${CACHE_BUST:-unknown}" >> /app/build-info.txt

EXPOSE 5000
CMD ["python", "app.py"]
