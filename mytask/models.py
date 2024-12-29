from django.db import models
import string
import random
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


def generate_unique_task_id():
    # 生成一个唯一且未使用的任务编号
    models_imported = False
    while True:
        # 使用 UUID 生成唯一编号，前缀为 "T-"
        task_id = "T-" + str(uuid.uuid4()).replace('-', '')[:6]

        if not Task.objects.filter(task_id=task_id).exists():
            return task_id


class Task(models.Model):
    task_id = models.CharField(max_length=10, unique=False, default=generate_unique_task_id)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    creator = models.CharField(max_length=150, blank=True, null=True)
    reviewer = models.CharField(max_length=150, blank=True, null=True)
    handler = models.CharField(max_length=150, blank=True, null=True)
    target_user = models.CharField(max_length=150, blank=True, null=True)
    status_choices = [
        ('REVIEWING', '审核中'),
        ('REJECTED', '已退回'),
        ('ASSIGNED', '已派发'),
        ('FORWARDED', '已转发'),
        ('COMPLETED', '已完成'),
    ]
    status = models.CharField(max_length=15, choices=status_choices, default='REVIEWING')
    # 添加任务截止时间字段
    deadline = models.DateTimeField(null=True, blank=True, help_text="任务的截止日期和时间")
    # 添加是否超时字段
    is_overdue = models.BooleanField(default=False)
    # 新增审核意见字段
    review_comment = models.TextField(blank=True, null=True)
    # 新增备用字段
    backup_field1 = models.CharField(max_length=100, blank=True, null=True)
    backup_field2 = models.CharField(max_length=100, blank=True, null=True)
    backup_field3 = models.CharField(max_length=100, blank=True, null=True)
    backup_field4 = models.CharField(max_length=100, blank=True, null=True)
    backup_field5 = models.CharField(max_length=100, blank=True, null=True)
    backup_field6 = models.CharField(max_length=100, blank=True, null=True)
    # 新增任务执行情况字段
    task_execution_status = models.TextField(blank=True, null=True)
    # 新增答复附件字段
    reply_attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 如果任务有截止时间并且当前时间超过截止时间，则设置为超时
        if self.deadline and self.deadline < timezone.now():
            self.is_overdue = True
        # 更新 handler 字段
        if self.status == 'REVIEWING':
            self.handler = self.reviewer
        elif self.status == 'REJECTED':
            self.handler = self.creator
        elif self.status == 'ASSIGNED':
            self.handler = self.target_user
        elif self.status == 'FORWARDED':
            self.handler = self.target_user
        elif self.status == 'COMPLETED':
            self.handler = self.creator
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.task_id})"

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at']


class Assignment(models.Model):
    task_id = models.CharField(max_length=10, db_index=True, default=generate_unique_task_id)
    username = models.CharField(max_length=150, null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.task_id}"


class Reviewer(models.Model):
    username = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - 审核员"