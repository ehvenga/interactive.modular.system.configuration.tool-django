from django.contrib import admin
from .models import PartDetails, ParameterList, PartInputParameters, PartOutputParameters, FunctionList, PartGoalFunctions, ParameterVersionHierarchy

admin.site.register(PartDetails)
admin.site.register(ParameterList)
admin.site.register(PartInputParameters)
admin.site.register(PartOutputParameters)
admin.site.register(FunctionList)
admin.site.register(PartGoalFunctions)
admin.site.register(ParameterVersionHierarchy)
