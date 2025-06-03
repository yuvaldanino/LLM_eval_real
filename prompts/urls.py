from django.urls import path
from . import views

app_name = 'prompts'

urlpatterns = [
    path('editor/', views.editor, name='editor'),
    path('run/', views.run_prompt, name='run_prompt'),
    path('history/', views.prompt_history, name='prompt_history'),
    path('history/clear/', views.clear_history, name='clear_history'),
] 