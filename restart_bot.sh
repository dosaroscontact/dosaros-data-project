#!/bin/bash
# Reinicia el bot de Telegram en tmux

cd /home/pi/dosaros-data-project

git pull origin main

tmux send-keys -t bot_consultas C-c Enter
sleep 2
tmux send-keys -t bot_consultas "PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py" Enter

echo "Bot reiniciado. Ver logs: tmux attach -t bot_consultas"
