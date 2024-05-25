from rest_framework import serializers
from .models import ParameterList, PartDetails, FunctionList

class ParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterList
        fields = '__all__'  # Serialize all fields from the model
class FunctionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionList
        fields = '__all__'  # Serialize all fields from the model

class PartDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartDetails
        fields = '__all__'
