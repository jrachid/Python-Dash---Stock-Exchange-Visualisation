COLORS = [
    {
        'background': '#8ef995',
        'text': 'rgb(30, 30, 30)'
    },
    {
        'background': '#bf0345',
        'text': 'rgb(30, 30, 30)'
    }
]

def cell_style(current_value, previous_value):
    style = {}
    if current_value >= previous_value:
        style = {
            'backgroundColor': COLORS[0]['background'],
            'color': COLORS[0]['text']
        }
    else:
        style = {
            'backgroundColor': COLORS[1]['background'],
            'color': COLORS[1]['text']
        }
    return style


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
    return dash_table.DataTable(
                    id='table_stocks',
                    columns = [{"name": i, "id": i} for i in ['ticker','open','high','low','close','volume']]
                )