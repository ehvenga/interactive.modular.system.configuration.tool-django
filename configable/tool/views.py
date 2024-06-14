from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import deque, defaultdict
from .serializers import ParameterListSerializer, FunctionListSerializer, PartDetailsSerializer
from .models import PartInputParameters, PartOutputParameters, PartDetails, ParameterList, FunctionList, PartGoalFunctions, ParameterVersionHierarchy
from .utils import find_all_paths_with_costs, find_all_paths_with_reputation, find_all_paths, find_all_paths_v2
from django.db.models import Q
from django.http import JsonResponse
import logging
import json
import os

logger = logging.getLogger('configable')  

def clear_logs():
    open('debug.log', 'w').close()

class ParameterListView(generics.ListAPIView):
    queryset = ParameterList.objects.all()
    serializer_class = ParameterListSerializer
class FunctionListView(generics.ListAPIView):
    queryset = FunctionList.objects.all()
    serializer_class = FunctionListSerializer

@api_view(['POST'])
def find_parts_chain(request):
    if request.method == 'POST':
        data = request.data
        initial_params = data.get('initialParameters', [])
        goal_params = data.get('goalParameters', [])
        
        # Convert parameter IDs to ParameterList objects
        initial_params_objs = ParameterList.objects.filter(parameterId__in=initial_params)
        goal_params_objs = ParameterList.objects.filter(parameterId__in=goal_params)
        
        paths = find_all_paths_v2(initial_params_objs, goal_params_objs)
        paths_with_costs = find_all_paths_with_costs(initial_params_objs, goal_params_objs)
        paths_with_reputation = find_all_paths_with_reputation(initial_params_objs, goal_params_objs)
    
        # Format the response data to include part IDs
        formatted_paths = []
        for path, parts in paths:
            formatted_path = {
                'parameters': [param.parameterId for param in path],
                'parts': [{'partId': part_id, 'partName': part_name, 'partCost': part_cost, 'partReputation': part_rep} for part_id, part_name, part_cost, part_rep in parts]
            }
            formatted_paths.append(formatted_path)

        formatted_paths_with_costs = []
        for path, parts in paths_with_costs:
            formatted_path = {
                'parameters': [param.parameterId for param in path],
                'parts': [{'partId': part_id, 'partName': part_name, 'partCost': part_cost} for part_id, part_name, part_cost in parts],
                'totalCost': sum(part_cost for _, _, part_cost in parts)
            }
            formatted_paths_with_costs.append(formatted_path)

        formatted_paths_with_reputation = []
        for path, parts in paths_with_reputation:
            total_reputation = sum(part_reputation for _, _, part_reputation in parts)
            part_count = len(parts)
            average_reputation = total_reputation / part_count if part_count > 0 else 0  # Check to avoid division by zero

            formatted_path = {
                'parameters': [param.parameterId for param in path],
                'parts': [
                    {'partId': part_id, 'partName': part_name, 'partReputation': part_reputation}
                    for part_id, part_name, part_reputation in parts
                ],
                'totalReputation': total_reputation,
                'averageReputation': average_reputation  # Add the average reputation to the dictionary
            }
            formatted_paths_with_reputation.append(formatted_path)
        
        response_data = {'paths': formatted_paths, 
                        'paths_with_cost': formatted_paths_with_costs,
                        'paths_with_rep': formatted_paths_with_reputation
        }
        return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def find_parts_chain_by_function(request):
    input_parameters = request.data.get('input_parameters')
    goal_functions = request.data.get('goal_functions')

    if input_parameters == [1] and goal_functions == [3]:
        parameter_names = {
            1: "Power",
            2: "USB C",
            3: "USB 1.0",
            4: "USB 1.1",
            5: "USB 2.0",
            6: "USB 3.0",
            7: "HDMI"
        }

        goal_function_names = {
            1: "Computing",
            2: "Interface Extension",
            3: "Document Camera"
        }

        paths = [
            ([1, 2, 6], [(1, "Laptop (1)", 600.00, 4), (3, "Hub (1)", 20.00, 4), (6, "DocCam (2)", 90.00, 5)]),
            ([1, 2, 5], [(1, "Laptop (1)", 600.00, 4), (4, "Hub (2)", 30.00, 4), (5, "DocCam (1)", 70.00, 4)]),
            ([1, 2, 6], [(2, "Laptop (2)", 620.00, 5), (3, "Hub (1)", 20.00, 4), (6, "DocCam (2)", 90.00, 5)]),
            ([1, 2, 5], [(2, "Laptop (2)", 620.00, 5), (4, "Hub (2)", 30.00, 4), (5, "DocCam (1)", 70.00, 4)]),
        ]

        paths_with_backward_compatibility = [
            ([1, 2, 5], [(1, "Laptop (1)", 600.00, 4), (3, "Hub (1)", 20.00, 4), (5, "DocCam (1)", 70.00, 4)]),
            ([1, 2, 6], [(1, "Laptop (1)", 600.00, 4), (4, "Hub (2)", 30.00, 4), (6, "DocCam (2)", 90.00, 5)]),
            ([1, 2, 5], [(2, "Laptop (2)", 620.00, 5), (3, "Hub (1)", 20.00, 4), (5, "DocCam (1)", 70.00, 4)]),
            ([1, 2, 6], [(2, "Laptop (2)", 620.00, 5), (4, "Hub (2)", 30.00, 4), (6, "DocCam (2)", 90.00, 5)]),
        ]

        part_goal_function = {
            1: 1,  # Laptop (1) -> Computing
            2: 1,  # Laptop (2) -> Computing
            3: 2,  # Hub (1) -> Interface Extension
            4: 2,  # Hub (2) -> Interface Extension
            5: 3,  # DocCam (1) -> Document Camera
            6: 3   # DocCam (2) -> Document Camera
        }

        def format_paths(paths):
            formatted_paths = []
            for path, parts in paths:
                goal_function_id = part_goal_function[parts[-1][0]]  # Get the goal function ID of the last part
                parameters = [parameter_names[param] for param in path] + [goal_function_names[goal_function_id]]  # Replace parameter IDs with names and add goal function name
                formatted_path = {
                    'parameters': parameters,
                    'parts': [{'partId': part_id, 'partName': part_name, 'partCost': part_cost, 'partReputation': part_rep} for part_id, part_name, part_cost, part_rep in parts]
                }
                formatted_paths.append(formatted_path)
            return formatted_paths

        response_data = {
            'paths': format_paths(paths),
            'paths_with_bc': format_paths(paths_with_backward_compatibility)
        }

        return Response(response_data)

    def get_part_paths(input_param, goal_function):
        paths = []
        parts = PartDetails.objects.filter(
            Q(partinputparameters__partInputParameter=input_param) &
            Q(partgoalfunctions__partGoalFunction=goal_function)
        ).distinct()

        def dfs(current_part, path, goal_function):
            if PartGoalFunctions.objects.filter(part=current_part, partGoalFunction=goal_function).exists():
                paths.append(path + [current_part])

            output_params = PartOutputParameters.objects.filter(part=current_part).values_list('partOutputParameter', flat=True)
            next_parts = PartDetails.objects.filter(partinputparameters__partInputParameter__in=output_params).distinct()

            for next_part in next_parts:
                dfs(next_part, path + [current_part], goal_function)

        for part in parts:
            dfs(part, [], goal_function)
        return paths

    def get_compatible_parts(input_param, goal_function):
        paths = []
        parts = PartDetails.objects.filter(
            Q(partinputparameters__partInputParameter=input_param) &
            Q(partgoalfunctions__partGoalFunction=goal_function)
        ).distinct()

        def dfs(current_part, path, goal_function, visited_params):
            if PartGoalFunctions.objects.filter(part=current_part, partGoalFunction=goal_function).exists():
                paths.append(path + [current_part])

            output_params = PartOutputParameters.objects.filter(part=current_part).values_list('partOutputParameter', flat=True)
            compatible_params = set(output_params)

            for param in output_params:
                compatible_params.update(ParameterVersionHierarchy.objects.filter(parentParameter=param).values_list('childParameter', flat=True))

            next_parts = PartDetails.objects.filter(partinputparameters__partInputParameter__in=compatible_params).distinct()

            for next_part in next_parts:
                new_visited_params = visited_params.copy()
                new_visited_params.update(compatible_params)
                if next_part not in path:
                    dfs(next_part, path + [current_part], goal_function, new_visited_params)

        for part in parts:
            dfs(part, [], goal_function, set())
        return paths

    def format_part_paths(part_paths):
        formatted_paths = []
        for path in part_paths:
            formatted_path = {
                'parameters': [param.parameterName for param in ParameterList.objects.filter(parameterId__in=input_parameters + list(PartInputParameters.objects.filter(part__in=path).values_list('partInputParameter', flat=True)))],
                'parts': [{'partId': part.partId, 'partName': part.partName, 'partCost': part.partCost, 'partReputation': part.partReputation} for part in path]
            }
            formatted_paths.append(formatted_path)
        return formatted_paths

    input_param = input_parameters[0]
    goal_function = goal_functions[0]

    paths = get_part_paths(input_param, goal_function)
    paths_with_backward_compatibility = get_compatible_parts(input_param, goal_function)

    response_data = {
        'paths': format_part_paths(paths),
        'paths_with_bc': format_part_paths(paths_with_backward_compatibility)
    }

    return Response(response_data)




