from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
import time
import tiktoken
from openai import OpenAI
import anthropic
from django.conf import settings
from .models import PromptRun
from .utils import run_prompt
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_token_count(text, model="gpt-3.5-turbo"):
    """Get the number of tokens in a text string."""
    try:
        if model.startswith("claude"):
            # Claude uses a different tokenizer, but we can use GPT-3.5's as an approximation
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback to cl100k_base encoding if model not found
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def get_model_cost(model, input_tokens, output_tokens):
    """Calculate the cost based on the model and token counts."""
    costs = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
    }
    
    if model not in costs:
        return 0
    
    return (input_tokens * costs[model]["input"] + 
            output_tokens * costs[model]["output"]) / 1000

# Create your views here.

@login_required
def editor(request):
    return render(request, 'prompts/editor.html')

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def run_prompt(request):
    try:
        data = json.loads(request.body)
        template = data.get('template', '')
        variables = data.get('variables', {})
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = float(data.get('temperature', 0.7))
        max_tokens = int(data.get('max_tokens', 1000))

        print(f"Received model name: {model}")  # Debug log

        # Validate template
        if not template:
            return JsonResponse({
                'status': 'error',
                'message': 'Prompt template cannot be empty'
            })

        # Replace variables in template
        prompt = template
        for var_name, var_value in variables.items():
            prompt = prompt.replace(f"{{{{{var_name}}}}}", str(var_value))

        # Get input token count
        input_tokens = get_token_count(prompt, model)

        # Call appropriate API based on model
        start_time = time.time()
        
        if model.startswith("claude"):
            # Call Anthropic API
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            response_text = response.content[0].text
            output_tokens = response.usage.output_tokens
            total_tokens = response.usage.input_tokens + response.usage.output_tokens
        else:
            # Call OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            response_text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

        end_time = time.time()

        # Calculate metrics
        response_time = end_time - start_time
        cost = get_model_cost(model, input_tokens, output_tokens)

        return JsonResponse({
            'status': 'success',
            'data': {
                'response': response_text,
                'metrics': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': total_tokens,
                    'cost': cost,
                    'response_time': response_time
                }
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

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
