import sys
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from bokeh.plotting import figure, show
from bokeh.io import output_notebook

url_csv = "https://api.covidtracking.com/v1/states/daily.csv"
url_json = "https://api.covidtracking.com/v1/states/daily.json"

################################ OBTENER LOS DATOS Y CREAR UN DATAFRAME #################################
hist_covid = requests.get(url_json)
awnser_code = hist_covid.status_code
if awnser_code != 200:
    print("Error en la lectura de datos.")
    sys.exit()
json_covid = hist_covid.json()
frames = pd.DataFrame(json_covid) # Obtenemos el DataFrame
#print(frames.info()) # Verificar la estructura del DataFrame
frames.fillna(0, inplace=True) # Rellenar con 0 los valores faltantes (si los hay)
frames['date'] = pd.to_datetime(frames['date'], format='%Y%m%d') # Convertir la columna de fecha al tipo de dato datetime
descripcion = frames.describe() # Datos promedio

################################ INFORMES POR ESTADO Y GLOBAL USA #################################
# Calcular el total de casos, muertes y recuperaciones para cada estado y para EE. UU. en general
'''
totales_estado = frames.groupby('state').agg({
    'positive': 'max',
    'death': 'max',
    'recovered': 'max',
}).reset_index()
'''
# Agrupar por 'state' y 'date' y sumar las columnas relevantes
totales_estado = frames.groupby(['state', 'date']).sum().reset_index()

totales_usa = frames.groupby('date').agg({
    'positive': 'sum',
    'death': 'sum',
    'recovered': 'sum',
}).reset_index()

print("Totales por estado")
print (totales_estado)
print ()
print ("Totales en USA")
print(totales_usa)

estados_de_eeuu = totales_estado['state'].unique().tolist() # Lista de estados

'''
matplotlib.use('agg') # Se prepara Matplotlib para volcar los gráficos a ficheros.
# Graficos por estado
for state in estados_de_eeuu:
    # Filtrar datos para un estado específico
    state_data = totales_estado[totales_estado['state'] == state]
    # Generar la gráfica y guardarla en un archivo
    plt.figure(figsize=(12, 6))
    plt.plot(state_data['date'], state_data['positive'], label='Casos positivos')
    plt.plot(state_data['date'], state_data['death'], label='Muertes')
    plt.xlabel('Fecha')
    plt.ylabel('Cantidad')
    plt.title(f'Casos positivos y muertes en {state}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig(f'charts/{state}_chart.png')  # Guardar las gráficas como imágenes en el directorio actual
    plt.close()  # Cerrar la figura para liberar memoria
'''

matplotlib.use('TkAgg') # Se pone matplolib para sacar los gráficos en pantalla.

## Gráfica para el total de Estados Unidos con Matplolib solamente
# Calcular los nuevos casos diarios y nuevas muertes diarias
'''
totales_usa['new_positive'] = totales_usa['positive'].diff()
totales_usa['new_death'] = totales_usa['death'].diff()
# Generar la gráfica.
plt.figure(figsize=(12, 6))
plt.plot(totales_usa['date'], totales_usa['new_positive'], label='Nuevos casos positivos', color='blue')
plt.plot(totales_usa['date'], totales_usa['new_death'], label='Nuevas muertes', color='red')
plt.xlabel('Fecha')
plt.ylabel('Cantidad Diaria')
plt.title('Nuevos casos positivos y nuevas muertes diarias en Estados Unidos')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
plt.close()
'''
# Convertir la columna 'date' a valores numéricos (días desde el inicio de los datos)
frames['days_since_start'] = (frames['date'] - frames['date'].min()).dt.days

# Crear un gráfico de dispersión con ajuste de regresión con Seaborn
# Establecer el estilo de Seaborn
'''
sns.set(style="whitegrid")
sns.set_palette("muted")
plt.figure(figsize=(10, 6))
sns.regplot(x='days_since_start', y='positive', data=frames, scatter_kws={'color': 'blue'}, line_kws={'color': 'red'})
plt.title('Total de casos de COVID-19 en Estados Unidos')
plt.xlabel('Días desde el inicio de los datos')
plt.ylabel('Total de casos')
plt.tight_layout()
plt.show()
'''

# Calcular la media de casos de COVID-19 para cada día
mean_cases_per_day = frames.groupby('days_since_start')['positive'].mean().reset_index()
# Calcular la media de defunciones de COVID-19 para cada día
mean_deaths_per_day = frames.groupby('days_since_start')['death'].mean().reset_index()

# Crear un gráfico de línea interactivo con Bokeh
p = figure(width=800, height=400, title='Total de casos de COVID-19 en Estados Unidos',
           x_axis_label='Días desde el inicio de los datos', y_axis_label='Media de casos')

p.line(x='days_since_start', y='positive', source=mean_cases_per_day, line_color='blue', line_width=2, legend_label='Casos registrados')
p.line(x='days_since_start', y='death', source=mean_deaths_per_day, line_color='red', line_width=2, legend_label='Defunciones')

# Agregar leyenda al gráfico
p.legend.location = "top_left"

# Habilitar la salida del gráfico en el notebook
#output_notebook()

# Mostrar el gráfico interactivo en el notebook
show(p)
