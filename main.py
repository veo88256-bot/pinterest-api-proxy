from fastapi import FastAPI
import requests
import json
import time

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running", "version": "v4_stealth_mode"}

@app.get("/get-shorts")
def get_shorts(query: str = "Rain video"):
    endpoint = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    
    # Mazeed sakht headers jo bilkul Chrome jaisay hain
    STEALTH_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*, q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Pinterest-AppState': 'active',
        'Sec-CH-UA': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Referer': 'https://www.pinterest.com/',
        'Cookie': 'csrftoken=1fcb40469199714f57bb9cbfb543da02; _auth=0; _pinterest_sess=TWc9PSZUMC9KdndRNTEwL1lnR1FnMEpma2hDNFNKa1NtZk5iUE9HenRaeHk1aWx0U3UyTG5mR1hKRTZrZWEzL3ZBeGljakcvbGpYdGdiV0c4MjlrMG5RUFNweVJSVG4rdkc2Nmh5aWJYb2I2TXh5UT0mNTBhSG14S0Q5UzR3RFlwakg4eXpiZVdqK0JFPQ==;'
    }

    data_payload = {
        "options": {
            "query": query,
            "scope": "pins",
            "rs": "trending"
        },
        "context": {}
    }

    params = {
        "source_url": f"/search/pins/?q={query}",
        "data": json.dumps(data_payload),
        "_": str(int(time.time() * 1000)) # Dynamic timestamp
    }

    try:
        # Pinterest ko request bhejte waqt thoda sa natural delay
        # (Lekin Render par ye IP block ka masla zyada hai)
        response = requests.get(endpoint, params=params, headers=STEALTH_HEADERS, timeout=15)
        
        if response.status_code == 403:
            return {
                "error": "IP_BLOCKED",
                "message": "Pinterest has blocked Render's IP range. Headers are correct, but the source is blacklisted.",
                "solution": "Use ScraperAPI or a residential proxy."
            }

        # Baqi parsing logic wahi purani...
        data = response.json()
        results = data.get('resource_response', {}).get('data', {}).get('results', [])
        clean_data = []
        for pin in results:
            if 'videos' in pin and pin['videos']:
                v_list = pin['videos'].get('video_list', {})
                v_obj = v_list.get('V_720P') or v_list.get('V_HLSV3')
                if v_obj:
                    clean_data.append({
                        "id": pin['id'],
                        "video_url": v_obj['url'],
                        "thumbnail": pin['images']['orig']['url'],
                        "title": pin.get('title', 'Pinterest Video')
                    })
        return {"videos": clean_data}

    except Exception as e:
        return {"error": str(e)}
