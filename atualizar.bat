@'
@echo off
cd /d "C:\Users\fcnal\onde.esta.automatizado"
(
echo ===== %date% %time% =====
git pull --rebase --autostash origin main
if errorlevel 1 (
  echo [ERRO] git pull falhou. Abortando.
  exit /b 1
)
python conversor.py
if errorlevel 1 (
  echo [ERRO] conversor.py falhou. Abortando.
  exit /b 1
)
git add data.js index.html
git diff --cached --quiet || (git commit -m "Atualizacao automatica" && git push origin main)
) >> atualizar.log 2>&1
'@ | Set-Content -Path atualizar.bat -Encoding ascii