import os
import requests
import re
from typing import Dict, Any

class LLMClient:
    @staticmethod
    def generate_completion(prompt: str) -> str:
        # Check for Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                print(f"Error calling Gemini API: {e}")
                
        # Check for OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")

        # Fallback to smart simulated response if no api key or call fails
        return LLMClient.mock_completion(prompt)

    @staticmethod
    def mock_completion(prompt: str) -> str:
        if "trigger_llm_error" in prompt:
            return ""
        # PII Masking simulation
        if "PII masking" in prompt or "PII" in prompt or "mask" in prompt.lower():
            text_to_mask = prompt
            match = re.search(r'(?:Raw Text:|Text to mask:)\s*(.*)', prompt, re.DOTALL | re.IGNORECASE)
            if match:
                text_to_mask = match.group(1).strip()
            
            masked = text_to_mask
            
            # Simulated names replacement
            names = ["John Doe", "Jane Smith", "Ram Prasad", "Sita Ram", "Robert", "Alice"]
            for i, name in enumerate(names, 1):
                masked = re.sub(r'\b' + re.escape(name) + r'\b', f"<PERSON_{i}>", masked, flags=re.IGNORECASE)
            
            # MR/MRS/MS + Name
            masked = re.sub(r'\b(Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+)\b', r'\1 <PERSON_1>', masked)
            
            # Phone numbers (10 digits)
            masked = re.sub(r'\b\d{10}\b', "<PHONE_1>", masked)
            # Bank names / accounts
            masked = re.sub(r'\b(SBI|HDFC|ICICI|Axis|Citi|Chase|Bank of India)\b', "<BANK_1>", masked, flags=re.IGNORECASE)
            # IDs
            masked = re.sub(r'\b\d{4}-\d{4}-\d{4}\b', "<ID_1>", masked)
            masked = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', "<ID_1>", masked)
            return masked

        # Initial Suggestion simulation
        if "Suggested next steps flow" in prompt or "similar past" in prompt.lower():
            query = "the query"
            query_match = re.search(r'Current RTI Query:\s*(.*)', prompt, re.IGNORECASE)
            if query_match:
                query = query_match.group(1).strip().split('\n')[0]
                
            return f"Action Plan for: {query}\n" \
                   f"1. Context Verification: Validate incoming details against department records.\n" \
                   f"2. Department Routing: Assign the relevant sections based on similar historical cases.\n" \
                   f"3. Draft Response: Formulate the official reply addressing the specific points raised."

        # Chat Context simulation
        if "chat" in prompt.lower() or "user_chat_query" in prompt.lower():
            latest_query = "your query"
            query_match = re.search(r'(?:User\'s Latest Query:|user_chat_query)\s*(.*)', prompt, re.IGNORECASE)
            if query_match:
                latest_query = query_match.group(1).strip().split('\n')[0]
                
            return f"Based on the conversation state and retrieved historical notes: regarding '{latest_query}', " \
                   f"the policy dictates that we must provide the requested records within 30 days. " \
                   f"Please verify if any exemptions apply under Section 8 before releasing the data."

        return "This is a simulated assistant response based on the prompt."
