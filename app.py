from dash.dependencies import Output, Input
from collections import deque
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from struct import *
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly
import random
import datetime
import time
import os
import dash
import math

#Authorization Headers for importing the information to/from googleDrive
gauth = GoogleAuth()           
drive = GoogleDrive(gauth)

#Timeinterval for getting the information and refreshing the graph in ms
refreshInterval = 10000
#elements to avoid overloading the buffer and getting the system slow
elementsLimits = 120

#Initializing the variables for storing the signals from the Lidar
#Empty array of 10 arrays for the information slices
timestamps = []
tilt = [] #they are not slices, and have just one signal
roll = [] #they are not slices, and have just one signal
radialWS = [[] for i in range(10)]
verticalWV = [[] for i in range(10)]
recrotWS = [[] for i in range(10)]
turbulenceI = [[] for i in range(10)]
horWShub = [[] for i in range(10)]
windDirHH = [[] for i in range(10)]
verticalWS = [[] for i in range(10)]
horizontalWS = [[] for i in range(10)]
cnr = [[] for i in range(10)]
data_distancesTest = [None] * 10

#Dictionary for the sifnals
data_signals = {'Tilt': tilt,
                'Roll': roll,
                'RWS': radialWS,
                'Veer': verticalWV,
                'RAWS': recrotWS,
                'TI': turbulenceI,
                'HWShub': horWShub,
                'DirectionHub': windDirHH,
                'Vsheer': verticalWS,
                'Hsheer': horizontalWS,
                'CNR': cnr}
#Dictionary for the units
data_units = {'Tilt' : '[degrees]',
              'Roll' : '[degrees]',
              'RWS' : '[m/s]',
              'Veer' : '[rad/m]',
              'RAWS' : '[m/s]',
              'TI' : '[-]',
              'HWShub' : '[m/s]',
              'DirectionHub' : '[rad]',
              'Vsheer' : '[-]',
              'Hsheer' : '[-]',
              'CNR' : '[dB]'}

def select_signal(signal):
    if(signal in ["Tilt","Roll"]):
        return(True)
    else:
        return (False)
    

#Function to update(add) signals information to the variables
def update_signals(timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr):
    timestamps.append((time.time() *1000))
######################################################################GENERATING RANDOM DATA IN CASE THAT THE LIDAR IS NOT USED; JUST FOR TEST#########################################################################
##    #For the first time, get a random number for the signals
##    if len(timestamps) == 1:
##        #Fill the array slices with random data
##        for i in range(10):
##            tilt[i].append(random.randrange(15,20))
##            roll[i].append(random.randrange(1,5))
##            radialWS[i].append(random.randrange(-130,-120))
##            verticalWV[i].append(random.randrange(1,3))
##            recrotWS[i].append(random.randrange(-100,-90))
##            turbulenceI[i].append(random.randrange(25,35))
##            horWShub[i].append(random.randrange(120,150))
##            windDirHH[i].append(random.randrange(-190,-170))
##            verticalWS[i].append(random.randrange(400,450))
##            horizontalWS[i].append(random.randrange(1,3))
##            cnr[i].append(random.randrange(200,250))
##    #Add random data that is a bit similar to the previous info
##    else:
##        for data_signals in [tilt, roll, radialWS, verticalWV, recrotWS, turbulenceI, horWShub, windDirHH, verticalWS, horizontalWS, cnr]:
##            for k in range(10):
##                data_signals[k].append(data_signals[k][-1]+data_signals[k][-1]*random.uniform(-0.01,0.01))
##
##    #Fix the length of the variables to max 300 units
##    for data_signals in [tilt, roll, radialWS, verticalWV, recrotWS, turbulenceI, horWShub, windDirHH, verticalWS, horizontalWS, cnr,]:
##        for j in range(10):
##            data_signals[j] = data_signals[j][-elementsLimits:]

    ################################Updating the signals from GoogleDrive########################################
    #Getting the structure data from Google Drive
    x = drive.ListFile({'q': "'1Bz1vycp82bOQxKUfvE8uKvefaMIjFKAw' in parents and trashed=false"}).GetList()
