from django.contrib import admin
from .models import Task, Assignment, Reviewer
from django.contrib.auth.models import User

# admin.site.register(Task)
admin.site.register(Assignment)
admin.site.register(Reviewer)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'attachment')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')
    readonly_fields = ('created_at',)


# 添加权限
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# 获取或创建权限
content_type = ContentType.objects.get_for_model(Task)
can_approve_tasks, created = Permission.objects.get_or_create(
    codename='can_approve_tasks',
    name='Can approve tasks',
    content_type=content_type,
)
can_manage_reviewers, created = Permission.objects.get_or_create(
    codename='can_manage_reviewers',
    name='Can manage reviewers',
    content_type=content_type,
)

# 为管理员用户添加权限
admin_user = User.objects.get(username='admin')
admin_user.user_permissions.add(can_approve_tasks, can_manage_reviewers)
