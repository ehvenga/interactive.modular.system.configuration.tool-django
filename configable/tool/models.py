from django.db import models

class PartDetails(models.Model):
    partId = models.AutoField(primary_key=True)
    partName = models.CharField(max_length=255)
    partCost = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    partReputation = models.IntegerField(default=5)
    partLead = models.IntegerField(default=5)

class ParameterList(models.Model):
    parameterId = models.AutoField(primary_key=True)
    parameterName = models.CharField(max_length=255)

class PartInputParameters(models.Model):
    part = models.ForeignKey(PartDetails, on_delete=models.CASCADE)
    partInputParameter = models.ForeignKey(ParameterList, on_delete=models.CASCADE)

class PartOutputParameters(models.Model):
    part = models.ForeignKey(PartDetails, on_delete=models.CASCADE)
    partOutputParameter = models.ForeignKey(ParameterList, on_delete=models.CASCADE)

class FunctionList(models.Model):
    functionId = models.AutoField(primary_key=True)
    functionName = models.CharField(max_length=255)

class PartGoalFunctions(models.Model):
    part = models.ForeignKey(PartDetails, on_delete=models.CASCADE)
    partGoalFunction = models.ForeignKey(FunctionList, on_delete=models.CASCADE)

class ParameterVersionHierarchy(models.Model):
    parentParameter = models.ForeignKey(ParameterList, related_name='children', on_delete=models.CASCADE)
    childParameter = models.ForeignKey(ParameterList, related_name='parents', on_delete=models.CASCADE)
