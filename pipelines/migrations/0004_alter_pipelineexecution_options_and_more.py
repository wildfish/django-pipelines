# Generated by Django 4.1.2 on 2022-12-18 21:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0003_alter_pipelineexecution_reporter_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pipelineexecution",
            options={"ordering": ["-started"]},
        ),
        migrations.AlterUniqueTogether(
            name="taskresult",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="pipelineexecution",
            name="serializable_pipeline_object",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="taskresult",
            name="serializable_pipeline_object",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="taskresult",
            name="serializable_task_object",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="pipelineexecution",
            name="run_id",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="pipelineexecution",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "PENDING"),
                    ("RUNNING", "RUNNING"),
                    ("DONE", "DONE"),
                    ("CONFIG_ERROR", "CONFIG_ERROR"),
                    ("VALIDATION_ERROR", "VALIDATION_ERROR"),
                    ("RUNTIME_ERROR", "RUNTIME_ERROR"),
                    ("CANCELLED", "CANCELLED"),
                ],
                default="PENDING",
                max_length=255,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="pipelineexecution",
            unique_together={("run_id", "serializable_pipeline_object")},
        ),
    ]
