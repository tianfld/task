"""task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from mytask import views
from mytask.views import user_login, user_register, home
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', home, name='home'),  # 添加主页 URL
    path('new-task/', views.new_task, name='new_task'),  # 注意这里的名称
    path('task-list/', views.task_list, name='task_list'),
    path('review-tasks/', views.review_tasks, name='review_tasks'),
    path('create/', views.create_task, name='create_task'),
    path('view-task/', views.view_task, name='view_task'),
    path('view-task/<str:task_id>/', views.view_task, name='view_task'),
#   path('view-task/<str:task_id>/', views.view_task, name='view_task'),
    path('manage-reviewers/', views.manage_reviewers, name='manage_reviewers'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)