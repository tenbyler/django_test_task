from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.shortcuts import get_object_or_404
from django.forms.widgets import NumberInput
from django.forms import MultiWidget
from django.utils import timezone
from datetime import datetime
from .models import Task
from users.models import User
from .filters import CreationFilter, CompletionFilter
import logging


class CompletedTasksListView(ListView):
    model = Task
    template_name = 'tasks/completed.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['title'] = 'Completed Tasks'
        context['need_filter'] = 'completed'
        return context

    def get_queryset(self):
        queryset = Task.objects.all().filter(status=Task.COMPLETED).order_by('-date_completed')
        self.filterset = CompletionFilter(self.request.GET, queryset=queryset)
        if self.filterset.is_bound and self.filterset.form.is_valid():
            queryset = self.filterset.qs
        return queryset


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/home.html'
    context_object_name = 'tasks'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['title'] = 'Open Tasks'
        context['need_filter'] = 'created'
        return context

    def get_queryset(self):
        queryset = Task.objects.all().filter(status=Task.OPEN).order_by('-date_posted')
        self.filterset = CreationFilter(self.request.GET, queryset=queryset)
        if self.filterset.is_bound and self.filterset.form.is_valid():
            queryset = self.filterset.qs
        return queryset


class UserTaskListView(ListView):
    model = Task
    template_name = 'tasks/user_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Task.objects.filter(author=user).order_by('-date_posted')


class TaskDetailView(DetailView):
    model = Task


class DateTimeMultiWidget(MultiWidget):
    def __init__(self, attrs=None):
        date_widget = NumberInput(attrs={'type': 'date',
                                         'class': 'form-control',
                                         'style': 'margin-right: 0.5em;'})
        time_widget = NumberInput(attrs={'type': 'time',
                                         'class': 'form-control',
                                         'style': 'margin-left: 0.5em;'})
        widgets = (date_widget, time_widget)
        super().__init__(widgets, attrs)

    def subwidgets(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        return context['widget']['subwidgets']    

    def decompress(self, value):
        if value:
            return [value.date(), value.time()]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        date_str, time_str = super().value_from_datadict(data, files, name)
        # DateField expects a single string that it can parse into a date.
        
        if date_str == time_str == '':
            return None

        if time_str == '':
            time_str = '00:00'

        if len(time_str) > 5:
            time_str = time_str[:5]

        my_datetime = datetime.strptime(date_str + ' ' + time_str, "%Y-%m-%d %H:%M")
        # making timezone aware
        return timezone.make_aware(my_datetime)


class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    fields = ['title', 'content', 'due_date', 'completer']

    def get_form(self, form_class=None):
        form = super(TaskCreateView, self).get_form(form_class)
        form.fields['due_date'].widget = DateTimeMultiWidget() 
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        return self.request.user.role == User.CREATOR

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-create'
        return context


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    fields = ['title', 'content', 'due_date', 'completer']

    def get_form(self, form_class=None):
        form = super(TaskUpdateView, self).get_form(form_class)
        form.fields['due_date'].widget = DateTimeMultiWidget() 
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-update'
        return context


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = '/'

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author


class TaskCompleteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    fields = ['completion_comment']
    
    def form_valid(self, form):
        form.instance.completer = self.request.user
        form.instance.date_completed = datetime.strftime(timezone.now(), "%Y-%m-%d %H:%M")
        form.instance.status = Task.COMPLETED
        return super().form_valid(form)

    def test_func(self):
        task = self.get_object()
        is_task_open = task.status == Task.OPEN
        user_can_complete = self.request.user.role == User.COMPLETER
        assigned_to_me = task.completer == self.request.user
        assigned_to_anyone = task.completer == None
        return (is_task_open and user_can_complete and (assigned_to_anyone or assigned_to_me))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-complete'
        return context
