FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# دانلود XMRig استاتیک (خودکفا، نیاز به کتابخانه‌ی اضافه نداره)
RUN curl -L -o /tmp/xmrig.tar.gz \
        https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-x64.tar.gz \
    && tar -xzf /tmp/xmrig.tar.gz -C /tmp \
    && mv /tmp/xmrig-6.21.0/xmrig /usr/local/bin/xmrig \
    && chmod +x /usr/local/bin/xmrig \
    && rm -rf /tmp/xmrig* \
    && /usr/local/bin/xmrig --version

COPY . .
RUN mkdir -p /app/data && chmod 777 /app/data

ENV XMRIG_PATH=/usr/local/bin/xmrig
ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
