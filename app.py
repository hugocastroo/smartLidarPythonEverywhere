import os
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly
import random
import datetime
import time
from collections import deque
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#Headers for importing the information to googleDrive
gauth = GoogleAuth()           
drive = GoogleDrive(gauth)

refreshInterval = 1000
elementsLimits = 150

#Initializinh the variables for storing the signals from the Lidar
#Empty array of 10 arrays for the information slices
timestamps = []
tilt = [[] for i in range(10)]
roll = [[] for i in range(10)]
radialWS = [[] for i in range(10)]
verticalWV = [[] for i in range(10)]
recrotWS = [[] for i in range(10)]
turbulenceI = [[] for i in range(10)]
horWShub = [[] for i in range(10)]
windDirHH = [[] for i in range(10)]
verticalWS = [[] for i in range(10)]
horizontalWS = [[] for i in range(10)]
cnr = [[] for i in range(10)]

#Dictionary for the sifnals
data_signals = {'iTilt': tilt,
                'iRoll': roll,
                'iRWS': radialWS,
                'iVeer': verticalWV,
                'iRAWS': recrotWS,
                'iT': turbulenceI,
                'iHWShub': horWShub,
                'iDirectionHub': windDirHH,
                'iVsheer': verticalWS,
                'iHsheer': horizontalWS,
                'iCNR': cnr}
#Dictionary for the units
data_units = {'iTilt' : '[0.01 degree]',
              'iRoll' : '[0.01 degree]',
              'iRWS' : '[0.01 m/s]',
              'iVeer' : '[0.01 rad/m]',
              'iRAWS' : '[0.01 m/s]',
              'iT' : '[0.01]',
              'iHWShub' : '[0.01 m/s]',
              'iDirectionHub' : '[0.01 rad]',
              'iVsheer' : '[0.01]',
              'iHsheer' : '[0.01]',
              'iCNR' : '[]'}
#Array for the distances
data_distances = [50,60,75,90,105,120,140,160,180,190]

#Function to update(add) signals information to the variables
def update_signals(timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr):
    timestamps.append((time.time() *1000))
    #For the first time, get a random number for the signals
    if len(timestamps) == 1:
        #Fill the array slices with random data
        for i in range(10):
            tilt[i].append(random.randrange(15,20))
            roll[i].append(random.randrange(1,5))
            radialWS[i].append(random.randrange(-130,-120))
            verticalWV[i].append(random.randrange(1,3))
            recrotWS[i].append(random.randrange(-100,-90))
            turbulenceI[i].append(random.randrange(25,35))
            horWShub[i].append(random.randrange(120,150))
            windDirHH[i].append(random.randrange(-190,-170))
            verticalWS[i].append(random.randrange(400,450))
            horizontalWS[i].append(random.randrange(1,3))
            cnr[i].append(random.randrange(200,250))
    #Add random data that is a bit similar to the previous info
    else:
        for data_signals in [tilt, roll, radialWS, verticalWV, recrotWS, turbulenceI, horWShub, windDirHH, verticalWS, horizontalWS, cnr]:
            for k in range(10):
                data_signals[k].append(data_signals[k][-1]+data_signals[k][-1]*random.uniform(-0.01,0.01))

    #Fix the length of the variables to max 300 units
    for data_signals in [tilt, roll, radialWS, verticalWV, recrotWS, turbulenceI, horWShub, windDirHH, verticalWS, horizontalWS, cnr,]:
        for j in range(10):
            data_signals[j] = data_signals[j][-elementsLimits:]

    return timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr

#Call the function and generate the data
timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr = update_signals(timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr)

#Stylesheet for the dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Not sure for what it is
server = app.server

#Layout for the page. Title, Dropdown, Graph and Interval info
app.layout = html.Div([
    html.H1('Interactive Data Acquisition System',),
    dcc.Dropdown(
        id='signalName',
        options=[{'label': i, 'value': i} for i in data_signals.keys()],
        value='iHWShub',
	multi=False),
    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(id='graph-update',interval=refreshInterval,n_intervals=0),
    dcc.Checklist(id="liveUpdate",
    options=[
        {'label': 'Live', 'value': "on"}
    ],
    value=["on"],
    labelStyle={'display': 'inline-block'}
)] )

