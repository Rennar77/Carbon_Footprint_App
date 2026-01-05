# app/services/ai_services.py
import os
import logging
import re
from typing import Dict, Any
import google.genai as genai 
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API 
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logging.warning("GEMINI_API_KEY not set. AI features will use fallback.")
    gemini_client = None
else:
    try:
        
        client = genai.Client(api_key=gemini_api_key)
        
        # Test with a simple model - use gemini-2.0-flash-001 (stable version)
        test_model = "gemini-2.0-flash-001"
        gemini_client = client
        gemini_model = test_model
        
        logging.info(f"Gemini API configured successfully with model: {test_model}")
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        gemini_client = None
        gemini_model = None


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
    if not gemini_client or not gemini_model:
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
        # NEW API call format
        response = gemini_client.models.generate_content(
            model=gemini_model,
            contents=prompt,
            config={
                "max_output_tokens": 100,
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
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


# Alternative: Using async version
async def generate_recommendation_async(user_summary: Dict[str, Any]) -> str:
    """Async version using the new package."""
    if not gemini_client or not gemini_model:
        return get_fallback_recommendation(user_summary)
    
    summary_str = ", ".join(f"{k}: {v}" for k, v in user_summary.items())
    
    prompt = f"Give one short sustainability recommendation based on: {summary_str}. One sentence only."
    
    try:
        response = await gemini_client.aio.models.generate_content(
            model=gemini_model,
            contents=prompt,
            config={
                "max_output_tokens": 100,
                "temperature": 0.3,
            }
        )
        
        return clean_gemini_response(response.text)
        
    except Exception as e:
        logging.error(f"Async Gemini API failed: {e}")
        return get_fallback_recommendation(user_summary)


# Simple test function
def test_gemini_connection():
    """Test if Gemini API is working."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        return False
    
    try:
        # NEW package initialization
        client = genai.Client(api_key=api_key)
        
        # Try with gemini-2.0-flash-001 (stable version from your list)
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents="Say 'Hello' in one sentence.",
            config={"max_output_tokens": 50}
        )
        
        print(f"✅ Gemini API connected successfully!")
        print(f"   Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False


# List available models (updated for new package)
def list_available_models():
    """List all available Gemini models with new package."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY in .env file")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        
        print("Available models that support generate_content:")
        models = client.models.list()
        
        for model in models:
            if 'generate_content' in model.supported_generation_methods:
                print(f"\n- {model.name}")
                print(f"  Display: {model.display_name}")
                print(f"  Description: {model.description}")
                
    except Exception as e:
        print(f"Error listing models: {e}")