##    print(len(x))
    testID = x[0]["id"]
    fileTest = drive.CreateFile({"id":testID})
    test = (fileTest.GetContentString(encoding='ANSI')[-225:])
    info = bytearray(test,encoding='ANSI')
#####################################Getting the data from a file in the PC##############################################
####    info = bytearray(b'')
####    with open("c:\\Users\\huggo\\source\\repos\\MolasDLLDemo1-1\\MolasDLLDemo1-1\\bin\\Debug\\netcoreapp3.1\\csvexample.txt", "rb") as f:
####        byte = f.read(1)
####        #While the file is not empty, keep reading the bytes and append them to the info bytearray
####        while byte != b"":
####            # Do stuff with byte.
####            info += byte
####            byte = f.read(1)
####    info = info[-225:]
########################################################INTERPRETING THE INFORMATION########################################################
    #Interpreting the structure into the signals
    iD = [None] * 10
    iRWS = [None] * 10
    iVeer = [None] * 10
    iRAWS = [None] * 10
    iT = [None] * 10
    iHWShub = [None] * 10
    iDirectionHub = [None] * 10
    iVsheer = [None] * 10
    iHsheer = [None] * 10
    iCNR = [None] * 10

    #unpack the info byte array in the different variables
##  reference to object 0 because it is a tuple and it is needed to get the object 0
##  In case that it is needed to convert the units then divide over 100 or 10 depending on the units change
    lidarID = unpack('H',info[0:2])[0] #Unpacking bytes 0 and 1, 
    iIndex = unpack('B',info[3:4])[0]
    iTimestamp = unpack('I',info[4:8])[0]
    iTilt = (unpack('h',info[8:10])[0])/100
    iRoll = (unpack('h',info[10:12])[0])/100
    iRWSstatus = unpack('H',info[212:214])[0]
    iRAWSstatus = unpack('H',info[214:216])[0]
    iTIstatus = unpack('H',info[216:218])[0]
    iHWShubstatus = unpack('H',info[218:220])[0]
    iDirHubstatus = unpack('H',info[220:222])[0]
    iLOS = unpack('B',info[222:223])[0]
##    print(iRWSstatus)
##    iRWSstatus = 46
##    print(iRWSstatus)
##    print(bin(iRWSstatus))
##    print(len(bin(iRWSstatus)))
    #Unpacking for the slices
    for i in range(10):
        iD[i] = (unpack('h',info[12+(i*2):14+(i*2)])[0])/10
        iRWS[i] = (unpack('h',info[32+(i*2):34+(i*2)])[0])/100
        iVeer[i] = (unpack('h',info[52+(i*2):54+(i*2)])[0])/100
        iRAWS[i] = (unpack('h',info[72+(i*2):74+(i*2)])[0])/100
        iT[i] = (unpack('h',info[92+(i*2):94+(i*2)])[0])/100
        iHWShub[i] = (unpack('h',info[112+(i*2):114+(i*2)])[0])/100
        iDirectionHub[i] = (unpack('h',info[132+(i*2):134+(i*2)])[0])/100
        iVsheer[i] = (unpack('h',info[152+(i*2):154+(i*2)])[0])/100
        iHsheer[i] = (unpack('h',info[172+(i*2):174+(i*2)])[0])/100
        iCNR[i] = math.log10(unpack('h',info[192+(i*2):194+(i*2)])[0])

    #Saving the interpreted info from the GoogleDrive into the program
