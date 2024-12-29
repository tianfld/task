# Generated by Django 4.1 on 2024-10-02 05:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mytask", "0008_task_target_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="backup_field1",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="backup_field2",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="backup_field3",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="backup_field4",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="backup_field5",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="backup_field6",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="reply_attachment",
            field=models.FileField(
                blank=True, null=True, upload_to="task_attachments/"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="review_comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="task_execution_status",
            field=models.TextField(blank=True, null=True),
        ),
    ]