#Callback for the graph, takes the intervals and the signal name as in input
#and plots the graph according to the requested signal
@app.callback(Output('live-graph', 'figure'),
             [Input('graph-update', 'n_intervals'),
              Input('signalName','value'),
              Input("liveUpdate","value")])

def update_graph_scatter(n,signal_name,state):
    #Commands for calling the google drive and storing the file
    #xx = drive.ListFile({'q': "'1Bz1vycp82bOQxKUfvE8uKvefaMIjFKAw' in parents and trashed=false"}).GetList()
    #testID = xx[0]["id"]
    #fileTest = drive.CreateFile({"id":testID})
    #print(fileTest.GetContentString()[-32:-28])
    #print((fileTest.GetContentString()[-16:-11]).replace(":","."))
    #Y.append(float(fileTest.GetContentString()[-32:-28]))
    #X.append(X[-1]+1)
    #Y.append(Y[-1] + Y[-1]*random.uniform(-0.01,0.01))
    #Update the signals information
    update_signals(timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr)

    if(len(state) == 0):
        return null
    else:
        #Create the graphs for the 10 different signals
        datax = [0 for i in range(10)]
        for i in range(10):
            datax[i] =  plotly.graph_objs.Scatter(
                        #Signal-Information to plot in the X axis
                        x=list(timestamps[-elementsLimits:]),
                        #Signal-Information to plot in the Y axis
                        y=list(data_signals[signal_name][i]),
                        #Name for the signal-points when hovering over the points
                        name= signal_name + " " + str(data_distances[i]) + " meters",
                        mode= 'lines+markers',
                        #Activates the legend in the screen and the description to the legend
                        showlegend = True,
                        text = signal_name + " " + str(data_distances[i]) + " meters",
                        
                        )
            
        #Return the ten different graphs with the adjust-setting for the graph, title etc.
        return {'data': [datax[0],datax[1],datax[2],datax[3],datax[4],datax[5],datax[6],datax[7],datax[8],datax[9]],
                'layout' : go.Layout(
                                    #Axisx adjust just according to the last 200 values, after 200 values they start going
                                    #out of the view
                                    #xaxis=dict(range=[min(timestamps[-20:]),max(timestamps[-20:])]),
                                    #If yaxis is not declared, then the axis adjusts automatically
                                    #yaxis=dict(range=[min(data_signals[signal_name])-0.5,((max(data_signals[signal_name])+20)/2)+0.5]),
                                    title = {
                                        'text': "Live " + signal_name,
                                        'x':0.45,
                                        'xanchor': 'center',
                                        'yanchor': 'top'},
                                    font=dict(
                                        family="Courier New, monospace",
                                        size=18,
                                        color="RebeccaPurple"),
                                    xaxis_title = "time",
                                    yaxis_title = str(signal_name + data_units[signal_name]) ,
                                    #Size for the graph, if not specified it is actually to small,
                                    #the width adjusted aumatically now, but the height is set to 800, because if not
                                    #the graph is to small in the Y axis
                                    height = 800,
                                    #width = 1900,
                                    #Margins for good visualisation of the texts
                                    margin={'l':100,'r':1,'t':100,'b':50},
                                    xaxis = dict(range=[min(timestamps[-30:]),max(timestamps[-30:])],
                                                 rangeselector = dict(buttons=list([
                                                                    dict(count=30,
                                                                         label="30s",
                                                                         step="second",
                                                                         stepmode="backward"),
                                                                    dict(count=60,
                                                                         label="60s",
                                                                         step="second",
                                                                         stepmode="backward"),
                                                                    dict(count=120,
                                                                         label="120s",
                                                                         step="second",
                                                                         stepmode="todate")])),
                                    rangeslider=dict(autorange=True,
                                                     visible=True,
                                                     range=[min(timestamps[-elementsLimits:]),max(timestamps[-elementsLimits:])]),
                                    type = "date"
                                    ))
                }

if __name__ == '__main__':
    app.run_server(debug=False)
