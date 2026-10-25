#!/usr/bin/env bash
# ==============================================================================
# edit-reel — Universal Installer for Antigravity, Claude Code, Cursor & Codex
# Author: Mohammed Mhaidra (@MMhaidra)
# Repository: https://github.com/MMhaidra/edit-reel
# ==============================================================================

set -e

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}====================================================================${RESET}"
echo -e "${BOLD}${CYAN}       🎬 Installing edit-reel — Autonomous AI Video Editor         ${RESET}"
echo -e "${BOLD}${CYAN}====================================================================${RESET}"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ python3 could not be found. Please install Python 3.9+ first.${RESET}"
    exit 1
fi

# 2. Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  ffmpeg is not found in PATH.${RESET}"
    echo -e "   Please install ffmpeg for audio mastering and video rendering:"
    echo -e "   - macOS:  brew install ffmpeg"
    echo -e "   - Ubuntu: sudo apt update && sudo apt install -y ffmpeg"
    echo ""
fi

# 3. Determine Repo Directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_DIR="${HOME}/.gemini/config/skills/edit-reel"
CLAUDE_DIR="${HOME}/.claude/skills/edit-reel"

echo -e "${CYAN}📁 Repository Directory:${RESET} ${SCRIPT_DIR}"

# 4. Set up Virtual Environment
if [ ! -d "${SCRIPT_DIR}/.venv" ]; then
    echo -e "${CYAN}⚙️  Creating Python virtual environment in .venv ...${RESET}"
    python3 -m venv "${SCRIPT_DIR}/.venv"
fi

echo -e "${CYAN}📦 Installing dependencies from requirements.txt ...${RESET}"
"${SCRIPT_DIR}/.venv/bin/pip" install --upgrade pip -q
"${SCRIPT_DIR}/.venv/bin/pip" install -r "${SCRIPT_DIR}/requirements.txt" -q

# 5. Link/Install for Google Antigravity
mkdir -p "${HOME}/.gemini/config/skills"
if [ "${SCRIPT_DIR}" != "${TARGET_DIR}" ]; then
    echo -e "${CYAN}🔗 Linking skill to Google Antigravity (~/.gemini/config/skills/edit-reel)...${RESET}"
    rm -rf "${TARGET_DIR}"
    ln -s "${SCRIPT_DIR}" "${TARGET_DIR}"
fi

# 6. Link/Install for Claude Code
if [ -d "${HOME}/.claude" ]; then
    mkdir -p "${HOME}/.claude/skills"
    if [ "${SCRIPT_DIR}" != "${CLAUDE_DIR}" ]; then
        echo -e "${CYAN}🔗 Linking skill to Claude Code (~/.claude/skills/edit-reel)...${RESET}"
        rm -rf "${CLAUDE_DIR}"
        ln -s "${SCRIPT_DIR}" "${CLAUDE_DIR}"
    fi
fi

echo ""
echo -e "${BOLD}${GREEN}✅ Successfully installed edit-reel!${RESET}"
echo ""
echo -e "${BOLD}🚀 How to use:${RESET}"
echo -e "  ${BOLD}1. Google Antigravity:${RESET}"
echo -e "     Prompt: ${CYAN}/edit-reel english${RESET} or ${CYAN}/edit-reel darija${RESET}"
echo ""
echo -e "  ${BOLD}2. Claude Code / Codex / Cursor:${RESET}"
echo -e "     Ask: ${CYAN}\"Edit my raw video using the edit-reel skill in ~/.gemini/config/skills/edit-reel\"${RESET}"
echo ""
echo -e "  ${BOLD}3. Direct CLI (Standalone):${RESET}"
echo -e "     ${CYAN}${SCRIPT_DIR}/.venv/bin/python3 ${SCRIPT_DIR}/scripts/pipeline.py -i <input.mp4> --lang en${RESET}"
echo ""
echo -e "${BOLD}${CYAN}Enjoy high-engagement, tactile editorial video creation!${RESET}"
