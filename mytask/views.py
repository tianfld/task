# myapp/views.py
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegisterForm, TaskForm
from .models import Task, Assignment, Reviewer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # 重定向到首页或其他页面
    else:
        form = LoginForm()
    return render(request, 'task/login.html', {'form': form})


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 自动登录新注册的用户
            return redirect('home')  # 重定向到首页或其他页面
    else:
        form = RegisterForm()
    return render(request, 'task/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')  # 重定向到登录页

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:  # 假设您使用的是 Django 的用户模型
            return view_func(request, *args, **kwargs)
        else:
            # 重定向到登录页面
            return redirect('login')
    return wrapper

@custom_login_required
def home(request):
    can_manage_reviewers = request.user.has_perm('mytask.can_manage_reviewers')
    context = {
        'can_manage_reviewers': can_manage_reviewers,
    }
    return render(request, 'task/home.html', context)


def new_task(request):
    return render(request, 'task/create_task.html')


def review_tasks(request):
    return render(request, 'task/home.html')

@custom_login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user.username
            task.status = 'REVIEWING'
            try:
                task.save()
            except Exception as e:
                messages.error(request, f'创建任务时发生错误: {e}')
                return redirect('create_task')

            # 获取派发目标用户
            target_user = request.POST.get('target_user')
            task.target_user = target_user
            task.save()
            if target_user:
                Assignment.objects.create(task_id=task.task_id, username=target_user)

            # 获取审核人
            reviewer = request.POST.get('reviewer')
            if reviewer:
                task.reviewer = reviewer
                task.save()

            messages.success(request, '任务已创建！')
            return redirect('task_list')
    else:
        form = TaskForm()

    # 获取所有用户和审核人
    users = User.objects.exclude(pk=request.user.pk).values_list('username', flat=True)
    reviewers = Reviewer.objects.all().values_list('username', flat=True)

    return render(request, 'task/create_task.html', {'form': form, 'users': users, 'reviewers': reviewers})
