from rest_framework import serializers
from .models import PartDetails, ParameterList, PartInputParameters, PartOutputParameters, FunctionList, PartGoalFunctions, ParameterVersionHierarchy

class PartDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartDetails
        fields = '__all__'

class ParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterList
        fields = '__all__'

class PartInputParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartInputParameters
        fields = '__all__'

class PartOutputParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartOutputParameters
        fields = '__all__'

class FunctionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionList
        fields = '__all__'

class PartGoalFunctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartGoalFunctions
        fields = '__all__'

class ParameterVersionHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterVersionHierarchy
        fields = '__all__'
