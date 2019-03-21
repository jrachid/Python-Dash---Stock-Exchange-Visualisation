import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go 
import pandas as pd 
import pandas_datareader.data as web
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
import requests
import pytz
import json
import functions


# List of Stocks tickers
nsdq = pd.read_csv('nasdaqList.csv')
nsdq.set_index('Symbol', inplace=True)
options = [{'label': str(nsdq.loc[ticker]['Name']) +' '+ ticker, 'value': ticker} for ticker in nsdq.index]

# List of Crypto tickers
with open('cryptoList.json', 'r') as f:
    cryptoList = json.load(f)
options_crypto = [{'label':key + ' ' + value, 'value': key} for key, value in cryptoList.items()]

# Creating an instance of Dash
app = dash.Dash()
app.scripts.config.serve_locally=True

# Define the Layout
app.layout = html.Div([
    # Multi TABS
    dcc.Tabs(id='tabs', value='tab-1', children=[
        # Beginning First TAB -- Stocks IEX
        dcc.Tab(label='Stocks IEX', children=[
            html.Div([
                html.H1('Stock Ticker Dashboard'),

                html.Div([
                    html.H3('Enter a stock symbol:', style={'paddingRight':'30%'}),
                    dcc.Dropdown(id='my_stock_picker',
                                options = options,
                                value=['TSLA'],
                                multi=True,
                                style={'height':50, 'width': 500}),
                ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '50%'}),

                html.Div([
                    html.H3('Select a start and end date: '),
                    dcc.DatePickerRange(id='my_date_picker',
                                        min_date_allowed=datetime.today()-relativedelta(years=5),
                                        max_date_allowed=datetime.today(),
                                        start_date = datetime(2018, 1, 1),
                                        end_date = datetime.today())
                ], style={'display' :'inline-block'}),

                html.Div([
                    html.Button(id='submit-button',
                                n_clicks=0,
                                children='Submit',
                                style={'fontSize': 24, 'marginLeft': '30px'})
                ], style={'display':'inline-block'}),

                dcc.Graph(id='my_graph',
                                figure= go.Figure({'data': [{'x': [1,2], 'y':[3,1]}],
                                        'layout': {'title': 'Default Title'}}))
            ], style={'width':'70%', 'float': 'left'}),
            html.Div([
                html.H3('Top 20'),
                dash_table.DataTable(
                    id='table_stocks',
                    columns = [{"name": i, "id": i} for i in ['ticker','open','high','low','close','volume']]
                )
            ], style={'border': '1px solid grey', 'float': 'left'})
        ]), # END of FIRST TAB
        # Beginning of Second TAB
        dcc.Tab(label='Cryptocurrencies', children=[
            html.Div([
                html.H1('Cryptocurrencies Dashboard'),
                html.Div([
                    html.H3('Enter a crypto symbol:', style={'paddingRight':'30%'}),
                    dcc.Dropdown(id='my_crypto_picker',
                                options = options_crypto,
                                value=['BTC'],
                                multi=True),
                ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '30%'}),

                html.Div([
                    html.Button(id='submit-button-crypto',
                                n_clicks=0,
                                children='Submit',
                                style={'fontSize': 24, 'marginLeft': '30px'})
                ], style={'display':'inline-block', 'verticalAlign': 'bottom'}),

                dcc.Graph(id='my_graph_crypto',
                            figure= go.Figure({'data': [{'x': [1,2], 'y':[3,1]}],
                                                'layout': {'title': 'Default Title'}}))
            ])
        ]) # END of Second TAB
    ])
])


@app.callback(Output('my_graph', 'figure'), 
                [Input('submit-button','n_clicks')],
                [State('my_stock_picker', 'value'),
                State('my_date_picker','start_date'),
                State('my_date_picker','end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    # Use datareader and datetime to define a DataFrame
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')

    traces = []
    for ticker in stock_ticker:
        df = web.DataReader(ticker,'iex',start,end)
        traces.append({'x': df.index, 'y': df['close'], 'name': ticker})

    fig = {'data': traces,
            'layout': {'title': stock_ticker}}

    return fig 

@app.callback(Output('table_stocks', 'data'),
                [Input('my_date_picker','start_date'),
                Input('my_date_picker','end_date')])
def table_stocks(start_date, end_date):
    start = datetime.today()-relativedelta(days=5)
    end = datetime.today()

    # Display table of top50
    top20 = ['MSFT', 'AAPL', 'AMZN', 'GOOGL', 'GOOG', 'FB', 'INTC', 'CSCO', 'CMCSA', 'PEP',
            'NFLX', 'ADBE', 'AMGN', 'PYPL', 'AVGO', 'TXN', 'NVDA', 'COST', 'FOXA', 'FOX', ]

    df_total = pd.DataFrame(columns= ['ticker','open','high','low','close','volume'])
    
    for top in top20:
        df = web.DataReader(top,'iex',start,end)
        df_total = df_total.append(df.iloc[-1])
        
    df_total['ticker'] = np.asarray(top20)    
    data = df_total.to_dict("rows")
    return data


@app.callback(Output('my_graph_crypto', 'figure'), 
                [Input('submit-button-crypto','n_clicks')],
                [State('my_crypto_picker', 'value')])
def update_graph_crypto(n_clicks, crypto_ticker):
    
    # API Key for cryptocompare
    api_key = '6057480ec6d0b562e585d33b11e5d74834c7488b42c81f61aec010523f3031ff'
    currency = 'USD'
    traces = []
    for ticker in crypto_ticker:
        url = "https://min-api.cryptocompare.com/data/histoday"
        payload={
            "api_key": api_key,
            'fsym': ticker,
            'tsym': currency,
            'limit': 100
        }
        result = requests.get(url, params=payload).json()
        df = pd.DataFrame(result['Data'])
        print(df.head())
        print(df.tail())
        traces.append({'x': df.index, 'y': df['close'], 'name': ticker})

    fig = {'data': traces,
            'layout': {'title': crypto_ticker}}

    return fig 

if __name__ == "__main__":
    app.run_server()