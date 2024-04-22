from .models import PartInputParameters, PartOutputParameters, ParameterList, PartDetails

def find_all_paths(start_params, goal_params):
    paths = []
    queue = [([start_param], []) for start_param in start_params]  # Stores a tuple of current path and parts
    while queue:
        current_path, current_parts = queue.pop(0)
        current_param = current_path[-1]
        if current_param in goal_params:
            paths.append((current_path, current_parts))
            continue
        # Fetching related parts and parameters
        connected_parts = PartInputParameters.objects.filter(
            partInputParameter=current_param
        ).select_related('part').all()

        for entry in connected_parts:
            part = entry.part
            part_id = part.partId
            part_name = part.partName
            # Assuming PartOutputParameters is related to PartDetails via a ForeignKey with a default related_name
            for output in part.partoutputparameters_set.all():
                next_param = output.partOutputParameter
                if next_param and not any(next_param == p.parameterId for p in current_path):
                    # Avoiding cycles by checking if we already visited this parameter
                    next_param_obj = ParameterList.objects.get(parameterId=next_param.parameterId)
                    queue.append((current_path + [next_param_obj], current_parts + [(part_id, part_name)]))

    return paths

def find_all_paths_v2(start_params, goal_params):
    paths = []
    queue = [([start_param], []) for start_param in start_params]  # Stores a tuple of current path and parts

    while queue:
        current_path, current_parts = queue.pop(0)
        current_param = current_path[-1]
        if current_param in goal_params:
            paths.append((current_path, current_parts))
            continue
        # Fetching related parts and parameters
        connected_parts = PartInputParameters.objects.filter(
            partInputParameter=current_param
        ).select_related('part').all()

        for entry in connected_parts:
            part = entry.part
            part_id = part.partId
            part_name = part.partName
            for output in part.partoutputparameters_set.all():
                next_param = output.partOutputParameter
                if next_param and not any(next_param == p.parameterId for p in current_path):
                    # Avoiding cycles by checking if we already visited this parameter
                    next_param_obj = ParameterList.objects.get(parameterId=next_param.parameterId)
                    queue.append((current_path + [next_param_obj], current_parts + [(part_id, part_name)]))

    # Splitting each found path into sub-paths of only two parameters
    split_paths = []
    unique_paths = set()  # To keep track of unique sub-paths

    for path, parts in paths:
        seen_parts = set()  # To keep track of parts and avoid duplicates
        for i in range(len(path) - 1):
            sub_path = path[i:i + 2]
            sub_parts = []
            if i < len(parts):
                part_id, part_name = parts[i]
                if part_id not in seen_parts:
                    sub_parts.append((part_id, part_name))
                    seen_parts.add(part_id)
            if len(sub_path) == 2:  # Ensuring each sub-path is valid
                sub_path_tuple = (tuple(sub_path), tuple(sub_parts))
                if sub_path_tuple not in unique_paths:
                    unique_paths.add(sub_path_tuple)
                    split_paths.append((sub_path, sub_parts))

    return split_paths

def find_all_paths_with_costs(start_params, goal_params):
    paths_with_costs = []
    queue = [([start_param], []) for start_param in start_params]  # Stores a tuple of current path and parts with costs
    while queue:
        current_path, current_parts_with_costs = queue.pop(0)
        current_param = current_path[-1]
        if current_param in goal_params:
            paths_with_costs.append((current_path, current_parts_with_costs))
            continue
        connected_parts = PartInputParameters.objects.filter(
            partInputParameter=current_param
        ).select_related('part').all()

        for entry in connected_parts:
            part = entry.part
            part_id = part.partId
            part_name = part.partName
            part_cost = part.partCost  # Assume this field exists on PartDetails model
            for output in part.partoutputparameters_set.all():
                next_param = output.partOutputParameter
                if next_param and not any(next_param == p.parameterId for p in current_path):
                    next_param_obj = ParameterList.objects.get(parameterId=next_param.parameterId)
                    queue.append((
                        current_path + [next_param_obj],
                        current_parts_with_costs + [(part_id, part_name, part_cost)]
                    ))

    return paths_with_costs

def find_all_paths_with_reputation(start_params, goal_params):
    paths_with_reputation = []
    queue = [([start_param], []) for start_param in start_params]  # Stores a tuple of current path and parts with reputations
    while queue:
        current_path, current_parts_with_reputation = queue.pop(0)
        current_param = current_path[-1]
        if current_param in goal_params:
            paths_with_reputation.append((current_path, current_parts_with_reputation))
            continue
        connected_parts = PartInputParameters.objects.filter(
            partInputParameter=current_param
        ).select_related('part').all()

        for entry in connected_parts:
            part = entry.part
            part_id = part.partId
            part_name = part.partName
            part_reputation = part.partReputation  # Assume this field exists on PartDetails model
            for output in part.partoutputparameters_set.all():
                next_param = output.partOutputParameter
                if next_param and not any(next_param == p.parameterId for p in current_path):
                    next_param_obj = ParameterList.objects.get(parameterId=next_param.parameterId)
                    queue.append((
                        current_path + [next_param_obj],
                        current_parts_with_reputation + [(part_id, part_name, part_reputation)]
                    ))

    return paths_with_reputation

