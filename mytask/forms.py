from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=254,
                               widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# 新建任务表单
class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(required=True, input_formats=['%Y-%m-%dT%H:%M'])  # 添加 deadline 字段

    class Meta:
        model = Task
        fields = ['title', 'content', 'attachment', 'deadline']  # 添加 deadline 到 fields 中
        labels = {
            'title': '任务标题',
            'content': '任务具体内容',
            'attachment': '附件',
            'deadline': '截至日期',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'deadline': forms.DateTimeInput(  # 使用 DateTimeInput 替换原来的 Textarea
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
        }
