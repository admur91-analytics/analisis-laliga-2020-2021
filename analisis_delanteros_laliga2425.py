import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
import numpy as np

from statsbombpy import sb

# Traer todos los partidos de La Liga 2020/2021
partidos = sb.matches(competition_id=11, season_id=90)

# Traer eventos de todos los partidos
print("Cargando eventos...")
todos_eventos = []
for match_id in partidos['match_id']:
    eventos = sb.events(match_id=match_id)
    todos_eventos.append(eventos)

df_eventos = pd.concat(todos_eventos, ignore_index=True)

# Filtrar solo tiros
tiros = df_eventos[df_eventos['type'] == 'Shot'].copy()

# Calcular estadísticas por jugador
resumen = tiros.groupby('player').agg(
    tiros_totales=('shot_outcome', 'count'),
    goles=('shot_outcome', lambda x: (x == 'Goal').sum()),
    xG_total=('shot_statsbomb_xg', 'sum')
).reset_index()

# Filtrar jugadores con al menos 5 tiros y top 10
resumen = resumen[resumen['tiros_totales'] >= 5]
resumen = resumen.sort_values('goles', ascending=False).head(10)

# Diferencia goles reales vs xG
resumen['diferencia'] = resumen['goles'] - resumen['xG_total']

# Nombres cortos
nombres_map = {
    'Lionel Andrés Messi Cuccittini': 'Messi',
    'Antoine Griezmann': 'Griezmann',
    'Ousmane Dembélé': 'Dembélé',
    'Anssumane Fati': 'Ansu Fati',
    'Francisco António Machado Mota de Castro Trincão': 'Trincão',
    'Pedro González López': 'Pedri',
    'Jordi Alba Ramos': 'Jordi Alba',
    'Sergino Dest': 'Dest',
    'Ronald Federico Araújo da Silva': 'Araújo',
    'Philippe Coutinho Correia': 'Coutinho'
}
resumen['nombre_corto'] = resumen['player'].map(nombres_map).fillna(resumen['player'])

# ---- GRÁFICO 1: Goles marcados ----
fig1, ax1 = plt.subplots(figsize=(12, 6), facecolor='#f5f5f5')
ax1.set_facecolor('#f5f5f5')

barras = ax1.bar(resumen['nombre_corto'], resumen['goles'],
                  color='#1a5276', edgecolor='white', linewidth=0.8)

ax1.set_title('Goles Marcados - Top 10 Jugadores\nLa Liga 2020/21 | Datos: StatsBomb',
              fontsize=13, fontweight='bold', pad=15)
ax1.set_xlabel('')
ax1.set_ylabel('Goles', fontsize=11)
ax1.tick_params(axis='x', rotation=45, labelsize=10)
plt.xticks(ha='right')
ax1.grid(axis='y', alpha=0.3)
ax1.spines[['top', 'right']].set_visible(False)

for barra in barras:
    altura = barra.get_height()
    ax1.text(barra.get_x() + barra.get_width()/2., altura + 0.3,
             f'{int(altura)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
fig1.savefig('grafico1_goles_marcados.png', dpi=150, bbox_inches='tight')

# ---- GRÁFICO 2: Goles Esperados vs Goles Reales ----
fig2, ax2 = plt.subplots(figsize=(14, 7), facecolor='#f5f5f5')
ax2.set_facecolor('#f5f5f5')

x = np.arange(len(resumen))
ancho = 0.35

barras_xg = ax2.bar(x - ancho/2, resumen['xG_total'].round(1),
                     ancho, label='Goles Esperados (xG)',
                     color='#2e86c1', edgecolor='white', linewidth=0.8)

barras_goles = ax2.bar(x + ancho/2, resumen['goles'],
                        ancho, label='Goles Reales',
                        color='#e67e22', edgecolor='white', linewidth=0.8)

ax2.set_title('Goles Esperados (xG) vs Goles Reales\nLa Liga 2020/21 | Datos: StatsBomb',
              fontsize=13, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(resumen['nombre_corto'], rotation=45, ha='right', fontsize=10)
ax2.set_ylabel('Goles', fontsize=11)
ax2.legend(fontsize=11)
ax2.grid(axis='y', alpha=0.3)
ax2.spines[['top', 'right']].set_visible(False)

for barra in barras_xg:
    altura = barra.get_height()
    ax2.text(barra.get_x() + barra.get_width()/2., altura + 0.2,
             f'{altura:.1f}', ha='center', va='bottom', fontsize=9)

for barra in barras_goles:
    altura = barra.get_height()
    ax2.text(barra.get_x() + barra.get_width()/2., altura + 0.2,
             f'{int(altura)}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
fig2.savefig('grafico2_xg_vs_reales.png', dpi=150, bbox_inches='tight')

# ---- TABLA ----
fig3, ax3 = plt.subplots(figsize=(11, 4), facecolor='#f5f5f5')
ax3.axis('off')

tabla_data = resumen[['nombre_corto', 'tiros_totales', 'goles', 'xG_total', 'diferencia']].copy()
tabla_data['xG_total'] = tabla_data['xG_total'].round(2)
tabla_data['diferencia'] = tabla_data['diferencia'].round(2)

tabla = ax3.table(
    cellText=tabla_data.values,
    colLabels=['Jugador', 'Tiros', 'Goles', 'xG', 'Diferencia (G - xG)'],
    cellLoc='center',
    loc='center'
)

tabla.auto_set_font_size(False)
tabla.set_fontsize(11)
tabla.scale(1.2, 1.8)

for j in range(5):
    tabla[0, j].set_facecolor('#1a5276')
    tabla[0, j].set_text_props(color='white', fontweight='bold')

for i in range(1, len(tabla_data) + 1):
    color = '#d6eaf8' if i % 2 == 0 else 'white'
    for j in range(5):
        tabla[i, j].set_facecolor(color)

ax3.set_title('Tabla de Estadísticas Detalladas - Top 10 Goleadores\nLa Liga 2020/21',
              fontsize=13, fontweight='bold', pad=20)

plt.tight_layout()
fig3.savefig('tabla_estadisticas.png', dpi=150, bbox_inches='tight')

plt.show()
print("¡Tres archivos guardados: grafico1_goles_marcados.png, grafico2_xg_vs_reales.png, tabla_estadisticas.png!")