from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('processes/', views.processes, name='processes'),
    path('processes/add',views.add_process,name='add_process'),
    path('process/edit/<int:id>',views.edit_process,name='edit_process'),
    path('tasks/',views.tasks,name='tasks'),
    path('tasks/add',views.add_task,name='add_task'),
    path('task/<int:id>',views.task_view,name='task_view'),
    
    path('activity/confirm/<int:id>',views.confirm_activity,name='confirm_activity'),
    path('activity/refer/<int:id>',views.refer_activity,name='refer_activity'),
]
