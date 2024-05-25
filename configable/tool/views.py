from django.shortcuts import render
from rest_framework import generics
from .models import ParameterList
from .serializers import ParameterListSerializer, FunctionListSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import PartInputParameters, PartOutputParameters, PartDetails, ParameterList, FunctionList
import networkx as nx
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import find_all_paths_with_costs, find_all_paths_with_reputation, find_all_paths, find_all_paths_v2

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