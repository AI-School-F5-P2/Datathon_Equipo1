import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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


matplotlib.use('TkAgg') # Se pone matplolib para sacar los gráficos en pantalla.

## Gráfica para el total de Estados Unidos con Matplolib solamente
# Calcular los nuevos casos diarios y nuevas muertes diarias

# Convertir la columna 'date' a valores numéricos (días desde el inicio de los datos)
frames['days_since_start'] = (frames['date'] - frames['date'].min()).dt.days

# Crear un gráfico de dispersión con ajuste de regresión con Seaborn
# Establecer el estilo de Seaborn
def format_y_axis(y, _):
    return '{:,.0f}'.format(y).replace(",", ".")

sns.set(style="whitegrid")
sns.set_palette("muted")
plt.figure(figsize=(10, 6))
sns.regplot(x='days_since_start', y='positive', data=frames, scatter_kws={'color': 'blue'}, line_kws={'color': 'red'})
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(format_y_axis))  # Aplicar formato personalizado al eje Y
plt.title('Total de casos de COVID-19 en Estados Unidos')
plt.xlabel('Días desde el inicio de los datos')
plt.ylabel('Total de casos')
plt.tight_layout()
plt.show()
