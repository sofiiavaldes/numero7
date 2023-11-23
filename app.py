import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

import datetime
import numpy as np
import pandas as pd
import yfinance as yf


stocks_max_sharpe = ["MSFT", "NSRGY", "PEP", "TSLA"]
stocks_min_volatility = ["MSFT", "NSRGY", "PEP", "TSLA"]

# Definir fechas de observación
end_max_sharpe = datetime.datetime.now()
start_max_sharpe = end_max_sharpe - datetime.timedelta(days=365 * 3)

end_min_volatility = datetime.datetime.now()
start_min_volatility = end_min_volatility - datetime.timedelta(days=365 * 3)

# Cargar datos con ticker 
data_max_sharpe = yf.download(stocks_max_sharpe, start=start_max_sharpe, end=end_max_sharpe)["Adj Close"]
data_min_volatility = yf.download(stocks_min_volatility, start=start_min_volatility, end=end_min_volatility)["Adj Close"]

# Calcular retornos %
returns_max_sharpe = data_max_sharpe.pct_change()
returns_min_volatility = data_min_volatility.pct_change()

# Retorno medio por acción
retorno_medio_max_sharpe = returns_max_sharpe.mean()
retorno_medio_min_volatility = returns_min_volatility.mean()

# Pesos de portafolio max sharpe
pesos_max_sharpe = np.array([0.7361831214637042, 0.0, 0.2638168785362957, 0.0])
retorno_port_max_sharpe = np.sum(retorno_medio_max_sharpe * pesos_max_sharpe)

# Pesos de portafolio min volatilidad
pesos_min_volatility = np.array([0.0534595668525922, 0.4243250904290558, 0.5199242020802015, 0.0022911406381505])
retorno_port_min_volatility = np.sum(retorno_medio_min_volatility * pesos_min_volatility)

# Retorno acumulado por acción a cada una de las fechas
returns_max_sharpe["Portafolio_max_sharpe"] = returns_max_sharpe.dot(pesos_max_sharpe)
returns_min_volatility["Portafolio_min_volatility"] = returns_min_volatility.dot(pesos_min_volatility)

# Calcular acumulado
ret_acumulado_max_sharpe = (1 + returns_max_sharpe).cumprod()
ret_acumulado_min_volatility = (1 + returns_min_volatility).cumprod()

# Inicializar la aplicación Dash
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

# Layout de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Distribución de Retornos de Portafolios'),

    html.Div(children='''
        Análisis de los retornos acumulados en los últimos 3 años.
    '''),

    # Gráfico 1: Retorno acumulado portafolio max sharpe
    dcc.Graph(
        id='graph1',
        figure=px.line(ret_acumulado_max_sharpe, x=ret_acumulado_max_sharpe.index,
                       y=["MSFT", "NSRGY", "PEP", "TSLA", "Portafolio_max_sharpe"],
                       line_shape="linear", title="Retorno acumulado - Portafolio Max Sharpe")
    ),

    # Gráfico 2: Retorno acumulado portafolio min volatilidad
    dcc.Graph(
        id='graph2',
        figure=px.line(ret_acumulado_min_volatility, x=ret_acumulado_min_volatility.index,
                       y=["MSFT", "NSRGY", "PEP", "TSLA", "Portafolio_min_volatility"],
                       line_shape="linear", title="Retorno acumulado - Portafolio Min Volatilidad")
    )
])

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0',port=10000)
