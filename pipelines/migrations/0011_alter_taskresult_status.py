# Generated by Django 4.1.3 on 2023-01-18 09:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0010_remove_taskexecution_pipeline_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taskresult",
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
    ]