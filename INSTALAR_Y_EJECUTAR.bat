@echo off
echo ==========================================
echo SISTEMA DE FISIOTERAPIA - INSTALACION
echo ==========================================
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Entrenando modelo...
python src\train_model.py
echo.
echo Iniciando Streamlit...
streamlit run app.py
pause
