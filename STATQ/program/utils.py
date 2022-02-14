from datetime import datetime
import numpy as np
import base64
import plotly
import json
import plotly.express as px
import plotly.graph_objects as go   
import pandas as pd
from pandas.errors import EmptyDataError
def parse_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding = "ISO-8859-1", decimal=',', delimiter=";")
    except EmptyDataError:
        return 'Fejlkode 0: Filen ser ud til at være tom'
    if '�r' in df.columns or 'År' in df.columns:
        resampler = parse_data2(df)
        return resampler
    if 'Dato' in list(df.columns):
        DateName = 'Dato'
    elif 'Startdato' in list(df.columns):
        DateName = 'Startdato'            
    try:
        df[DateName] = pd.to_datetime(df[DateName], format='%Y%m%d')
    except ValueError:
        return 'Fejlkode 1: Forkert dato-format (se FAQ)'
    try:
        df.dropna(subset=['Resultat'], how='all', inplace=True)
        df.dropna(subset=[DateName], how='all', inplace=True)
        df['Parameter'].to_string()    
        df['Resultat'] = pd.to_numeric(df['Resultat'])
    except KeyError:
        return 'Fejlkode 2: Filen kan ikke læses (se FAQ)'
    except ValueError:
        return 'Fejlkode 1: Forkert dato-format (se FAQ)'
    if df.empty:
        return 'Fejlkode 0: Filen ser ud til at være tom'
    df.set_index(DateName, inplace=True)
    df.sort_index(inplace=True)
    return df
def parse_databasedata(file_path):
    try:
        df = pd.read_csv(file_path, encoding = "utf-8", decimal='.', delimiter=",")
    except EmptyDataError:
        return 'Fejlkode 0: Filen ser ud til at være tom'
    if '�r' in df.columns or 'År' in df.columns:
        resampler = parse_data2(df)
        return resampler
    if 'Dato' in list(df.columns):
        DateName = 'Dato'
    elif 'Startdato' in list(df.columns):
        DateName = 'Startdato'            
    try:
        df[DateName] = pd.to_datetime(df[DateName], format='%Y%m%d')
    except ValueError:
        return 'Fejlkode 1: Forkert dato-format (se FAQ)'
    try:
        df.dropna(subset=['Resultat'], how='all', inplace=True)
        df.dropna(subset=[DateName], how='all', inplace=True)
        df['Parameter'].to_string()    
        df['Resultat'] = pd.to_numeric(df['Resultat'])
    except KeyError:
        return 'Fejlkode 2: Filen kan ikke læses (se FAQ)'
    except ValueError:
        return 'Fejlkode 1: Forkert dato-format (se FAQ)'
    if df.empty:
        return 'Fejlkode 0: Filen ser ud til at være tom'
    df.set_index(DateName, inplace=True)
    df.sort_index(inplace=True)
    return df

def parse_data2(df):
    if '�r' in df.columns:
        col_year = '�r'
    elif 'År' in df.columns:
        col_year = 'År'
    else:
        print('Du har formentlig glemt at omdøbe kolonne-navne: De må ikke indeholde æ, ø og å')
    if 'M�ned' in df.columns:
        col_maaned = 'M�ned'
    elif 'Måned' in df.columns:
        col_maaned = 'Måned'
    else:
        print('Du har formentlig glemt at omdøbe kolonne-navne: De må ikke indeholde æ, ø og å')

    resampler = []; values = []
    years = list( set(df[col_year]) )
    n = 0
    for i in range(0,len(df)):
        if df[col_year][i] == years[n]:
            values.append({'aar':df[col_year][i], 'Maaned': df[col_maaned][i], 'resultat': df['Resultat'][i]})
        if df[col_year][i] != years[n] or i == len(df)-1:
            n_maaneder = len([x['Maaned'] for x in values])
            if n_maaneder < 12:
                advarsel = print('OBS: Målinger eksisterer ikke for alle måneder i ' + str(values[0][col_year]))
            else:
                advarsel = ''
            summations = {'aar': df[col_year][i-1], 'n_maaneder': n_maaneder, 'middel':np.mean([x['resultat'] for x in values]), 'samlet':sum([x['resultat'] for x in values]), 'advarsel': advarsel, 'parameter':df['Parameter'][i-1], 'enhed': df['Enhed'][i-1]}
            
            resampler.append([values,summations])
            values = []
            summations = []
            values.append({'aar':df[col_year][i], 'Maaned': df[col_maaned][i], 'resultat': df['Resultat'][i]})
            n+=1
    return resampler

