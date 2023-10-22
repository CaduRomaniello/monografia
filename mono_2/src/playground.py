import plotly.express as px
df = px.data.iris()
import plotly.graph_objects as go
import numpy as np

x1 = [0, 1, 2, 3, 4]
y1 = [0, 1, 2, 3, 4]
z1 = [0, 1, 2, 3, 4]
c = ['b', 'r', 'g', 'b', 'o']

original_idleness = [21828, 21915, 21714, 21956, 22111, 21664, 21771, 21970, 21841, 21666, 21681, 21867, 21940, 21863, 22011, 21836, 21581, 21875, 21823, 21910]
original_deallocated = [1314, 1321, 1093, 1267, 1307, 1196, 1254, 1209, 1390, 1180, 1225, 1193, 1032, 1311, 1347, 1199, 1114, 1178, 1255, 1421]
original_standing = [189, 191, 205, 237, 207, 183, 163, 195, 189, 227, 221, 198, 226, 269, 195, 235, 212, 180, 201, 202]
final_idleness = [21714, 21664, 21771, 21867, 21940, 21581, 21875, 16922, 17262, 16710, 16956, 17415, 17391, 17477, 17092, 16522, 16912, 16923, 16882, 16774]
final_deallocated = [1093, 1196, 1254, 1193, 1032, 1114, 1178, 5986, 5767, 5416, 5399, 5597, 5307, 5883, 5014, 6436, 5605, 5550, 5505, 5634]
final_standing = [205, 183, 163, 198, 226, 212, 180, 114, 115, 199, 166, 116, 131, 112, 154, 140, 121, 152, 155, 129]

# Helix equation
t = np.linspace(0, 10, 50)
x, y, z = np.cos(t), np.sin(t), t

# fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z,mode='markers'), go.Scatter3d(x=x1, y=y1, z=z1,mode='lines', line=dict(color='green', width=5))])
fig = go.Figure(data=[go.Scatter3d(x=original_idleness, y=original_deallocated, z=original_standing,mode='markers'), go.Scatter3d(x=final_idleness, y=final_deallocated, z=final_standing,mode='markers', marker=dict(color='green'))])
fig.show()