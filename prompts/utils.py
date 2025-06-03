import time
import tiktoken
from openai import OpenAI
from django.conf import settings

def get_token_count(text, model="gpt-3.5-turbo"):
    """Count the number of tokens in a text using the specified model's encoding."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_model_cost(model_name, input_tokens, output_tokens):
    """Calculate the cost of a model run based on token counts."""
    # Cost per 1K tokens (as of 2024)
    costs = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06}
    }
    
    if model_name not in costs:
        raise ValueError(f"Unknown model: {model_name}")
    
    input_cost = (input_tokens / 1000) * costs[model_name]["input"]
    output_cost = (output_tokens / 1000) * costs[model_name]["output"]
    
    return input_cost + output_cost

def run_prompt(template, variables, model_name):
    """Run a prompt through the OpenAI API and return the results."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Replace variables in template
    prompt = template
    for var_name, var_value in variables.items():
        prompt = prompt.replace(f"{{{{{var_name}}}}}", str(var_value))
    
    # Count input tokens
    input_tokens = get_token_count(prompt, model_name)
    
    # Start timing
    start_time = time.time()
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Get response text
        response_text = response.choices[0].message.content
        
        # Calculate metrics
        output_tokens = get_token_count(response_text, model_name)
        total_tokens = input_tokens + output_tokens
        cost = get_model_cost(model_name, input_tokens, output_tokens)
        response_time = time.time() - start_time
        
        return {
            "response": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
            "response_time": response_time
        }
        
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}") 