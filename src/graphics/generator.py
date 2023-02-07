import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import json

direct = "%s"%(os.getcwd())
fig = go.Figure()

# Creating class to read file 
class Graph:
    executionTime = []
    executionCost = []

    def __init__(self):
        self.executionTime = []
        self.executionCost = []

    def pushTime(self, time):
        self.executionTime.append(time)
    def pushCost(self, cost):
        self.executionCost.append(cost)

# Reading File
def readFile(graphClass, fileName):
    f = open(fileName)
    data = json.load(f)

    for i in data['points']:
        # print(i)
        graphClass.pushTime(float(i['time']))
        graphClass.pushCost(int(i['cost']))

    f.close()
    return
    try:
        auxIter = 0
        # File processing
        _dataLinesArray = graphFile.readlines()
        for i in _dataLinesArray:
            _auxLine = i.split()
            graphClass.pushTime(float(_auxLine[0]))
            graphClass.pushCost(int(_auxLine[1]))


    finally:
        graphFile.close()

# Plotting Graph 
def plotGraph(argv):

    # ano = argv[1]
    # semestre = argv[2]
    # tempo = argv[3]
    # seed = [1,2,3,4,5]


    graphClassExec01 = Graph()
    graphClassExec02 = Graph()
    graphClassExec03 = Graph()
    graphClassExec04 = Graph()
    graphClassExec05 = Graph()

    graphClassArray = [graphClassExec01, graphClassExec02, graphClassExec03, graphClassExec04, graphClassExec05]
    solucaoMedia = 0

    # for i in range(5):
    #     file = "pas-%s-%s-preferencias-dados-reais_S%d_T%s.txt"%(str(ano), str(semestre), seed[i], str(tempo))
    #     readFile(graphClassArray[i], file)

    readFile(graphClassArray[0], "../../output/newModel/1-10-100-1000/costGraphic_seed-1_maxTime-900.json")
    readFile(graphClassArray[1], "../../output/newModel/1-10-100-1000/costGraphic_seed-2_maxTime-900.json")
    readFile(graphClassArray[2], "../../output/newModel/1-10-100-1000/costGraphic_seed-3_maxTime-900.json")
    readFile(graphClassArray[3], "../../output/newModel/1-10-100-1000/costGraphic_seed-4_maxTime-900.json")
    readFile(graphClassArray[4], "../../output/newModel/1-10-100-1000/costGraphic_seed-5_maxTime-900.json")
    # exit(0)
    
    title = "GAP all 1 -> 900s"
    fileOutput = "GAP_1-10-100-1000_900s"

    # Calculando GAP
    menor = graphClassExec01.executionCost[len(graphClassExec01.executionCost) - 1]
    for i in range(len(graphClassArray)):
        size = len(graphClassArray[i].executionCost) - 1
        if graphClassArray[i].executionCost[size] <= menor:
            menor = graphClassArray[i].executionCost[size]
 
    # Atualizando vetor de custos com GAP
    gapExec01 = Graph()
    gapExec02 = Graph()
    gapExec03 = Graph()
    gapExec04 = Graph()
    gapExec05 = Graph()

    gapArray = [gapExec01, gapExec02, gapExec03, gapExec04, gapExec05]

    for i in range(len(graphClassArray)):
        for j in range(len(graphClassArray[i].executionCost)):
            gapArray[i].pushTime(graphClassArray[i].executionTime[j])
            gap = 0

            if graphClassArray[i].executionCost[j] != 0:
                gap = ((graphClassArray[i].executionCost[j] - menor) / graphClassArray[i].executionCost[j]) * 100
            else:
                gap = 0

            gapArray[i].pushCost(gap)

    # Edit the layout
    fig.update_layout(title="%s"%(title),
                   xaxis_title="Tempo (s)",
                   yaxis_title='GAP (%)')
    fig.add_trace(go.Scatter(x=gapExec01.executionTime, y=gapExec01.executionCost, mode = 'lines', name = "Seed 01", line=dict(color='blue', width=4)))
    fig.add_trace(go.Scatter(x=gapExec02.executionTime, y=gapExec02.executionCost, mode = 'lines', name = "Seed 02", line=dict(color='green', width=4)))
    fig.add_trace(go.Scatter(x=gapExec03.executionTime, y=gapExec03.executionCost, mode = 'lines', name = "Seed 03", line=dict(color='red', width=4)))
    fig.add_trace(go.Scatter(x=gapExec04.executionTime, y=gapExec04.executionCost, mode = 'lines', name = "Seed 04", line=dict(color='yellow', width=4)))
    fig.add_trace(go.Scatter(x=gapExec05.executionTime, y=gapExec05.executionCost, mode = 'lines', name = "Seed 05", line=dict(color='purple', width=4)))

    fig.update_layout(
        # title="Plot Title",
        # xaxis_title="X Axis Title",
        # yaxis_title="Y Axis Title",
        # legend_title="Legend Title",
        font=dict(
            # family="Arial",
            size=30,
            # color="RebeccaPurple"
        )
    )

    fig.write_html("%s/%s.html"%(direct, fileOutput))
    fig.write_html("../../output/newModel/%s.html"%(fileOutput))


    # Dados para tabela
    for i in range(5):
        solucaoMedia += graphClassArray[i].executionCost[len(graphClassArray[i].executionCost) - 1] / 5

    print("Menor: ", float(menor))
    print("Media: ", solucaoMedia) 


plotGraph(sys.argv)

# python nome.py ano semestre tempo
