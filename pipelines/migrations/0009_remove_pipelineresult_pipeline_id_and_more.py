# Generated by Django 4.1.3 on 2023-01-16 14:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0008_auto_20230116_1208"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pipelineresult",
            name="pipeline_id",
        ),
        migrations.RemoveField(
            model_name="pipelineresult",
            name="run_id",
        ),
        migrations.RemoveField(
            model_name="taskresult",
            name="pipeline_id",
        ),
        migrations.RemoveField(
            model_name="taskresult",
            name="run_id",
        ),
        migrations.RemoveField(
            model_name="taskresult",
            name="serializable_pipeline_object",
        ),
        migrations.RemoveField(
            model_name="taskresult",
            name="task_id",
        ),
    ]
