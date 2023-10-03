import plotly.express as px
import pandas as pd
df = pd.read_csv("geral.csv", header=0, delim_whitespace=False)
fig = px.scatter_matrix(df)
fig.show()