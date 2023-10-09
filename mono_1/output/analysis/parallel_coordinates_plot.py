from sklearn import preprocessing
from matplotlib import pyplot as plt
from matplotlib import cm
import pandas as pd
import numpy
import sys
import os

# posicao,ociosidade,demNaoAtend,demNaoAtendEspecial,salasDiff

import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("geral.csv", header=0, delim_whitespace=False)
# fig = px.parallel_coordinates(df, color="position",
#                               dimensions=['idleness','deallocated','lessThan10','moreThan10','preferences','professors'],
#                               color_continuous_scale=px.colors.diverging.Tealrose,
#                               color_continuous_midpoint=75)
# fig.show()

fig = go.Figure(data=
    go.Parcoords(
        line = dict(color = df['professors'],
                   colorscale = 'Electric',
                   showscale = True),
        dimensions = list([
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "idleness", values = df['idleness']),
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "deallocated", values = df['deallocated']),
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "lessThan10", values = df['lessThan10']),
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "moreThan10", values = df['moreThan10']),
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "preferences", values = df['preferences']),
            dict(range = [0,1],
                 tickvals = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                 label = "professors", values = df['professors'])])
    )
)
fig.show()










# def plotGraph(argv):
#     data_size = 1000

#     df1 = pd.read_csv(argv[1], header=0, delim_whitespace=False)
#     df2 = pd.read_csv(argv[2], header=0, delim_whitespace=False)
#     df3 = pd.read_csv(argv[3], header=0, delim_whitespace=False)
#     # df1 = df1.sample(data_size) # pegando algumas linhas aleatórias

#     # print(df1.describe())
#     # print("\n")

#     cols_to_norm = ["ociosidade", "demNaoAtend", "demNaoAtendEspecial", "salasDiff"]

#     # Geral
#     ax = pd.plotting.parallel_coordinates(df1, class_column="posicao", cols=cols_to_norm, colormap=cm.winter)
#     ax = pd.plotting.parallel_coordinates(df2, class_column="posicao", cols=cols_to_norm, colormap=cm.autumn)
#     ax = pd.plotting.parallel_coordinates(df3, class_column="posicao", cols=cols_to_norm, color='black')
#     ax.get_legend().remove()
#     nomeArq = argv[1].split(sep=".")[0]
#     # plt.savefig(nomeArq, dpi=300)
#     plt.savefig("geral", dpi=300)
#     plt.figure()

#     # Separado
#     ax = pd.plotting.parallel_coordinates(df1, class_column="posicao", cols=cols_to_norm, colormap=cm.winter)
#     ax.get_legend().remove()
#     nomeArq = argv[1].split(sep=".")[0]
#     plt.savefig(nomeArq, dpi=300)
#     plt.figure()

#     ax = pd.plotting.parallel_coordinates(df2, class_column="posicao", cols=cols_to_norm, colormap=cm.winter)
#     ax.get_legend().remove()
#     nomeArq = argv[2].split(sep=".")[0]
#     plt.savefig(nomeArq, dpi=300)
#     plt.figure()

#     # for i in range(len(cols_to_norm) - 1):
#     #     for j in range((i + 1), len(cols_to_norm)):
#     #         ax = pd.plotting.parallel_coordinates(df1, class_column=cols_to_norm[i], cols=[cols_to_norm[i], cols_to_norm[j]], colormap=cm.Wistia)
#     #         ax.get_legend().remove()
#     #         plt.savefig(f"{cols_to_norm[i]}-{cols_to_norm[j]}", dpi=300)
#     #         plt.figure()

# plotGraph(sys.argv)