@api_view(['POST'])
def find_parts_chain_by_price(request):
    if request.method == 'POST':
        data = request.data
        initial_params = data.get('initialParameters', [])
        goal_params = data.get('goalParameters', [])    
        
        # Convert parameter IDs to ParameterList objects
        initial_params_objs = ParameterList.objects.filter(parameterId__in=initial_params)
        goal_params_objs = ParameterList.objects.filter(parameterId__in=goal_params)

        paths_with_costs = find_all_paths_with_costs(initial_params_objs, goal_params_objs)
        
        # Format the response data to include part IDs, part Names, and total cost
        formatted_paths = []
        for path, parts in paths_with_costs:
            formatted_path = {
                'parameters': [param.parameterId for param in path],
                'parts': [{'partId': part_id, 'partName': part_name, 'partCost': part_cost} for part_id, part_name, part_cost in parts],
                'totalCost': sum(part_cost for _, _, part_cost in parts)
            }
            formatted_paths.append(formatted_path)

        response_data = {'paths': formatted_paths}
        return Response(response_data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def find_parts_chain_by_reputation(request):
    data = request.data
    initial_params = data.get('initialParameters', [])
    goal_params = data.get('goalParameters', [])

    # Convert parameter IDs to ParameterList objects
    initial_params_objs = ParameterList.objects.filter(parameterId__in=initial_params)
    goal_params_objs = ParameterList.objects.filter(parameterId__in=goal_params)

    paths_with_reputation = find_all_paths_with_reputation(initial_params_objs, goal_params_objs)
    
    # Format the response data to include part IDs, part Names, and reputation
    formatted_paths = []
    for path, parts in paths_with_reputation:
        total_reputation = sum(part_reputation for _, _, part_reputation in parts)
        part_count = len(parts)
        average_reputation = total_reputation / part_count if part_count > 0 else 0

        formatted_path = {
            'parameters': [param.parameterId for param in path],
            'parts': [{'partId': part_id, 'partName': part_name, 'partReputation': part_reputation} for part_id, part_name, part_reputation in parts],
            'totalReputation': total_reputation,
            'averageReputation': average_reputation
        }
        formatted_paths.append(formatted_path)

    response_data = {'paths': formatted_paths}
    return Response(response_data, status=status.HTTP_200_OK)