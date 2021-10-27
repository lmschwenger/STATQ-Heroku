from datetime import datetime
import numpy as np
import base64
import plotly
import json
import plotly.express as px
import plotly.graph_objects as go   
import pandas as pd

def parse_data(file_path):
    
    try:
        df = pd.read_csv(file_path, encoding = "ISO-8859-1", decimal=',',
                         delimiter=";")
        DateName = 'Dato'
        try:
            df[DateName] = pd.to_datetime(df[DateName], format='%Y%m%d')
        except ValueError:
            return 'Filen kan ikke læses (Fejlkode 1)'
    except KeyError:
        df = pd.read_csv(file_path, encoding = "ISO-8859-1", decimal=',',
                         delimiter=";")
        DateName = 'Startdato'
        try:
            df[DateName] = pd.to_datetime(df[DateName], format='%Y%m%d')
        except ValueError:
            return 'Filen kan ikke læses (Fejlkode 1)'
    try:
        df.dropna(subset=['Resultat'], how='all', inplace=True)
        df.dropna(subset=[DateName], how='all', inplace=True)
        df['Parameter'].to_string()    
        df['Resultat'] = pd.to_numeric(df['Resultat'])
    except KeyError:
        return 'Filen kan ikke læses (Fejlkode 2)'
    except ValueError:
        return 'Filen kan ikke læses (Fejlkode 1)'
    if df.empty:
        return 'Filen kan ikke læses (Fejlkode 0)'
    df.set_index(DateName, inplace=True)
    df.sort_index(inplace=True)
    return df

def plotly_hydro(df):

    Enhed = str(df['Parameter'].iloc[0]) + ', ' + str(df['Enhed'].iloc[0])
    if str(df['Parameter'].iloc[0]) == 'Vandstand':
        symbol = 'Kotesystem'
    else:
        symbol = 'Enhed'

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Resultat'], name=df['Parameter'][0], connectgaps=False,
        mode = 'lines'))

    # fig = px.line(df, y='Resultat', color='Parameter',
    #     title=df['ObservationsStedNavn'].iloc[0],
    #     labels=dict(Resultat=Enhed)
    #     )
    aarsmiddel = df['Resultat'].resample('Y').mean()
    fig.add_trace(go.Scatter(x=aarsmiddel.index, y=aarsmiddel, line={'color':'rgba(0,0,0,1)'}, name="Årsmiddel",
        mode='lines+markers',
        marker=dict( color='black', size=8, line= dict( color='black', width=2 ))))
    fig.update_xaxes(title_text="")
    fig.update_layout(autosize=True)
    fig.data = (fig.data[1],fig.data[0])
    # fig.update_traces(marker=dict(size=10, opacity=0.75,
    #                               line=dict(width=1.5, color='black')))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def plotly_kemi(df):
    df['Parameter'] = df['Parameter'] + ' [' + df['Enhed'] + ']'
    fig = px.scatter(df, y='Resultat', color='Parameter', 
        title=df['ObservationsStedNavn'].iloc[0],
        labels={'Parameter'+'Enhed'}
        )
    fig.update_layout(autosize=True)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Værdi")
    #fig.update_layout(barmode='group')
    fig.update_traces(marker=dict(size=8, opacity=0.85,
                                  line=dict(width=0.4, color='black')))
    #fig.data[0].update(mode='markers+lines')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
