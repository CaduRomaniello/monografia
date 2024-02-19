import os
import copy
import json
import numpy as np
import plotly.graph_objects as go

from heuristics.mip import mipPy
from utils.pareto import dominates
from movements.allocate import allocate
from classes.objectives import Objectives
from pymoo.indicators.hv import Hypervolume
from utils.instance import parse_data, read_instance
from utils.population import generate_first_population
from utils.verifier import remove_objectives_duplicates, verifier
from utils.dataManipulation import allocate_professors, allocate_reservations, create_variable_classrooms, create_variable_meetings, create_variable_professors, find_preferences, find_relatives_meetings

def normalize_values(values_1, values_2, values_3):
    max_value = max(max(values_1), max(values_2), max(values_3))
    min_value = min(min(values_1), min(values_2), min(values_3))
    return [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_1],\
           [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_2],\
           [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_3]

def normalize_values_epsilon(values_1, values_2, values_3, values_4):
    max_value = max(max(values_1), max(values_2), max(values_3), max(values_4))
    min_value = min(min(values_1), min(values_2), min(values_3), min(values_4))
    return [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_1],\
           [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_2],\
           [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_3],\
           [((value - min_value) / (max_value - min_value)) if (max_value - min_value != 0) else 1 for value in values_4]

def nondominated_sort(solutions):
    fronts = []
    domination_count = [0] * len(solutions)
    dominated_solutions = [[] for _ in range(len(solutions))]

    for i in range(len(solutions)):
        for j in range(i + 1, len(solutions)):
            if dominates(solutions[i], solutions[j]):
                dominated_solutions[i].append(j)
                domination_count[j] += 1
            elif dominates(solutions[j], solutions[i]):
                dominated_solutions[j].append(i)
                domination_count[i] += 1

    front = []
    for i in range(len(solutions)):
        if domination_count[i] == 0:
            front.append(i)

    while front:
        next_front = []
        for i in front:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        fronts.append(front)
        front = next_front

    return fronts

