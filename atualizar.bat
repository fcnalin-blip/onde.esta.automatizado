@echo off
cd /d "C:\Users\fcnal\onde.esta.automatizado"
(
echo ===== %date% %time% =====
git pull --rebase --autostash origin main
python conversor.py
git add data.js index.html
git diff --cached --quiet || (git commit -m "Atualizacao automatica" && git push origin main)
) >> atualizar.log 2>&1
