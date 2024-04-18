from django.shortcuts import render
from rest_framework import generics
from .models import ParameterList
from .serializers import ParameterListSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import PartInputParameters, PartOutputParameters, PartDetails, ParameterList
from .serializers import PartDetailsSerializer
import networkx as nx
from rest_framework import status
from rest_framework.decorators import api_view
from .utils import find_all_paths
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import find_all_paths_with_costs  # We'll define this function next

class ParameterListView(generics.ListAPIView):
    queryset = ParameterList.objects.all()
    serializer_class = ParameterListSerializer

@api_view(['POST'])
def find_parts_chain(request):
    if request.method == 'POST':
        data = request.data
        initial_params = data.get('initialParameters', [])
        goal_params = data.get('goalParameters', [])
        
        # Convert parameter IDs to ParameterList objects
        initial_params_objs = ParameterList.objects.filter(parameterId__in=initial_params)
        goal_params_objs = ParameterList.objects.filter(parameterId__in=goal_params)
        
        paths = find_all_paths(initial_params_objs, goal_params_objs)
    
        # Format the response data to include part IDs
        formatted_paths = []
        for path, parts in paths:
            formatted_path = {
                'parameters': [param.parameterId for param in path],
                'parts': [{'partId': part_id, 'partName': part_name} for part_id, part_name in parts]
            }
            formatted_paths.append(formatted_path)

        
        response_data = {'paths': formatted_paths}
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