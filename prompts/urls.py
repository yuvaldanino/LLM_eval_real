from django.urls import path
from . import views

app_name = 'prompts'

urlpatterns = [
    path('', views.prompt_editor, name='prompt_editor'),
    path('run/', views.run_prompt_view, name='run_prompt'),
    path('history/', views.prompt_history, name='prompt_history'),
    path('history/clear/', views.clear_history, name='clear_history'),
] 