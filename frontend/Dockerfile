FROM python:3.10-slim

WORKDIR /app

# Сначала системные зависимости
RUN apt-get update && apt-get install -y ffmpeg build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установим Python-зависимости
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запускаем Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=3000", "--server.address=0.0.0.0"]