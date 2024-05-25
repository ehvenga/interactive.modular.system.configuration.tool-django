# Generated by Django 5.0.4 on 2024-05-25 20:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FunctionList',
            fields=[
                ('functionId', models.AutoField(primary_key=True, serialize=False)),
                ('functionName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PartGoalFunctions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.partdetails')),
                ('partGoalFunction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.functionlist')),
            ],
        ),
    ]