def graphics(filename):
    ###############################################################################################################################################
    # READING INSTANCE DATA AND SOLVING MIP
    objectives = Objectives()

    # Reading instance data
    instance_data = read_instance(filename)

    # Creating variables
    instance = parse_data(instance_data)
    classrooms = create_variable_classrooms(instance)
    professors = create_variable_professors(instance)
    meetings = create_variable_meetings(instance, objectives)

    # Allocating professors, reservations, preferences and looking for relatives meetings
    relatives_meetings = find_relatives_meetings(meetings)
    allocate_professors(meetings, professors)
    allocate_reservations(classrooms, instance["reservations"])
    find_preferences(meetings, instance["preferences"])

    # Saving original solution
    print(f"[INFO] Saving original solution")
    original_meetings = copy.deepcopy(meetings)
    original_classrooms = copy.deepcopy(classrooms)
    original_objectives = copy.deepcopy(objectives)
    original_solution = {
        "meetings": original_meetings,
        "classrooms": original_classrooms,
        "objectives": original_objectives
    }
    verifier(original_solution)

    print(len(original_meetings))
    print(len(classrooms))
    print(len(instance_data['schedules']))
    # exit()

    # Separating solution in subparts to solve it using MIP
    monday = []
    tuesday = []
    wednesday = []
    thursday = []
    friday = []
    saturday = []
    for meeting in original_meetings:
        if meeting.day_name() == 'monday':
            monday.append(meeting)
        elif meeting.day_name() == 'tuesday':
            tuesday.append(meeting)
        elif meeting.day_name() == 'wednesday':
            wednesday.append(meeting)
        elif meeting.day_name() == 'thursday':
            thursday.append(meeting)
        elif meeting.day_name() == 'friday':
            friday.append(meeting)
        elif meeting.day_name() == 'saturday':
            saturday.append(meeting)
        else:
            raise Exception('Invalid day of week')

    # Solving subparts using MIP
    mip_solution = copy.deepcopy(original_solution)

    ## Monday
    monday_cost, monday_allocations = mipPy({'meetings': monday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in monday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Tuesday
    tuesday_cost, tuesday_allocations = mipPy({'meetings': tuesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in tuesday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Wednesday
    wednesday_cost, wednesday_allocations = mipPy({'meetings': wednesday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in wednesday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Thursday
    thursday_cost, thursday_allocations = mipPy({'meetings': thursday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in thursday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Friday
    friday_cost, friday_allocations = mipPy({'meetings': friday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in friday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Saturday
    saturday_cost, saturday_allocations = mipPy({'meetings': saturday, "classrooms": original_classrooms, "objectives": original_objectives}, instance)
    for i in saturday_allocations:
        if i['classroom_id'] != 0:
            allocate(mip_solution, i['meeting_id'], i['classroom_id'])

    ## Verifying MIP solution
    verifier(mip_solution)
    mip_solution['objectives'].print()
    total_cost = monday_cost + tuesday_cost + wednesday_cost + thursday_cost + friday_cost + saturday_cost
    print(f'[INFO] Total cost: {total_cost}')
    # exit()

    mip_objectives = copy.deepcopy(mip_solution['objectives'])


    ###############################################################################################################################################

    input = filename
    if filename != 'instance.json':
        filename = filename.split('.')[0].split('input-')[1]
    else:
        filename = filename.split('.')[0]
    filename = f'output-instance-{filename}'

    current_directory = os.getcwd()
    print('Diretório de Trabalho Atual:', current_directory)

    lahc_multi_data = []
    number_of_solutions_lahc = []
    for i in range(5):
        with open(f'../json/output/lahc-multi/{filename}-params-seed-{i + 1}-time-900.json', 'r') as file:
            data = json.load(file)
            number_of_solutions_lahc.append(len(data[0]))
            data = [Objectives(i["idleness"], i["deallocated"], i["standing"]) for i in data[0]]
            lahc_multi_data = lahc_multi_data + data
    lahc_multi_data = remove_objectives_duplicates(lahc_multi_data)
    pareto_front = nondominated_sort(lahc_multi_data)[0]
    lahc_multi_data = [lahc_multi_data[i] for i in pareto_front]

    nsgaII_data = []
    number_of_solutions_nsgaII = []
    for i in range(5):
        with open(f'../json/output/nsgaII/{filename}-params-seed-{i + 1}-time-900.json', 'r') as file:
            data = json.load(file)
            number_of_solutions_nsgaII.append(len(data[0]))
            data = [Objectives(i["idleness"], i["deallocated"], i["standing"]) for i in data[0]]
            nsgaII_data = nsgaII_data + data
    nsgaII_data = remove_objectives_duplicates(nsgaII_data)
    pareto_front = nondominated_sort(nsgaII_data)[0]
    nsgaII_data = [nsgaII_data[i] for i in pareto_front]

    epsilon_data = []
    with open(f'../json/output/epsilon/{filename}-params-epsilon.json', 'r') as file:
        data = json.load(file)
        print(data[0])
        data = [Objectives(i["idleness"], i["deallocated"], i["standing"]) for i in data[0]]
        epsilon_data = epsilon_data + data
    epsilon_data = remove_objectives_duplicates(epsilon_data)
    pareto_front = nondominated_sort(epsilon_data)[0]
    epsilon_data = [epsilon_data[i] for i in pareto_front]
    number_of_solutions_epsilon = len(epsilon_data)
    
    # lahc_multi_data[0] = [Objectives(i["idleness"], i["deallocated"], i["standing"]) for i in lahc_multi_data[0]]
    # lahc_multi_data = remove_objectives_duplicates(lahc_multi_data[0])

    # nsgaII_data[0] = [Objectives(i["idleness"], i["deallocated"], i["standing"]) for i in nsgaII_data[0]]
    # nsgaII_data = remove_objectives_duplicates(nsgaII_data[0])

    mip_data = [mip_objectives]

    # initial_population = generate_first_population(original_solution, percentage=0.2, greedy=False)
    # initial_population = [i['objectives'] for i in initial_population]
    # initial_population = remove_objectives_duplicates(initial_population)

    mip_dominates = 0
    mip_is_dominated = 0
    for i in range(len(nsgaII_data)):
        if dominates(mip_data[0], nsgaII_data[i]):
            mip_dominates += 1
        elif dominates(nsgaII_data[i], mip_data[0]):
            mip_is_dominated += 1

    print(f'MIP dominates {mip_dominates} solutions')
    print(f'MIP is dominated by {mip_is_dominated} solutions')
    print(f'Total solutions of NSGAII algorithm: {len(nsgaII_data)}')

    ###############################################################################################################################################

    x_axis_lahc_multi = [i.idleness for i in lahc_multi_data]
    y_axis_lahc_multi = [i.deallocated for i in lahc_multi_data]
    z_axis_lahc_multi = [i.standing for i in lahc_multi_data]

    x_axis_nsgaII = [i.idleness for i in nsgaII_data]
    y_axis_nsgaII = [i.deallocated for i in nsgaII_data]
    z_axis_nsgaII = [i.standing for i in nsgaII_data]

    x_axis_mip = [i.idleness for i in mip_data]
    y_axis_mip = [i.deallocated for i in mip_data]
    z_axis_mip = [i.standing for i in mip_data]

    x_axis_epsilon = [i.idleness for i in epsilon_data]
    y_axis_epsilon = [i.deallocated for i in epsilon_data]
    z_axis_epsilon = [i.standing for i in epsilon_data]

    # x_axis_initial = [i.idleness for i in initial_population]
    # y_axis_initial = [i.deallocated for i in initial_population]
    # z_axis_initial = [i.standing for i in initial_population]

    # x_axis_lahc_multi, x_axis_nsgaII, x_axis_mip = normalize_values(x_axis_lahc_multi, x_axis_nsgaII, x_axis_mip)
    # y_axis_lahc_multi, y_axis_nsgaII, y_axis_mip = normalize_values(y_axis_lahc_multi, y_axis_nsgaII, y_axis_mip)
    # z_axis_lahc_multi, z_axis_nsgaII, z_axis_mip = normalize_values(z_axis_lahc_multi, z_axis_nsgaII, z_axis_mip)
    x_axis_lahc_multi, x_axis_nsgaII, x_axis_mip, x_axis_epsilon = normalize_values_epsilon(x_axis_lahc_multi, x_axis_nsgaII, x_axis_mip, x_axis_epsilon)
    y_axis_lahc_multi, y_axis_nsgaII, y_axis_mip, y_axis_epsilon = normalize_values_epsilon(y_axis_lahc_multi, y_axis_nsgaII, y_axis_mip, y_axis_epsilon)
    z_axis_lahc_multi, z_axis_nsgaII, z_axis_mip, z_axis_epsilon = normalize_values_epsilon(z_axis_lahc_multi, z_axis_nsgaII, z_axis_mip, z_axis_epsilon)

    ###############################################################################################################################################

    hv_lahc_data = []
    for i in range(len(x_axis_lahc_multi)):
        hv_lahc_data.append([x_axis_lahc_multi[i], y_axis_lahc_multi[i], z_axis_lahc_multi[i]])

    hv_nsgaII_data = []
    for i in range(len(x_axis_nsgaII)):
        hv_nsgaII_data.append([x_axis_nsgaII[i], y_axis_nsgaII[i], z_axis_nsgaII[i]])

    hv_epsilon_data = []
    for i in range(len(x_axis_epsilon)):
        hv_epsilon_data.append([x_axis_epsilon[i], y_axis_epsilon[i], z_axis_epsilon[i]])

    hv_mip_data = []
    for i in range(len(x_axis_mip)):
        hv_mip_data.append([x_axis_mip[i], y_axis_mip[i], z_axis_mip[i]])

    reference_point = np.array([2.0, 2.0, 2.0])
    hv_calculator = Hypervolume(reference_point)

    hypervolume_lahc = hv_calculator.do(np.array(hv_lahc_data))
    print("Hypervolume LAHC:", hypervolume_lahc)

    hypervolume_nsgaII = hv_calculator.do(np.array(hv_nsgaII_data))
    print("Hypervolume NSGA-II:", hypervolume_nsgaII)

    hypervolume_epsilon = hv_calculator.do(np.array(hv_epsilon_data))
    print("Hypervolume Epsilon:", hypervolume_epsilon)

    hypervolume_mip = hv_calculator.do(np.array(hv_mip_data))
    print("Hypervolume MIP:", hypervolume_mip)

    lahc_metrics = {
        'hypervolume': hypervolume_lahc,
        'number_of_solutions': number_of_solutions_lahc,
        'min_solutions': min(number_of_solutions_lahc),
        'max_solutions': max(number_of_solutions_lahc),
        'mean_solutions': sum(number_of_solutions_lahc) / len(number_of_solutions_lahc)
    }

    nsgaII_metrics = {
        'hypervolume': hypervolume_nsgaII,
        'number_of_solutions': number_of_solutions_nsgaII,
        'min_solutions': min(number_of_solutions_nsgaII),
        'max_solutions': max(number_of_solutions_nsgaII),
        'mean_solutions': sum(number_of_solutions_nsgaII) / len(number_of_solutions_nsgaII)
    }

    epsilon_metrics = {
        'hypervolume': hypervolume_epsilon,
        'number_of_solutions': number_of_solutions_epsilon,
        'solutions': number_of_solutions_epsilon
    }

    # with open(f'../graphics/tables/lahc-metrics-{input.split(".")[0]}.json', 'w') as f:
    #         f.write(json.dumps(lahc_metrics))

    # with open(f'../graphics/tables/nsga-metrics-{input.split(".")[0]}.json', 'w') as f:
    #         f.write(json.dumps(nsgaII_metrics))

    # with open(f'../graphics/tables/epsilon-metrics-{input.split(".")[0]}.json', 'w') as f:
    #         f.write(json.dumps(epsilon_metrics))

    ###############################################################################################################################################

    fig = go.Figure()

    lahc_multi_scatter = go.Scatter3d(
        x=x_axis_lahc_multi,
        y=y_axis_lahc_multi,
        z=z_axis_lahc_multi,
        mode='markers',
        name='MOLA',
        hovertemplate='<b>Idleness</b>: %{x}'+'<br><b>Deallocated</b>: %{y}<br><b>Standing</b>: %{z}',
        marker=dict(
            color='red',
            size=5,
            symbol='diamond-open'
        ),
        showlegend=True
    )
    lahc_multi_scatter_legend = go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],
        mode='markers',
        name='MOLA',
        marker=dict(
            color='red',
            size=10,
            symbol='diamond',
            opacity=0
        ),
        showlegend=True
    )

    nsgaII_scatter = go.Scatter3d(
        x=x_axis_nsgaII,
        y=y_axis_nsgaII,
        z=z_axis_nsgaII,
        mode='markers',
        name='NSGA-II',
        hovertemplate='<b>Idleness</b>: %{x}'+'<br><b>Deallocated</b>: %{y}<br><b>Standing</b>: %{z}',
        marker=dict(
            color='blue',
            size=5,
            symbol='circle-open'
        ),
        showlegend=True
    )
    nsgaII_scatter_legend = go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],
        mode='markers',
        name='NSGA-II',
        marker=dict(
            color='blue',
            size=10,
            symbol='circle',
            opacity=0
        ),
        showlegend=True
    )

    mip_scatter = go.Scatter3d(
        x=x_axis_mip,
        y=y_axis_mip,
        z=z_axis_mip,
        mode='markers',
        name='MIP',
        hovertemplate='<b>Idleness</b>: %{x}'+'<br><b>Deallocated</b>: %{y}<br><b>Standing</b>: %{z}',
        marker=dict(
            color='green',
            size=5,
            symbol='square'
        ),
        showlegend=True
    )
    mip_scatter_legend = go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],
        mode='markers',
        name='MIP',
        marker=dict(
            color='green',
            size=10,
            symbol='square',
            opacity=0
        ),
        showlegend=True
    )

    epsilon_scatter = go.Scatter3d(
        x=x_axis_epsilon,
        y=y_axis_epsilon,
        z=z_axis_epsilon,
        mode='markers',
        name='Epsilon restrito',
        hovertemplate='<b>Idleness</b>: %{x}'+'<br><b>Deallocated</b>: %{y}<br><b>Standing</b>: %{z}',
        marker=dict(
            color='black',
            size=3,
            symbol='x'
        ),
        showlegend=True
    )
    epsilon_scatter_legend = go.Scatter3d(
        x=[None],
        y=[None],
        z=[None],
        mode='markers',
        name='Restricted epsilon',
        marker=dict(
            color='black',
            size=10,
            symbol='x',
            opacity=0
        ),
        showlegend=True
    )

    fig.add_trace(lahc_multi_scatter)
    # fig.add_trace(lahc_multi_scatter_legend)

    fig.add_trace(nsgaII_scatter)
    # fig.add_trace(nsgaII_scatter_legend)

    fig.add_trace(epsilon_scatter)
    # fig.add_trace(epsilon_scatter_legend)

    fig.add_trace(mip_scatter)
    # fig.add_trace(mip_scatter_legend)

    # fig.add_trace(initial_scatter)

    fig.update_layout(scene=dict(xaxis_title='Ociosidade (Idl)', yaxis_title='Desalocação (Dea)', zaxis_title='Em pé (Sta)'))

    fig.update_layout(title=f'Comparação das soluções ({input})')

    fig.update_layout(legend=dict(title='Algoritmos', itemsizing='constant', itemclick='toggleothers'))

    # fig = go.Figure(data=[
    #         go.Scatter3d(x=x_axis_nsgaII, y=y_axis_nsgaII, z=z_axis_nsgaII, mode='markers', marker=dict(color='red', size=7)),
    #         go.Scatter3d(x=x_axis_lahc_multi, y=y_axis_lahc_multi, z=z_axis_lahc_multi, mode='markers', marker=dict(color='blue', size=7)),
    #         go.Scatter3d(x=x_axis_mip, y=y_axis_mip, z=z_axis_mip, mode='markers', marker=dict(color='green', size=7))
    #     ]
    # )

    # fig.update_layout(scene=dict(xaxis_title='Idleness', yaxis_title='Deallocated', zaxis_title='Standing'))

    # Exibir o gráfico
    print(len(epsilon_data))
    fig.show()
    # fig.write_image(f"../graphics/{input.split('.')[0]}.png", engine='kaleido')

graphics('input-seed-5-size-1000.json')