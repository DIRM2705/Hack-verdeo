import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt

# 1. Cargar y preparar datos
df = pd.read_csv('consumo_de_agua.csv')
df = df.dropna(subset=['lote', 'PERIODO', 'Fpago', 'TOTAL'])
df['Fpago'] = pd.to_datetime(df['Fpago'], errors='coerce')
df = df.dropna(subset=['Fpago'])

# 2. Ingeniería de Características (Feature Engineering)
# Calcular estadísticas generales por lote
lote_stats = df.groupby('lote').agg(
    Total_Pagos=('PERIODO', 'count'),
    Periodo_Alta=('PERIODO', 'min'),
    Monto_Promedio=('TOTAL', 'mean')
)

# Calcular los "Huecos" para definir quién es moroso actualmente
max_periodo_global = df['PERIODO'].max()
lote_stats['Periodos_Esperados'] = max_periodo_global - lote_stats['Periodo_Alta'] + 1
lote_stats['Huecos'] = lote_stats['Periodos_Esperados'] - lote_stats['Total_Pagos']
lote_stats['Huecos'] = lote_stats['Huecos'].apply(lambda x: max(0, x))

# Calcular hábitos de pago (Días entre pagos)
df_sorted = df.sort_values(['lote', 'Fpago'])
df_sorted['Dias_Entre_Pagos'] = df_sorted.groupby('lote')['Fpago'].diff().dt.days

pagos_stats = df_sorted.groupby('lote').agg(
    Promedio_Dias=('Dias_Entre_Pagos', 'mean'),
    Inconsistencia_Dias=('Dias_Entre_Pagos', 'std') # Desviación estándar (qué tan erráticos son)
).fillna(0) # Lotes con 1 solo pago tendrán NaN, rellenamos con 0

# Unir todas las características
df_model = lote_stats.join(pagos_stats)

# 3. Definir la Variable Objetivo (Target)
# Consideraremos "Alto Riesgo / Moroso" (1) si tienen 3 o más periodos atrasados. Si no, "Buen Cliente" (0).
df_model['Es_Moroso'] = (df_model['Huecos'] >= 3).astype(int)

# 4. Entrenar el Modelo (Random Forest)
# Variables predictoras (Excluimos Total_Pagos y Huecos porque directamente definen la variable objetivo)
features = ['Monto_Promedio', 'Promedio_Dias', 'Inconsistencia_Dias']
X = df_model[features]
y = df_model['Es_Moroso']

# Dividir en datos de entrenamiento (70%) y prueba (30%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Crear y entrenar el bosque aleatorio
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)

# Predicciones
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

# 5. Generar gráfica de Importancia de Variables
importances = rf.feature_importances_
plt.figure(figsize=(8, 5))
plt.barh(features, importances, color='#FF9800', edgecolor='black')
plt.title('¿Qué factores predicen mejor la Morosidad?', fontsize=14)
plt.xlabel('Importancia (0 a 1)', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('importancia_variables.png')
plt.close()

# 6. Predecir la "Probabilidad de Riesgo" para todos los lotes actuales
# rf.predict_proba devuelve [Probabilidad_Buen_Cliente, Probabilidad_Moroso]
probabilidades = rf.predict_proba(X)
df_model['Probabilidad_Riesgo_%'] = (probabilidades[:, 1] * 100).round(2)

print(df_model)

#7. Guardar en CSV para análisis posterior
df_model.to_csv('lotes_con_probabilidad_riesgo.csv', index=True)

# Mostrar resultados
print(f"Precisión del Modelo: {acc*100:.2f}%\n")
print("--- Reporte de Clasificación ---")
print(classification_report(y_test, y_pred, target_names=['Buen Cliente (0)', 'Moroso (1)']))

print("\n--- Top 5 Lotes con MAYOR Riesgo de Impago (Que hoy NO son morosos graves) ---")
# Filtramos a los que tienen huecos < 3 (es decir, parecen ir bien) pero el modelo dice que van a fallar
en_riesgo = df_model[df_model['Huecos'] < 3].sort_values('Probabilidad_Riesgo_%', ascending=False)
print(en_riesgo[['Monto_Promedio', 'Promedio_Dias', 'Inconsistencia_Dias', 'Huecos', 'Probabilidad_Riesgo_%']].head())

print("\n--- Top 5 Lotes con MENOR Riesgo de Impago ---")
# Filtramos a los que tienen huecos >= 3 (es decir, parecen mal) pero el modelo dice que van a seguir bien
buenos = df_model[df_model['Huecos'] >= 3].sort_values('Probabilidad_Riesgo_%')
print(buenos[['Monto_Promedio', 'Promedio_Dias', 'Inconsistencia_Dias', 'Huecos', 'Probabilidad_Riesgo_%']].head())