##    timestamps.append(iTimestamp) TIME FROM THE LIDAR IS GIVEN IN MS AND IT IS JUST THE TIME AFTER MIDNIGHT
    tilt.append(iTilt)  #SIMPLE SIGNALS WITH NO ARRAY; JUST ONE SIGNAL IS RECEIVED EVERY CYCLE AND NOT 10
    roll.append(iRoll)  #SIMPLE SIGNALS WITH NO ARRAY; JUST ONE SIGNAL IS RECEIVED EVERY CYCLE AND NOT 10
    for i in range(10):
        radialWS[i].append(iRWS[i])
        verticalWV[i].append(iVeer[i])
        recrotWS[i].append(iRAWS[i])
        turbulenceI[i].append(iT[i])
        horWShub[i].append(iHWShub[i])
        windDirHH[i].append(iDirectionHub[i])
        verticalWS[i].append(iVsheer[i])
        horizontalWS[i].append(iHsheer[i])
        cnr[i].append(iCNR[i])
        data_distancesTest[i] = int(iD[i])
    
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
        value='HWShub',
	multi=False),

    dcc.Graph(id='live-graph', animate=False),
    dcc.Interval(id='graph-update',interval=refreshInterval,n_intervals=0),
    dcc.Checklist(id="liveUpdate",
    options=[
        {'label': 'Live', 'value': "on"}
    ],
    value=["on"],
    labelStyle={'display': 'inline-block'}),
    
    ] )

#Callback for the graph, takes the intervals and the signal name as in input

#and plots the graph according to the requested signal, check box for live update signal
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
    #check for the input interval to know if it has a value or not.


    #Update the signals information
    update_signals(timestamps,tilt,roll,radialWS,verticalWV,recrotWS,turbulenceI,horWShub,windDirHH,verticalWS,horizontalWS,cnr)
    ########################################################CHECK IF THE USER WANTS LIVE GRAPH OR STATIC GRAPH; IF STATIC; THEN DONT RETURN ANYTHING AND STOP PLOTTING INFORMATION#####################################
    if(len(state) == 0):
        return null
    else:
        ########################################################CHECK IF THE USER WANT TO HAVE A SINGLE SIGNAL OR A SIGNAL THAT HAS 10 DIFFERENT VALUES(SLICE)########################################################
        ########################################################ACCORDING TO THE RESPONSE; CREATE 10 DIFFERENT SIGNALS OR JUST ONE AND RETURN THE RESULT########################################################
        if(select_signal(signal_name)):
            datax =  plotly.graph_objs.Scatter(
                            #Signal-Information to plot in the X axis
                            x=list(timestamps[-elementsLimits:]),
                            #Signal-Information to plot in the Y axis
                            y=list(data_signals[signal_name]),
                            #Name for the signal-points when hovering over the points
                            name= signal_name,
                            mode= 'lines+markers',
                            #Activates the legend in the screen and the description to the legend
                            showlegend = True,
                            text = signal_name,
                            )
            #Return the ten different graphs with the adjust-setting for the graph, title etc.
            return {'data': [datax],
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
########################################################CREATE 10 DIFFERENT SIGNALS AND RETURN THEM########################################################
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
                            name= signal_name + " " + str(data_distancesTest[i]) + " m gate",
                            mode= 'lines+markers',
                            #Activates the legend in the screen and the description to the legend
                            showlegend = True,
                            text = signal_name + " " + str(data_distancesTest[i]) + " meters",
                            
                            )
                #Return the ten different graphs with the adjust-setting for the graph, title etc.
            return {'data': [datax[0],datax[1],datax[2],datax[3],datax[4],datax[5],datax[6],datax[7],datax[8],datax[9]],
                    'layout' : go.Layout(#Axisx adjust just according to the last 200 values, after 200 values they start going
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
                                                                        dict(count=30*(refreshInterval/1000),
                                                                             label="30",
                                                                             step="second",
                                                                             stepmode="backward"),
                                                                        dict(count=60*(refreshInterval/1000),
                                                                             label="60",
                                                                             step="second",
                                                                             stepmode="backward"),
                                                                        dict(count=120*(refreshInterval/1000),
                                                                             label="120",
                                                                             step="second",
                                                                             stepmode="backward")])),
                                        rangeslider=dict(autorange=True,
                                                         visible=True,
                                                         range=[min(timestamps[-elementsLimits:]),max(timestamps[-elementsLimits:])]),
                                        type = "date"
                                        ))
                    }

if __name__ == '__main__':
    app.run_server(debug=False)
