import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def generate_graphic(original_population, final_population):

    max_idleness, max_standing, max_deallocated = get_normalization_values(original_population[0])

    original_idleness = [individual['objectives'].idleness / max_idleness for individual in original_population]
    original_deallocated = [individual['objectives'].deallocated / max_deallocated for individual in original_population]
    original_standing = [individual['objectives'].standing / max_standing for individual in original_population]

    final_idleness = [individual['objectives'].idleness / max_idleness for individual in final_population]
    final_deallocated = [individual['objectives'].deallocated / max_deallocated for individual in final_population]
    final_standing = [individual['objectives'].standing / max_standing for individual in final_population]

    fig = go.Figure(data=[go.Scatter3d(x=original_idleness, y=original_deallocated, z=original_standing,mode='markers'), go.Scatter3d(x=final_idleness, y=final_deallocated, z=final_standing,mode='markers', marker=dict(color='green'))])
    # fig.update_layout(xaxis_title="Idleness", yaxis_title="Deallocated", zaxis_title="Standing")
    fig.update_layout(
        scene = dict(
            xaxis = dict(nticks=10, range=[0, 1],),
            yaxis = dict(nticks=10, range=[0, 1],),
            zaxis = dict(nticks=10, range=[0, 1],),
            xaxis_title='Idleness',
            yaxis_title='Deallocated',
            zaxis_title='Standing',
        )
    )
    fig.show()

def get_normalization_values(solution):
    lower_capacity = 999
    higher_capacity = -1
    max_idleness = 0
    max_standing = 0
    max_deallocated = 0

    for classroom in solution['classrooms']:
        if classroom.capacity < lower_capacity:
            lower_capacity = classroom.capacity
        if classroom.capacity > higher_capacity:
            higher_capacity = classroom.capacity

    for meeting in solution['meetings']:
        max_deallocated += meeting.demand
        max_idleness += higher_capacity - meeting.demand if higher_capacity - meeting.demand > 0 else 0
        max_standing += meeting.demand - lower_capacity if meeting.demand - lower_capacity > 0 else 0

    return max_idleness, max_standing, max_deallocated
