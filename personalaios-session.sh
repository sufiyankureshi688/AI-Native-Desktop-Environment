#!/bin/bash
# PersonalAIOS Session Script - Updated for Modular Architecture
cd "$(dirname "$0")"
export PERSONALAIOS_SESSION="true"  
export PYTHONPATH="$PWD:$PYTHONPATH"
MODE="--desktop-mode"
[[ "$1" == "--window" ]] && MODE=""
echo "🚀 PersonalAIOS • AI-Native Desktop with Desktop Manager"
exec python3 ai_shell.py $MODE
