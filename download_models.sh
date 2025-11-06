#!/bin/bash

# Скрипт для скачивания моделей GolosAI-DE
# Usage: ./download_models.sh

set -e

echo "🚀 GolosAI-DE - Скачивание моделей"
echo "===================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Создание директорий
echo -e "${YELLOW}📁 Создание директорий...${NC}"
mkdir -p models/tts
mkdir -p models/asr
mkdir -p models/llm

# Скачивание TTS моделей
echo -e "${YELLOW}🔊 Скачивание TTS моделей (Piper)...${NC}"
cd models/tts

# Проверка наличия wget
if ! command -v wget &> /dev/null; then
    echo -e "${RED}❌ wget не установлен. Установите: sudo apt install wget${NC}"
    exit 1
fi

# Thorsten High (мужской голос, высокое качество)
if [ ! -f "de_DE-thorsten-high.onnx" ]; then
    echo -e "${GREEN}⬇️  Скачивание de_DE-thorsten-high...${NC}"
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
else
    echo -e "${GREEN}✅ de_DE-thorsten-high уже скачан${NC}"
fi

# Thorsten Low (мужской голос, быстрый)
if [ ! -f "de_DE-thorsten-low.onnx" ]; then
    echo -e "${GREEN}⬇️  Скачивание de_DE-thorsten-low...${NC}"
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/low/de_DE-thorsten-low.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/low/de_DE-thorsten-low.onnx.json
else
    echo -e "${GREEN}✅ de_DE-thorsten-low уже скачан${NC}"
fi

# Eva (женский голос)
if [ ! -f "de_DE-eva_k_x_low.onnx" ]; then
    echo -e "${GREEN}⬇️  Скачивание de_DE-eva_k_x_low...${NC}"
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k_x_low.onnx
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low/de_DE-eva_k_x_low.onnx.json
else
    echo -e "${GREEN}✅ de_DE-eva_k_x_low уже скачан${NC}"
fi

cd ../..

echo ""
echo -e "${GREEN}✅ Все модели успешно скачаны!${NC}"
echo ""
echo "📊 Размер моделей:"
du -sh models/tts/

echo ""
echo -e "${YELLOW}ℹ️  Примечание:${NC}"
echo "  - ASR модели (Whisper) загрузятся автоматически при первом запуске"
echo "  - LLM модели нужно добавить вручную в models/llm/"
echo ""
echo -e "${GREEN}🚀 Теперь можно запустить проект: docker-compose up --build -d${NC}"
