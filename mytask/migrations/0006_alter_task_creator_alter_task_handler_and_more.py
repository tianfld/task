# Generated by Django 4.1 on 2024-08-24 16:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mytask", "0005_task_deadline_task_is_overdue"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="creator",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="task",
            name="handler",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="task",
            name="reviewer",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
