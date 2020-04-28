# este script unificará los datos de varias empresas para el prototipo 2
# debe producir un archivo csv para cada empresa, con fechas, crecimeintos y puntuaciones de noticias
import os
import datetime
from statistics import mean
import pandas

# AHORA MISMO ESTÁ EN MODO DE CLASSIFICATION

# guardaremos los datos de empresas separados en dataframes diferentes, en un diccionario
data_dict = {}

# definimos función para calcular el crecimiento
def get_growth(open_price, close_price):
    # en algunos casos, los datos vienen como string, o aparece algún símbolo para indicar que faltan
    if isinstance(open_price, str):
        try:
            open_price = float(open_price.replace(',', ''))
        except ValueError:
            return None
    if isinstance(close_price, str):
        try:
            close_price = float(close_price.replace(',', ''))
        except ValueError:
            return None
    if not (isinstance(open_price, float) or isinstance(close_price, float)):
        raise TypeError("Incorrect data type: " + type(open_price) + ", " + type(close_price))
    return (close_price - open_price) / open_price


def generate_date_list(date1):
    # dada una date1, produce una lista de las fechas de los siguientes 6 días
    transformed_date = datetime.datetime.strptime(date1, "%Y-%m-%d")
    time_delta = datetime.timedelta(days=1)
    aux = [transformed_date]
    for i in range(1, 7):
        next_day = aux[-1] + time_delta
        aux.append(next_day)
    return [date.strftime("%Y-%m-%d") for date in aux]

# creamos las rutas adecuadas para obtener datos y guardarlos
path_bolsa = os.path.join(os.path.dirname(__file__), "datos", "bolsa")
path_noticias = os.path.join(os.path.dirname(__file__), "datos", "noticias - score")
path_final = os.path.join(os.path.dirname(__file__), "datos", "aprendizaje")

for file in os.listdir(path_bolsa):
    # primero buscamos entre los datos de noticias, para comprobar que podemos seguir
    if file not in os.listdir(path_noticias):
        continue
    # adquirimos el dataframe con scores de noticias, y lo ajustamos a nuestras necesidades
    news_data = pandas.read_csv(path2 + "\\" + file)
    news_data.drop(["Unnamed: 0"], axis=1, inplace=True)
    raw_data = pandas.read_csv(path1 + "\\" + file)
    # limpiamos un poco
    raw_data["Date"] = raw_data.apply(lambda row: datetime.datetime.strptime(row["Date"], "%b %d, %Y")
                                      .strftime("%Y-%m-%d"), axis=1)
    raw_data.set_index("Date", inplace=True)
    raw_data.drop(["High", "Low", "Adj Close**", "Volume"], axis=1, inplace=True)
    raw_data.sort_index(inplace=True)
    # creamos un dataframe vacío, donde guardaremos los datos de la empresa
    df = pandas.DataFrame(columns=["Date", "Growth", "Score"])
    # iteramos sobre las filas del dataframe raw_data
    for index, row in raw_data.iterrows():
        # buscamos las filas del dataframe de scores que se encuentren en la semana correspondiente a esta fila
        date_list = generate_date_list(index)
        score_list = list(news_data.loc[news_data["Date_Time"].isin(date_list)]["Score"])
        if len(score_list) == 0:
            score = 0
        else:
            score = mean(score_list)
            if score > 0:
                score = 1
            else:
                score = -1
        # adquirimos los datos
        growth = get_growth(row["Open"], row["Close*"])
        if growth > 0:
            growth = 1
        else:
            growth = -1
        df = df.append({"Date": index, "Growth": growth, "Score": score},
                       ignore_index=True)
    # guardamos los datos en el diccionario
    data_dict[file[:-4]] = df

# finalmente, guardamos los dataframes a csv
for key, value in data_dict.items():
    value.to_csv(os.path.join(path_final, key, ".csv"), index=False)