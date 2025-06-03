from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import PromptRun
from .utils import run_prompt

# Create your views here.

@login_required
def prompt_editor(request):
    """View for the prompt editor page."""
    return render(request, 'prompts/editor.html')

@login_required
@require_http_methods(['POST'])
def run_prompt_view(request):
    """API endpoint to run a prompt."""
    try:
        data = json.loads(request.body)
        template = data.get('template')
        variables = data.get('variables', {})
        model_name = data.get('model')
        
        if not all([template, model_name]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)
        
        # Run the prompt
        result = run_prompt(template, variables, model_name)
        
        # Save the run
        prompt_run = PromptRun.objects.create(
            user=request.user,
            template=template,
            variables=variables,
            model_name=model_name,
            response=result['response'],
            input_tokens=result['input_tokens'],
            output_tokens=result['output_tokens'],
            total_tokens=result['total_tokens'],
            cost=result['cost'],
            response_time=result['response_time']
        )
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': prompt_run.id,
                'response': result['response'],
                'metrics': {
                    'input_tokens': result['input_tokens'],
                    'output_tokens': result['output_tokens'],
                    'total_tokens': result['total_tokens'],
                    'cost': float(result['cost']),
                    'response_time': result['response_time']
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def prompt_history(request):
    """View for the prompt history page."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # API endpoint for AJAX requests
        page = request.GET.get('page', 1)
        runs = PromptRun.objects.filter(user=request.user)
        paginator = Paginator(runs, 10)
        
        try:
            page_obj = paginator.page(page)
            history = [{
                'id': run.id,
                'template': run.template,
                'variables': run.variables,
                'model': run.model_name,
                'tokens': run.total_tokens,
                'cost': float(run.cost),
                'created_at': run.created_at.isoformat()
            } for run in page_obj]
            
            return JsonResponse({
                'status': 'success',
                'history': history,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_pages': paginator.num_pages
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # Regular page view
    return render(request, 'prompts/history.html')

@login_required
@require_http_methods(['POST'])
def clear_history(request):
    """API endpoint to clear prompt history."""
    try:
        PromptRun.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
