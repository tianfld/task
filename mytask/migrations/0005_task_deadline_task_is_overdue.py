# Generated by Django 4.1 on 2024-08-24 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mytask", "0004_alter_task_options_remove_task_assignees_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="deadline",
            field=models.DateTimeField(blank=True, help_text="任务的截止日期和时间", null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="is_overdue",
            field=models.BooleanField(default=False),
        ),
    ]
