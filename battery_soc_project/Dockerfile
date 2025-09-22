# Python 3.9 slim base image
FROM python:3.9-slim

# Çalışma dizini oluştur
WORKDIR /app

# Sistem güncellemesi ve gerekli paketler
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python gereksinimlerini kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY src/ ./src/
COPY models/ ./models/
COPY data/processed/ ./data/processed/

# Gerekli dizinleri oluştur
RUN mkdir -p reports logs

# Port açığa çıkar
EXPOSE 5000

# Ortam değişkenleri
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Uygulamayı başlat
CMD ["python", "src/api.py"]