# Sistema de Fisioterapia - Predicción

Proyecto preparado con el dataset real `Datos fisioterapia 2023 2026.csv`.

## Dataset
- 1,200 registros
- 20 columnas
- Variable objetivo: `resultado_tratamiento`
- Sin valores faltantes detectados.

## Instalación rápida en Windows

1. Instala Python 3.11 o 3.12.
2. Abre CMD en esta carpeta.
3. Ejecuta:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\train_model.py
streamlit run app.py
```

4. Abre la dirección que muestre Streamlit, normalmente `http://localhost:8501`.

También puedes usar `INSTALAR_Y_EJECUTAR.bat`.

## Variables usadas para la predicción
Se usan las variables de la evaluación inicial:
edad, genero, imc, ocupacion_demanda, tipo_lesion, cronicidad,
dolor_inicial_eva, cirugias_previas, comorbilidades_num,
rom_inicial_pct, fuerza_inicial_daniels, kinesiofobia_tsk,
catastrofismo_pcs y actividad_fisica_previa.

Se excluyen asistencia_sesiones_pct, cumplimiento_ejercicios_casa y
num_sesiones_totales para evitar utilizar información que normalmente se
conoce después de iniciado el tratamiento.

## Resultado
El modelo genera una predicción 0/1 para `resultado_tratamiento`.
La interpretación clínica de 0 y 1 debe corresponder al diccionario de datos
de quien creó el dataset; la aplicación no asume que 1 signifique curación.

## Supabase
`src/db_connector.py` queda preparado para una conexión opcional a Supabase.
No coloques claves reales dentro del código ni las publiques.