def plotly_season(df):

    yearly_mean = df['Resultat'].resample('Y').mean()
    monthly = df['Resultat'].resample('M').mean()

    sommer = (df.index.month > 4) & (df.index.month < 10)
    vinter = (df.index.month < 4) + (df.index.month > 10)

    seasonal_s = df.loc[sommer, 'Resultat'].resample('Y').mean()
    seasonal_w = df.loc[vinter, 'Resultat'].resample('Y').mean()
    x_s = np.arange(0,len(seasonal_s),1)
    x_w = np.arange(0,len(seasonal_w),1)
    y_reg1 =[]
    y_reg2 = []
    if len(seasonal_s) > 1:
        mk1 = mk_test(seasonal_s)
        p1 = normdist_p(mk1, 2)
        if p1 < 0.05:
            trend1 = 'Signifikant'
        elif p1 > 0.05:
            trend1 = 'Ikke signifikant'
        a1,b1 = np.polyfit(np.arange(0,len(seasonal_s),1), seasonal_s, 1)
        y_reg1 = np.linspace(b1, (b1+a1*x_s[-1]), len(x_s))
    if len(seasonal_w) > 1:
        mk2 = mk_test(seasonal_w)
        p2 = normdist_p(mk2, 2)
        if p2 < 0.05:
            trend2 = 'Signifikant'
        elif p2 > 0.05:
            trend2 = 'Ikke signfikant'
        a2,b2 = np.polyfit(x_w, seasonal_w, 1)
        y_reg2 = np.linspace(b2, (b2+a2*x_w[-1]), len(x_w))


    monthly = df['Resultat'].resample('M').mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=seasonal_s.index, y=seasonal_s, name='Sommer', 
        mode='lines+markers',
        marker=dict( color='red', size=8, line= dict( color='black', width=2 ) ),
        line=dict( color='black' )
            )
        )
    if y_reg1 != []:
        fig.add_trace(go.Scatter(x=seasonal_s.index, y=y_reg1, 
            name = 'Trend',
            mode='lines',
            line = dict(dash='dash', color='red', width=1)
                )
            )
    fig.add_trace(go.Scatter(x=seasonal_w.index, y=seasonal_w, name='Vinter', 
        mode='lines+markers',
        marker_symbol = 'diamond',
        marker=dict( color='blue', size=7, line= dict( color='black', width=2 ) ),
        line=dict( color='black' )
            )
        )
    if y_reg2 != []:
        fig.add_trace(go.Scatter(x=seasonal_w.index, y=y_reg2, 
            name = 'Trend',
            mode='lines',
            line = dict(dash='dash', color='blue', width=1)
                )
            )
    fig.update_xaxes(title_text="")
    fig.update_layout(autosize=True, title=df['ObservationsStedNavn'].iloc[0])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def mk_test(data):
    data = list(data)
    sign_i = [];
    signs=[]
    n=len(data)
    possibilites=(n*(n-1))/2
    slopes=[]
    for i in range(0,n):
        x_i = data[i]
        for j in range(0,i):
            if x_i-data[j] > 0:
                sign=1
            elif x_i-data[j] == 0:
                sign=0
            elif x_i-data[j] < 0:
                sign=-1
            sign_i.append(sign)
            slopes.append((x_i-data[j])/(i-j))
        signs.append(sign_i)
        sign_i=[]
        
    sum_line=[]
    for i in range(0,len(signs)):
        sum_line.append(sum(signs[i]))
        
        
    
    S = sum(sum_line)
    
    tau = S/(n*(n-1)/2)
    frequencies=[]
    tp=[]
    groups = []
    for i in range(0,len(data)):
        test_val=data[i]
        if test_val not in groups:
            frequencies.append(data.count(test_val))
            tp.append(frequencies[-1]*(frequencies[-1]-1)*(2*frequencies[-1]+5))
            groups.append(test_val)
    
    var = (1/18)*((n*(n-1)/2)*(2*n+5)-sum(tp))
    se = pow(var,0.5)
    if S>0:
        Z_MK=(S-1)/se
    elif S<0:
        Z_MK=(S+1)/se
    elif S==0:
        Z_MK = 0
    return Z_MK


def normdist_p(val,tailed):
    from math import erf
    pi=3.141592
    cdf = 0.5*(1+erf(val/pow(2,.5)))
    if tailed==0:  
        return cdf
    elif tailed==1:
        return 1-cdf
    elif tailed==2:
        return 2*min(cdf,1-cdf)