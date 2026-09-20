#!/bin/zsh
cd -- "$(dirname -- "$0")" || exit 1
python3 restore.py
result=$?
printf '\n按回车关闭窗口…'
read -r
exit "$result"
