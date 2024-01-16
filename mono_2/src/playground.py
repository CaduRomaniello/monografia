# import plotly.express as px

# from classes.objectives import Objectives
# df = px.data.iris()
# import plotly.graph_objects as go
# import numpy as np

# obj1 = Objectives(8916, 472, 0)
# obj2 = Objectives(8917, 472, 0)
# print(obj1.dominates(obj2))
# print(obj2.dominates(obj1))

# x1 = [0, 1, 2, 3, 4]
# y1 = [0, 1, 2, 3, 4]
# z1 = [0, 1, 2, 3, 4]
# c = ['b', 'r', 'g', 'b', 'o']

# original_idleness = [21828, 21915, 21714, 21956, 22111, 21664, 21771, 21970, 21841, 21666, 21681, 21867, 21940, 21863, 22011, 21836, 21581, 21875, 21823, 21910]
# original_deallocated = [1314, 1321, 1093, 1267, 1307, 1196, 1254, 1209, 1390, 1180, 1225, 1193, 1032, 1311, 1347, 1199, 1114, 1178, 1255, 1421]
# original_standing = [189, 191, 205, 237, 207, 183, 163, 195, 189, 227, 221, 198, 226, 269, 195, 235, 212, 180, 201, 202]
# final_idleness = [21714, 21664, 21771, 21867, 21940, 21581, 21875, 16922, 17262, 16710, 16956, 17415, 17391, 17477, 17092, 16522, 16912, 16923, 16882, 16774]
# final_deallocated = [1093, 1196, 1254, 1193, 1032, 1114, 1178, 5986, 5767, 5416, 5399, 5597, 5307, 5883, 5014, 6436, 5605, 5550, 5505, 5634]
# final_standing = [205, 183, 163, 198, 226, 212, 180, 114, 115, 199, 166, 116, 131, 112, 154, 140, 121, 152, 155, 129]

# # Helix equation
# t = np.linspace(0, 10, 50)
# x, y, z = np.cos(t), np.sin(t), t

# # fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z,mode='markers'), go.Scatter3d(x=x1, y=y1, z=z1,mode='lines', line=dict(color='green', width=5))])
# fig = go.Figure(data=[go.Scatter3d(x=original_idleness, y=original_deallocated, z=original_standing,mode='markers'), go.Scatter3d(x=final_idleness, y=final_deallocated, z=final_standing,mode='markers', marker=dict(color='green'))])
# fig.show()

############################################################

# import matplotlib
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import json
# matplotlib.use('TkAgg')

# # Vetor de objetos no formato JSON
# vetor_objetos = [
#     '{"idleness": 963, "deallocated": 2506, "standing": 384}',
#     '{"idleness": 123, "deallocated": 1500, "standing": 200}',
#     '{"idleness": 500, "deallocated": 2000, "standing": 1000}',
#     # Adicione mais objetos conforme necessário
# ]

# # Converter os objetos JSON para dicionários Python
# objetos_dict = [json.loads(objeto) for objeto in vetor_objetos]

# # Extrair as coordenadas x, y e z dos objetos
# coord_x = [objeto["idleness"] for objeto in objetos_dict]
# coord_y = [objeto["deallocated"] for objeto in objetos_dict]
# coord_z = [objeto["standing"] for objeto in objetos_dict]

# # Criar a figura e o eixo 3D
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# # Plotar os pontos 3D
# ax.scatter(coord_x, coord_y, coord_z)

# # Definir rótulos dos eixos
# ax.set_xlabel('Idleness')
# ax.set_ylabel('Deallocated')
# ax.set_zlabel('Standing')

# plt.savefig('grafico_3d.png')

# # Exibir o gráfico
# plt.show()
# plt.pause(0.001)

############################################################

# import plotly.graph_objects as go
# import json

# # Vetor de objetos no formato JSON
# vetor_objetos = [
#     '{"idleness": 963, "deallocated": 2506, "standing": 384}',
#     '{"idleness": 123, "deallocated": 1500, "standing": 200}',
#     '{"idleness": 500, "deallocated": 2000, "standing": 1000}',
#     # Adicione mais objetos conforme necessário
# ]

