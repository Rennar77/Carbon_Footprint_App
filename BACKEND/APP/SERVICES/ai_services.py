# app/services/ai_services.py
import os
import logging
import re
from typing import Dict, Any
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    logging.warning("HF_TOKEN not set")
    client = None
else:
    client = InferenceClient(api_key=hf_token)


def remove_think_tags(text: str) -> str:
    """Removes <think>...</think> reasoning traces from DeepSeek output."""
    if not text:
        return text
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = cleaned.replace("<think>", "").replace("</think>", "")
    return cleaned.strip()


async def generate_recommendation(user_summary: Dict[str, Any]) -> str:
    """
    Generate a concise, actionable sustainability recommendation.
    The output is a single sentence in plain text.
    """
    if not client:
        logging.warning("Hugging Face client not initialized, using fallback.")
        return "Try reducing your driving emissions by combining short trips this week."

    # Transform the summary into a short structured string
    summary_str = ", ".join(f"{k}: {v}" for k, v in user_summary.items())

    prompt = f"""
You are a friendly sustainability coach.

Given the following user summary: {summary_str}

Provide **exactly one short actionable recommendation** the user can do *this week* to lower their carbon footprint.

**RULES:**
- Only output **one sentence**, in plain text.
- Do **not** include any reasoning, explanations, or <think> tags.
- Do not include multiple options; choose the **most impactful single action**.
- Return the text directly, ready to display to the user.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You provide one direct sustainability recommendation, no reasoning."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.0,  # deterministic output
        )

        raw_text = response.choices[0].message["content"]

        # Remove any stray <think> tags
        cleaned_text = remove_think_tags(raw_text)

        # Ensure only the first sentence is returned
        first_sentence = cleaned_text.split(".")[0].strip() + "."
        return first_sentence

    except Exception as e:
        logging.error(f"Hugging Face API request failed: {e}")
        return "Try reducing your driving emissions by combining short trips this week."
