import requests
import json
import config

def make_api_request(feature, query):
    """
    Make API request for different features
    """
    # Get base URL for the feature
    base_url = config.API_ENDPOINTS.get(feature, '')
    
    if not base_url:
        return {"error": "API endpoint not configured for this feature"}
    
    # Construct full URL
    full_url = f"{base_url}{query}"
    
    try:
        # Make request with proper headers
        headers = {
            'User-Agent': 'BRONX-OSINT-BOT/1.0',
            'Accept': 'application/json'
        }
        
        print(f"🔍 Making request to: {full_url}")
        
        response = requests.get(full_url, headers=headers, timeout=15)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Data received: {json.dumps(data, indent=2)[:200]}...")
                return data
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response from API"}
        else:
            return {"error": f"API returned status code {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"error": "⏰ Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "🔌 Connection failed. Check API endpoint."}
    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"💥 Unexpected error: {str(e)}"}

def format_response(data, feature_name):
    """
    Format API response for Telegram display
    """
    if not data:
        return """
❌ *No Data Found*

━━━━━━━━━━━━━━━━━━━━━━
No information available for this query.
        """
    
    if 'error' in data:
        return f"""
❌ *Error Occurred*

━━━━━━━━━━━━━━━━━━━━━━

{data['error']}

━━━━━━━━━━━━━━━━━━━━━━
        """
    
    # Format the JSON data nicely
    try:
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        
        # If JSON is too long, truncate it
        if len(formatted_json) > 3500:
            formatted_json = formatted_json[:3500] + "\n\n... (truncated)"
        
        return f"""
✅ *{feature_name} Result*

━━━━━━━━━━━━━━━━━━━━━━

```json
{formatted_json}
