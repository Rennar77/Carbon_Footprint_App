# app/services/ai_services.py
import os
import logging
import re
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logging.warning("GEMINI_API_KEY not set. AI features will use fallback.")
    gemini_client = None
else:
    try:
        genai.configure(api_key=gemini_api_key)
        # Use gemini-1.5-flash for faster responses (free tier eligible)
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        logging.info("Gemini API configured successfully")
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        gemini_client = None


def clean_gemini_response(text: str) -> str:
    """Cleans Gemini API response text."""
    if not text:
        return text
    
    # Remove markdown formatting if present
    cleaned = re.sub(r'\*\*|\*|`', '', text)
    # Remove any numbering like "1. ", "2. ", etc.
    cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
    # Remove common AI prefixes
    cleaned = re.sub(r'^(Here\'s|Sure|Alright|Okay|Great|Certainly)[,:]\s*', '', cleaned, flags=re.IGNORECASE)
    # Ensure it ends with a period
    cleaned = cleaned.strip()
    if not cleaned.endswith('.'):
        cleaned += '.'
    
    return cleaned


async def generate_recommendation(user_summary: Dict[str, Any]) -> str:
    """
    Generate a concise, actionable sustainability recommendation.
    The output is a single sentence in plain text.
    """
    if not gemini_client:
        logging.warning("Gemini client not initialized, using fallback.")
        return get_fallback_recommendation(user_summary)

    # Transform the summary into a short structured string
    summary_str = ", ".join(f"{k}: {v}" for k, v in user_summary.items())
    
    prompt = f"""
You are a friendly sustainability coach providing personalized carbon reduction advice.

User's weekly carbon footprint summary:
{summary_str}

Provide exactly ONE short, actionable recommendation the user can implement THIS WEEK to lower their carbon footprint.

RULES:
- Output ONLY ONE sentence in plain text
- Make it specific to the user's data
- Focus on the most impactful change they can make
- Use simple, encouraging language
- Do NOT include any explanations, disclaimers, or markdown formatting
- Do NOT say "Here is a recommendation" or similar phrases
- Just give the direct recommendation

Example outputs:
- "Try cycling to work twice this week instead of driving."
- "Reduce your electricity use by turning off lights in empty rooms."
- "Consider having one meat-free day this week."
"""

    try:
        # Generate content with Gemini
        response = gemini_client.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': 100,
                'temperature': 0.3,  # Slightly creative but mostly deterministic
                'top_p': 0.8,
                'top_k': 40,
            },
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        raw_text = response.text
        
        # Clean the response
        cleaned_text = clean_gemini_response(raw_text)
        
        # Ensure it's a single sentence
        sentences = cleaned_text.split('.')
        if len(sentences) > 1:
            # Take only the first complete sentence
            cleaned_text = sentences[0].strip() + '.'
        
        # Final validation
        if len(cleaned_text.split()) > 25:  # If too long, simplify
            cleaned_text = "Try reducing your highest emission activity this week."
            
        return cleaned_text
        
    except Exception as e:
        logging.error(f"Gemini API request failed: {e}")
        return get_fallback_recommendation(user_summary)


def get_fallback_recommendation(user_summary: Dict[str, Any]) -> str:
    """Generate a simple fallback recommendation based on user data."""
    fallbacks = [
        "Try reducing your driving emissions by combining short trips this week.",
        "Consider having one meat-free day this week to lower your food emissions.",
        "Turn off electronics when not in use to reduce electricity consumption.",
        "Take public transport or carpool for your next commute.",
        "Use a reusable water bottle instead of buying plastic ones.",
    ]
    
    # Try to pick a relevant fallback based on user data
    summary_str = str(user_summary).lower()
    
    if 'car' in summary_str or 'drive' in summary_str or 'vehicle' in summary_str:
        return fallbacks[0]
    elif 'electricity' in summary_str or 'power' in summary_str or 'kwh' in summary_str:
        return fallbacks[2]
    elif 'flight' in summary_str or 'plane' in summary_str:
        return fallbacks[3]
    elif 'food' in summary_str or 'cooking' in summary_str or 'meal' in summary_str:
        return fallbacks[1]
    else:
        return fallbacks[4]


# Alternative: Google AI Studio API (older version)
async def generate_recommendation_google_ai_studio(user_summary: Dict[str, Any]) -> str:
    """
    Alternative using Google AI Studio API (if you prefer that interface)
    """
    import requests
    
    api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return get_fallback_recommendation(user_summary)
    
    summary_str = ", ".join(f"{k}: {v}" for k, v in user_summary.items())
    
    prompt = f"Give one short sustainability recommendation based on: {summary_str}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        
        return clean_gemini_response(text)
        
    except Exception as e:
        logging.error(f"Google AI Studio API failed: {e}")
        return get_fallback_recommendation(user_summary)