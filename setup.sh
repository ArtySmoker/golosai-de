#!/bin/bash

# Скрипт автоматической установки GolosAI-DE
# Usage: ./setup.sh

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║      GolosAI-DE Setup Script         ║"
echo "║   AI Voice Dialogue System           ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Проверка Docker
echo -e "${YELLOW}🔍 Проверка зависимостей...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker установлен${NC}"

# Проверка Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не установлен!${NC}"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose установлен${NC}"

# Проверка wget
if ! command -v wget &> /dev/null; then
    echo -e "${YELLOW}⚠️  wget не установлен. Установка...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y wget
    elif command -v yum &> /dev/null; then
        sudo yum install -y wget
    else
        echo -e "${RED}❌ Не удалось установить wget. Установите вручную.${NC}"
        exit 1
    fi
fi

# Создание директорий
echo ""
echo -e "${YELLOW}📁 Создание структуры директорий...${NC}"
mkdir -p models/{asr,llm,tts}
mkdir -p config
echo -e "${GREEN}✅ Директории созданы${NC}"

# Скачивание моделей
echo ""
echo -e "${YELLOW}⬇️  Скачивание TTS моделей...${NC}"
echo "Это может занять несколько минут..."

cd models/tts

# Thorsten High
if [ ! -f "de_DE-thorsten-high.onnx" ]; then
    echo -e "${BLUE}📥 Скачивание de_DE-thorsten-high (мужской голос, высокое качество)...${NC}"
    wget -q --show-progress \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
    wget -q \
        https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
    echo -e "${GREEN}✅ Скачан${NC}"
else
    echo -e "${GREEN}✅ de_DE-thorsten-high уже существует${NC}"
fi

cd ../..

# Проверка конфигурационных файлов
echo ""
echo -e "${YELLOW}⚙️  Проверка конфигурации...${NC}"

if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}❌ config/config.yaml не найден${NC}"
    echo "Убедитесь, что все файлы проекта на месте"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml не найден${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Конфигурация найдена${NC}"

# Сборка и запуск
echo ""
echo -e "${YELLOW}🔨 Сборка Docker образов...${NC}"
echo "Это может занять 5-10 минут при первом запуске..."

if docker compose version &> /dev/null; then
    docker compose build
else
    docker-compose build
fi

echo ""
echo -e "${YELLOW}🚀 Запуск сервисов...${NC}"

if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Ожидание запуска
echo ""
echo -e "${YELLOW}⏳ Ожидание готовности сервисов...${NC}"
sleep 10

# Проверка статуса
echo ""
echo -e "${YELLOW}📊 Статус сервисов:${NC}"
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

# Финальное сообщение
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║     ✅ Установка завершена!          ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}🌐 Откройте в браузере:${NC} ${GREEN}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  Просмотр логов:      docker-compose logs -f"
echo "  Остановка:           docker-compose down"
echo "  Перезапуск:          docker-compose restart"
echo "  Статус:              docker-compose ps"
echo ""
echo -e "${YELLOW}📚 Документация:${NC} См. README.md"
echo ""
