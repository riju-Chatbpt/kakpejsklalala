mkdir -p utils handlers

# utils/__init__.py
cat > utils/__init__.py << 'EOF'
EOF

# utils/api_handler.py
cat > utils/api_handler.py << 'EOF'
import requests
import json
import config

def make_api_request(feature, query):
    base_url = config.API_ENDPOINTS.get(feature, '')
    if not base_url:
        return {"error": "API endpoint not configured"}
    full_url = f"{base_url}{query}"
    try:
        headers = {'User-Agent': 'BRONX-OSINT-BOT/1.0', 'Accept': 'application/json'}
        response = requests.get(full_url, headers=headers, timeout=15)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response"}
        else:
            return {"error": f"API returned status code {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def format_response(data, feature_name):
    if not data:
        return "❌ *No Data Found*\n\nNo information available."
    if 'error' in data:
        return f"❌ *Error*\n\n{data['error']}"
    try:
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        if len(formatted_json) > 3500:
            formatted_json = formatted_json[:3500] + "\n\n... (truncated)"
        return f"✅ *{feature_name} Result*\n\n```json\n{formatted_json}\n```\n\n🤖 *BRONX OSINT BOT*\n📞 @BRONX_ULTRA"
    except:
        return f"✅ *{feature_name} Result*\n\n{str(data)[:3000]}\n\n🤖 *BRONX OSINT BOT*"
EOF
