import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score
from db_connector import obtener_datos_gold

def entrenar_y_guardar():
    print("Conectando con Supabase para obtener datos de la Capa Gold...")
    try:
        df = obtener_datos_gold()
        print(f"Datos obtenidos exitosamente de Supabase: {len(df)} filas.")
    except Exception as e:
        print(f"Atención: No se pudo conectar a Supabase ({e}). Usando CSV local...")
        df = pd.read_csv("Datos fisioterapia 2023 2026.csv")
        if 'ID' in df.columns:
            df.rename(columns={'ID': 'id_paciente'}, inplace=True)
        df['indice_vulnerabilidad_psicosocial'] = df['kinesiofobia_tsk'] + df['catastrofismo_pcs']

    cat_features = ['genero', 'ocupacion_demanda', 'tipo_lesion', 'cronicidad', 'actividad_fisica_previa']
    num_features = [
        'edad', 'imc', 'dolor_inicial_eva', 'cirugias_previas', 'comorbilidades_num',
        'rom_inicial_pct', 'fuerza_inicial_daniels', 'kinesiofobia_tsk', 'catastrofismo_pcs',
        'indice_vulnerabilidad_psicosocial', 'asistencia_sesiones_pct',
        'cumplimiento_ejercicios_casa', 'num_sesiones_totales'
    ]

    X = df[cat_features + num_features]
    y = df['resultado_tratamiento'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
            ('num', 'passthrough', num_features)
        ]
    )

    model_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    print("Entrenando algoritmo Random Forest...")
    model_pipeline.fit(X_train, y_train)

    y_pred = model_pipeline.predict(X_test)
    y_proba = model_pipeline.predict_proba(X_test)[:, 1]

    print(f"ROC-AUC Alcanzado: {roc_auc_score(y_test, y_proba):.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs("models", exist_ok=True)
    ruta_salida = "models/modelo_fisioterapia.joblib"
    joblib.dump(model_pipeline, ruta_salida)
    print(f"Modelo guardado exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    entrenar_y_guardar()