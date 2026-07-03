import os
import logging
import json
from google import genai

logger = logging.getLogger("ai_summarizer")

def rule_based_summary(data):
    brand = data['brand'].capitalize()
    return f"{brand} received {data['total_mentions']} mentions this week. Negative sentiment is at {data['negative_ratio']:.1f}%. {data['top_risk']} On the positive side, {data['top_opportunity']}"

def generate_summary(data):
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or "your_gemini" in api_key.lower():
        logger.info("No valid Gemini API key found. Using rule-based fallback summary.")
        return rule_based_summary(data)
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Analyze the following data for {data['brand'].capitalize()} and generate a short, professional executive summary (max 3 sentences) suitable for a Business Intelligence dashboard.
        Total Mentions: {data['total_mentions']}
        Negative Sentiment Ratio: {data['negative_ratio']:.1f}%
        Top Risk: {data['top_risk']}
        Top Opportunity: {data['top_opportunity']}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini API failed: {e}. Falling back to rule-based summary.")
        return rule_based_summary(data)

def _fallback_opportunity(brand: str, topic_summary: str | None, aspect_summary: str | None) -> dict:
    if topic_summary:
        summary = f"Users are discussing {topic_summary}."
    elif aspect_summary:
        summary = f"Users noted {aspect_summary}."
    else:
        summary = f"No clear new feature requests detected for {brand.capitalize()}."
        
    return {
        "summary": summary,
        "opportunities": []
    }

def extract_innovation_opportunities(
    reviews_texts: list[str],
    brand: str,
    topic_summary: str | None = None,
    aspect_summary: str | None = None
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or "your_gemini" in api_key.lower():
        logger.info("No valid Gemini API key found. Using fallback opportunity extraction.")
        return _fallback_opportunity(brand, topic_summary, aspect_summary)
        
    try:
        client = genai.Client(api_key=api_key)
        
        reviews_block = "\n".join([f"- {r}" for r in reviews_texts[:100]])
        
        prompt = f"""
You are a senior product strategist.
Analyze these customer reviews for {brand}.
Identify:
1. Repeated unmet needs
2. Frequently requested features
3. Product improvements users want
4. Innovation opportunities
5. Competitor gaps mentioned by users

Ignore isolated complaints that appear only once.
Focus on patterns that occur across multiple reviews.

Reviews:
{reviews_block}

Return ONLY valid JSON:
{{
"summary": "One concise executive-level insight in 1-2 sentences.",
"opportunities": [
{{
"name": "...",
"confidence": "high|medium|low"
}}
]
}}

Do not return markdown.
Do not return explanations outside JSON.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        resp_text = response.text.strip()
        if resp_text.startswith("```json"):
            resp_text = resp_text[7:]
        if resp_text.endswith("```"):
            resp_text = resp_text[:-3]
            
        return json.loads(resp_text)
    except Exception as e:
        logger.warning(f"Gemini API failed during opportunity extraction: {e}. Falling back.")
        return _fallback_opportunity(brand, topic_summary, aspect_summary)
