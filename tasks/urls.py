from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='tasks-home'),
    path('user/<str:username>', views.UserTaskListView.as_view(), name='user-tasks'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('task/new/', views.TaskCreateView.as_view(), name='task-create'),
    path('task/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('task/<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task-complete'),
    path('completed/', views.CompletedTasksListView.as_view(), name='tasks-completed'),
]