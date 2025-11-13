# app/services/ai_services.py
import os
import logging
from typing import Dict, Any
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Hugging Face client
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    logging.warning("HF_TOKEN not set")
    client = None
else:
    client = InferenceClient(api_key=hf_token)

async def generate_recommendation(user_summary: Dict[str, Any]) -> str:
    """
    Generate a concise, actionable sustainability recommendation.
    """
    if not client:
        logging.warning("Hugging Face client not initialized, using fallback.")
        return "Try reducing your driving emissions by combining short trips this week."

    prompt = f"""
You are a friendly sustainability coach. 
Given the following user summary: {user_summary}, 
provide **exactly one actionable recommendation** the user can do in the next week to reduce their carbon footprint. 
**Do not include any reasoning, explanations, or internal thoughts.** 
Respond in **plain text only**, suitable to show directly to the user.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",  # valid model name
            messages=[
                {"role": "system", "content": "You are a friendly sustainability coach."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        # Hugging Face response object
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"Hugging Face API request failed: {e}")
        return "Try reducing your driving emissions by combining short trips this week."
