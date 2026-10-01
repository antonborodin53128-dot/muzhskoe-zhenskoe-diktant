ДИКТАНТ v11 — ABSOLUTE AUDIO PATH FIX
Интерфейс и механика v10 не менялись.

Исправление:
BASE_DIR = директория app.py
AUDIO_DIR = BASE_DIR/audio
/audio/<filename> отдаёт файл из абсолютного AUDIO_DIR.

Диагностика после Deploy:
/audio-status
/audio/01.mp3
/audio-test