@custom_login_required
def task_list(request):
    tasks = []
    task_queryset = Task.objects.all()

    # 获取查询参数
    query = request.GET.get('query', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    status = request.GET.get('status', '')

    # 检查是否有清空条件的请求
    if request.GET.get('clear_filters'):
        query = ''
        start_date = ''
        end_date = ''
        status = ''

    try:
        if query:
            task_queryset = task_queryset.filter(Q(title__icontains=query) | Q(task_id__icontains=query))

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            task_queryset = task_queryset.filter(created_at__range=(start_date, end_date))

        if status and status!= '':
            task_queryset = task_queryset.filter(status=status)

        # 对每个任务编号，获取最新更新的记录
        task_ids = set()
        for task in task_queryset:
            if task.task_id not in task_ids:
                latest_task = Task.objects.filter(task_id=task.task_id).order_by('-updated_at').first()
                tasks.append(latest_task)
                task_ids.add(task.task_id)
    except Exception as e:
        # 记录可能出现的错误
        print(f"An error occurred during filtering: {e}")

    task_data = []
    for task in tasks:
        task_data.append({
            'task_id': task.task_id,
            'title': task.title,
            'created_at': task.created_at,
            'status': task.get_status_display(),
            'handler': task.handler
        })

    return render(request, 'task/task_list.html', {'tasks': task_data, 'query': query, 'start_date': start_date, 'end_date': end_date,'status': status})




# myapp/views.py
from django.conf import settings

# myapp/views.py
from django.conf import settings


@custom_login_required
def view_task(request, task_id):
    # 获取任务对象，按 updated_at 降序取第一个，确保是最新记录
    task_queryset = Task.objects.filter(task_id=task_id).order_by('-updated_at')
    task = task_queryset.first()

    if not task:
        return render(request, 'task/not_found.html')

    # 获取当前用户的分配记录
    assignment = Assignment.objects.filter(task_id=task_id, username=request.user.username).first()

    # 获取所有用户（假设您需要所有用户作为选项）
    users = User.objects.exclude(pk=request.user.pk).values_list('username', flat=True)
    reviewers = Reviewer.objects.all().values_list('username', flat=True)

    # 检查用户是否有权限进行审核
    can_approve_tasks = request.user.has_perm('mytask.can_approve_tasks')

    if request.method == 'POST':
        if task.status == 'REVIEWING':
            approval_status = request.POST.get('approval_status')
            review_comment = request.POST.get('review_comment')
            if approval_status:
                new_status = 'ASSIGNED' if approval_status == 'approved' else 'REJECTED'
                new_task = Task.objects.create(
                    task_id=task.task_id,
                    title=task.title,
                    content=task.content,
                    attachment=task.attachment,
                    creator=task.creator,
                    reviewer=task.reviewer,
                    handler=task.target_user,
                    target_user=task.target_user,
                    status=new_status,
                    deadline=task.deadline,
                    is_overdue=task.is_overdue,
                    review_comment=review_comment,
                    backup_field1=task.backup_field1,
                    backup_field2=task.backup_field2,
                    backup_field3=task.backup_field3,
                    backup_field4=task.backup_field4,
                    backup_field5=task.backup_field5,
                    backup_field6=task.backup_field6,
                    task_execution_status=task.task_execution_status,
                    reply_attachment=task.reply_attachment
                )
                return redirect('task_list')
        elif task.status == 'REJECTED':
            title = request.POST.get('title')
            content = request.POST.get('content')
            attachment = request.FILES.get('attachment')
            target_user = request.POST.get('target_user')
            reviewer = request.POST.get('reviewer')
            new_task = Task.objects.create(
                task_id=task.task_id,
                title=title,
                content=content,
                attachment=attachment if attachment else task.attachment,
                creator=task.creator,
                reviewer=reviewer if reviewer else task.reviewer,
                handler=task.handler,
                target_user=target_user if target_user else task.target_user,
                status='REVIEWING',
                deadline=task.deadline,
                is_overdue=task.is_overdue,
                review_comment=task.review_comment,
                backup_field1=task.backup_field1,
                backup_field2=task.backup_field2,
                backup_field3=task.backup_field3,
                backup_field4=task.backup_field4,
                backup_field5=task.backup_field5,
                backup_field6=task.backup_field6,
                task_execution_status=task.task_execution_status,
                reply_attachment=task.reply_attachment
            )
            return redirect('task_list')
        elif task.status == 'ASSIGNED' or task.status == 'FORWARDED':
            if 'reply_task' in request.POST:
                task_execution_status = request.POST.get('task_execution_status')
                reply_attachment = request.FILES.get('reply_attachment')
                new_task = Task.objects.create(
                    task_id=task.task_id,
                    title=task.title,
                    content=task.content,
                    attachment=task.attachment,
                    creator=task.creator,
                    reviewer=task.reviewer,
                    handler=task.handler,
                    target_user=task.target_user,
                    status='COMPLETED',
                    deadline=task.deadline,
                    is_overdue=task.is_overdue,
                    review_comment=task.review_comment,
                    backup_field1=task.backup_field1,
                    backup_field2=task.backup_field2,
                    backup_field3=task.backup_field3,
                    backup_field4=task.backup_field4,
                    backup_field5=task.backup_field5,
                    backup_field6=task.backup_field6,
                    task_execution_status=task_execution_status,
                    reply_attachment=reply_attachment if reply_attachment else task.reply_attachment
                )
                return redirect('task_list')
            elif 'forward_task' in request.POST:
                new_target_user = request.POST.get('new_target_user')
                new_task = Task.objects.create(
                    task_id=task.task_id,
                    title=task.title,
                    content=task.content,
                    attachment=task.attachment,
                    creator=task.creator,
                    reviewer=task.reviewer,
                    handler=new_target_user,
                    target_user=new_target_user,
                    status='FORWARDED',
                    deadline=task.deadline,
                    is_overdue=task.is_overdue,
                    review_comment=task.review_comment,
                    backup_field1=task.backup_field1,
                    backup_field2=task.backup_field2,
                    backup_field3=task.backup_field3,
                    backup_field4=task.backup_field4,
                    backup_field5=task.backup_field5,
                    backup_field6=task.backup_field6,
                    task_execution_status=task.task_execution_status,
                    reply_attachment=task.reply_attachment
                )
                return redirect('task_list')

    return render(request, 'task/view_task.html', {
        'task': task,
        'users': users,
        'assignment': assignment,
        'can_approve_tasks': can_approve_tasks,
        'reviewers': reviewers
    })





@custom_login_required
def manage_reviewers(request):
    if not request.user.has_perm('mytask.can_manage_reviewers'):
        raise PermissionDenied

    reviewers = Reviewer.objects.all()
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        Reviewer.objects.exclude(user__id__in=selected_users).delete()
        for user_id in selected_users:
            user = User.objects.get(id=user_id)
            Reviewer.objects.get_or_create(user=user)
        messages.success(request, '审核员列表已更新。')
        return redirect('manage_reviewers')

    all_users = User.objects.all()
    return render(request, 'mytask/manage_reviewers.html', {'reviewers': reviewers, 'all_users': all_users})