def plotly_hydro(df):
    Enhed = str(df['Parameter'].iloc[0]) + ', ' + str(df['Enhed'].iloc[0])
    if str(df['Parameter'].iloc[0]) == 'Vandstand':
        symbol = 'Kotesystem'
    else:
        symbol = 'Enhed'

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Resultat'], name=df['Parameter'][0] + ' [' + df['Enhed'][0]+']', connectgaps=False,
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
    if 'ObservationsStedNavn' in list(df.columns):
        if len(set(df['ObservationsStedNavn'])) > 1 and 'Lokalitetsnavn' in list(df.columns):
            fig.update_layout(autosize=True, title=df['Lokalitetsnavn'].iloc[0])  
    else:
        fig.update_layout(autosize=True, title='Målestation(er): '+ str(set(df['ObservationsStedNr'])).strip("'{}'"))
    fig.data = (fig.data[1],fig.data[0])
    if str(df['Parameter'].iloc[0]) == 'Vandstand':
        fig.update_yaxes(title_text=df['Enhed'][0] + ' ' + df['Kotesystem'][0])
    elif str(df['Parameter'].iloc[0]) == 'Vandføring':
        fig.update_yaxes(title_text=df['Enhed'][0])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def plotly_kemi(df):
    df['Parameter'] = df['Parameter'] + ' [' + df['Enhed'] + ']'
    if 'ObservationsStedNavn' in list(df.columns):
        fig = px.scatter(df, y='Resultat', color='Parameter', symbol='ObservationsStedNavn',
            labels={'Parameter'+'Enhed'}
            )
        fig.update_layout(autosize=True, title=str(set(df['ObservationsStedNavn'])).strip("'{}'"))
    else:
        fig = px.scatter(df, y='Resultat', color='Parameter', symbol='ObservationsStedNr',
            labels={'Parameter'+'Enhed' + ' (st. ' + 'ObservationsStedNr' + ')'}
            )
        fig.update_layout(autosize=True, title='Målestation(er): ' + str(set(df['ObservationsStedNr'])).strip("'{}'"))
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Værdi")
    #fig.update_layout(barmode='group')
    fig.update_traces(marker=dict(size=10, opacity=0.85,
                                  line=dict(width=0.4, color='black')))
    fig.update_layout(legend_title="", legend=dict(
        orientation="h",
        font = dict(size=14)

    ))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def plotly_season(df):
    sommer = (df.index.month > 4) & (df.index.month < 10)
    vinter = (df.index.month < 4) + (df.index.month > 10)
    seasonal_s = df.loc[sommer, 'Resultat'].resample('Y').mean()
    seasonal_w = df.loc[vinter, 'Resultat'].resample('Y').mean()
    x_s = np.arange(0,len(seasonal_s),1)
    x_w = np.arange(0,len(seasonal_w),1)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=seasonal_s.index, y=seasonal_s, name=df['Parameter'][0] + ' (Sommermiddel)', 
        mode='lines+markers',
        marker=dict( color='red', size=8, line= dict( color='black', width=2 ) ),
        line=dict( color='black' )
            )
        )
    fig.add_trace(go.Scatter(x=seasonal_w.index, y=seasonal_w, name=df['Parameter'][0] + ' (Vintermiddel)', 
        mode='lines+markers',
        marker_symbol = 'diamond',
        marker=dict( color='blue', size=7, line= dict( color='black', width=2 ) ),
        line=dict( color='black' )
            )
        )
    if 'ObservationsStedNavn' in list(df.columns):
        fig.update_layout(autosize=True, title=str(set(df['ObservationsStedNavn'])).strip("'{}'"))
    else:
        fig.update_layout(autosize=True, title='Målestationer(er): ' + str(set(df['ObservationsStedNr'])).strip("'{}'"))
    
    if str(df['Parameter'].iloc[0]) == 'Vandstand':
        fig.update_yaxes(title_text=df['Enhed'][0] + ' ' + df['Kotesystem'][0])
    elif str(df['Parameter'].loc[0] == 'Vandføring'):
        fig.update_yaxes(title_text=df['Enhed'][0])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def plotly_stoftransport(resampler):

    years = [x[1]['aar'] for x in resampler]
    y_obs = [x[1]['samlet'] for x in resampler]
    a, b = np.polyfit(years, y_obs, 1)
    y_reg = [a * x + b for x in years]
    r2 = r_squared(y_obs, y_reg)
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=years, y=y_obs, name=resampler[0][1]['parameter'], 
        mode='lines+markers',
        marker=dict( color='red', size=8, line= dict( color='black', width=2 ) ),
        line=dict( color='black' )
            )
        )
    fig.add_trace(go.Scatter(x=years, y=y_reg, name = 'Regression (' + str(round(a, 2)) + ', $R^2$ = ' + str(round(r2, 2)),
        line=dict( color='red', dash='dash' )
            )
        )
    fig.update_layout(autosize=True, title='Stoftransport')
    fig.update_yaxes(title_text=resampler[0][1]['enhed'])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def plotly_bar(df):
    col_name = 'Resultat'
    yearly_max = df[col_name].resample('Y').max()
    yearly_max.dropna(how='all', inplace=True)
    yearly_avg = df[col_name].mean()
    yearly_avg.dropna(how='all', inplace=True)
    yearly_min = df[col_name].resample('Y').min()
    yearly_min.dropna(how='all', inplace=True)

    median_maks = np.median(yearly_max)        
    median = np.median(df[col_name])
    median_min = np.median(yearly_min)
    
    
    vinter = (df.index.month < 4) + (df.index.month > 10)    
    sommer = (df.index.month > 4) & (df.index.month < 10)  
    vinter_avg = np.mean(df.loc[vinter, col_name].resample('Y').mean())
    sommer_avg = np.mean(df.loc[sommer, col_name].resample('Y').mean())
    
    output = dict({'Medianmaksimum': median_maks,
                   'Medianminimum': median_min, 
                   'Median' : median,
                   'Årsmiddel' : yearly_avg,
                   'Vintermiddel': vinter_avg,
                   'Sommermiddel': sommer_avg})
    print(output)
    output_items = output.items()
    output_list = list(output_items)
    output_df = pd.DataFrame(output_list, columns = ['Parameter', 'Value'])
    periode = 'Periode: %d - %d' % (min(df.index.year), max(df.index.year))

    fig = px.bar(output_df, x = 'Parameter', y = 'Value', labels = {'Value': str(df['Enhed'][0])})
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

def r_squared(y_obs, y_reg):
    import numpy as np
    residuals = []
    mean_observed = np.mean(y_obs)
    if len(y_obs) != len(y_reg):
        return 'Vektorene er ikke samme længde'
    else:
        for i in range(0,len(y_obs)):
            residuals.append(pow(y_obs[i] - y_reg[i], 2))
        SS_res = sum(residuals)
        SS_tot = sum([(y - mean_observed)**2 for y in y_obs])
    return 1 - (SS_res/SS_tot)

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