# # Converter os objetos JSON para dicionários Python
# objetos_dict = [json.loads(objeto) for objeto in vetor_objetos]

# # Extrair as coordenadas x, y e z dos objetos
# coordenadas_x = [objeto["idleness"] for objeto in objetos_dict]
# coordenadas_y = [objeto["deallocated"] for objeto in objetos_dict]
# coordenadas_z = [objeto["standing"] for objeto in objetos_dict]

# # Criar o gráfico 3D
# fig = go.Figure(data=[go.Scatter3d(x=coordenadas_x, y=coordenadas_y, z=coordenadas_z, mode='markers', name="Teste")])

# # Definir rótulos dos eixos
# fig.update_layout(title='Gráfico 3D com Múltiplos Grupos', scene=dict(xaxis_title='Idleness', yaxis_title='Deallocated', zaxis_title='Standing'))

# # Exibir o gráfico
# fig.show()
# fig.write_image("grafico_3d_plotly.png")

############################################################

import plotly.graph_objects as go
import json

# Vetor de objetos no formato JSON
vetor_objetos1 = [
    '{"idleness": 963, "deallocated": 2506, "standing": 384}',
    '{"idleness": 123, "deallocated": 1500, "standing": 200}',
    '{"idleness": 500, "deallocated": 2000, "standing": 1000}',
]

vetor_objetos2 = [
    '{"idleness": 800, "deallocated": 1800, "standing": 800}',
    '{"idleness": 200, "deallocated": 1200, "standing": 300}',
    '{"idleness": 600, "deallocated": 1000, "standing": 500}',
]

# Converter os objetos JSON para dicionários Python
objetos_dict1 = [json.loads(objeto) for objeto in vetor_objetos1]
objetos_dict2 = [json.loads(objeto) for objeto in vetor_objetos2]

# Extrair as coordenadas x, y e z dos objetos
coordenadas_x1 = [objeto["idleness"] for objeto in objetos_dict1]
coordenadas_y1 = [objeto["deallocated"] for objeto in objetos_dict1]
coordenadas_z1 = [objeto["standing"] for objeto in objetos_dict1]

coordenadas_x2 = [objeto["idleness"] for objeto in objetos_dict2]
coordenadas_y2 = [objeto["deallocated"] for objeto in objetos_dict2]
coordenadas_z2 = [objeto["standing"] for objeto in objetos_dict2]

# Rótulos personalizados para o hover
rotulos_hover1 = [f'Idleness: {x}<br>Deallocated: {y}<br>Standing: {z}' for x, y, z in zip(coordenadas_x1, coordenadas_y1, coordenadas_z1)]
rotulos_hover2 = [f'Idleness: {x}<br>Deallocated: {y}<br>Standing: {z}' for x, y, z in zip(coordenadas_x2, coordenadas_y2, coordenadas_z2)]

# Criar o gráfico 3D
fig = go.Figure()

# Adicionar um conjunto de pontos usando go.Scatter3d
scatter1 = go.Scatter3d(x=coordenadas_x1, y=coordenadas_y1, z=coordenadas_z1, mode='markers', name='Grupo 1', hovertemplate='<b>Grupo 1</b><br><br><b>Idleness</b>: $%{x}'+'<br><b>Deallocated</b>: %{y}<br><b>Standing</b>: %{z}')
scatter2 = go.Scatter3d(x=coordenadas_x2, y=coordenadas_y2, z=coordenadas_z2, mode='markers', name='Grupo 2', hovertext=rotulos_hover2)

# Adicionar os traces ao gráfico
fig.add_trace(scatter1)
fig.add_trace(scatter2)

# Definir rótulos dos eixos
fig.update_layout(scene=dict(xaxis_title='Idleness', yaxis_title='Deallocated', zaxis_title='Standing'))

# Adicionar um título ao gráfico
fig.update_layout(title='Gráfico 3D com Múltiplos Grupos')

# Adicionar uma legenda
fig.update_layout(legend=dict(title='Grupos'))

# Exibir o gráfico
fig.show()
fig.write_image("grafico_3d_plotly.png")
