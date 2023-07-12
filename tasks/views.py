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


# This is a list of all COMPLETED tasks
class CompletedTasksListView(ListView):
    model = Task
    template_name = 'tasks/completed.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # need to initialize the filter here
        context['filter'] = self.filterset
        context['title'] = 'Completed Tasks'
        context['need_filter'] = 'completed'
        return context

    def get_queryset(self):
        queryset = Task.objects.all().filter(status=Task.COMPLETED).order_by('-date_completed')
        # need to apply the filter here
        self.filterset = CompletionFilter(self.request.GET, queryset=queryset)
        if self.filterset.is_bound and self.filterset.form.is_valid():
            queryset = self.filterset.qs
        return queryset


# This is a list of all OPEN tasks
class TaskListView(ListView):
    model = Task
    template_name = 'tasks/home.html'
    context_object_name = 'tasks'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # need to initialize the filter here
        context['filter'] = self.filterset
        context['title'] = 'Open Tasks'
        context['need_filter'] = 'created'
        return context

    def get_queryset(self):
        queryset = Task.objects.all().filter(status=Task.OPEN).order_by('-date_posted')
        # need to apply the filter here
        self.filterset = CreationFilter(self.request.GET, queryset=queryset)
        if self.filterset.is_bound and self.filterset.form.is_valid():
            queryset = self.filterset.qs
        return queryset


# This is a list of Task for each specific User
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


# This is a View for the DateTime input (it has separate pickers matched to a single field)
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

        # In case time is not set, we set it to midnight
        if time_str == '':
            time_str = '00:00'

        if len(time_str) > 5:
            time_str = time_str[:5]

        my_datetime = datetime.strptime(date_str + ' ' + time_str, "%Y-%m-%d %H:%M")
        # making timezone aware
        return timezone.make_aware(my_datetime)


# This is a form for task creation
class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    fields = ['title', 'content', 'due_date', 'completer']

    # Set the widget for the due_date
    def get_form(self, form_class=None):
        form = super(TaskCreateView, self).get_form(form_class)
        form.fields['due_date'].widget = DateTimeMultiWidget() 
        return form
    
    # Set the author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    # To be able to see this form, you have to be a CREATOR
    def test_func(self):
        return self.request.user.role == User.CREATOR

    # Pass data to the html form 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-create'
        return context


# This is a form for task updates
class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    fields = ['title', 'content', 'due_date', 'completer']

    # Set the widget for the due_date
    def get_form(self, form_class=None):
        form = super(TaskUpdateView, self).get_form(form_class)
        form.fields['due_date'].widget = DateTimeMultiWidget() 
        return form
    
    # Set the author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    # To be able to see this form, you have to be the creator of the task
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author

    # Pass data to the html form 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-update'
        return context


# This is a form for task deletion
class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = '/'

    # To be able to see this form, you have to be the creator of the task
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author


# This is a form for task completion
class TaskCompleteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    fields = ['completion_comment']
    
    # Set the COMPLETER, the completion time and change the task's status
    def form_valid(self, form):
        form.instance.completer = self.request.user
        form.instance.date_completed = datetime.strftime(timezone.now(), "%Y-%m-%d %H:%M")
        form.instance.status = Task.COMPLETED
        return super().form_valid(form)

    # To be able to see this form:
    # 1. The task has to be open
    # 2. You have to be a COMPLETER
    # 3. You have to be assigned to this task
    #    OR the task can be assigned to anyone
    def test_func(self):
        task = self.get_object()
        is_task_open = task.status == Task.OPEN
        user_can_complete = self.request.user.role == User.COMPLETER
        assigned_to_me = task.completer == self.request.user
        assigned_to_anyone = task.completer == None
        return (is_task_open and user_can_complete and (assigned_to_anyone or assigned_to_me))

    # Pass data to the html form 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calling_view'] = 'task-complete'
        return context
