# 🧠 LLM Eval Playground
A platform for evaluating and testing Large Language Models (LLMs). Choose your model, craft prompts, run injections, and analyze responses — all in one place.
Helps you choose best model for your task. 
## 🚀 Features
- **Model Selector**  
 Easily switch between different LLM providers (e.g., OpenAI, Anthropic).
- **Prompt Execution**  
 Run custom prompts and view real-time model responses.
- **Prompt Injection Testing**  
 Test how LLMs respond to injected or adversarial inputs.
- **Cost Tracking**  
 Automatically calculates input/output tokens and estimated cost.
- **Eval Metrics**  
 View model response length, latency, and token breakdown at a glance.
## 🎯 Use Cases
- Compare how different LLMs respond to the same prompt.
- Identify weaknesses in prompt design or model behavior.
- Experiment with system prompts, injections, and few-shot strategies.
- Estimate token costs before deploying prompts to production.
## Currently Working On:
- adding RAG eval tooling (chunker eval, embedder eval, prompt eval, memory eval)
- custom BERT embedding model eval platform
- Kuberflow pipeline to fine-tune BERT embeddings for better text understanding based on company specific content. 
## 📦 Getting Started
```bash
git clone https://github.com/your-username/llm-eval-playground.git
cd llm-eval-playground
pip install -r requirements.txt
python manage.py runserver
```
Add your API keys in `.env` or `settings.py` depending on your setup.
