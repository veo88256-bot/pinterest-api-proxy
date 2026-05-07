from fastapi import FastAPI
import requests
import json

app = FastAPI()

# Headers jo aapne cURL se nikale (Mimicking your browser)
PINTEREST_HEADERS = {
    'accept': 'application/json, text/javascript, */*, q=0.01',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    'referer': 'https://www.pinterest.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'x-pinterest-appstate': 'active',
    'x-requested-with': 'XMLHttpRequest',
    # Bohat zaruri: Aapki session cookie
    'Cookie': 'csrftoken=2f0e1f4076694325503c3f3ff3545d7d; _auth=0; _pinterest_sess=TWc9PSZydHRMZ2lLRmdCVUdqV3ZQUnRDVWlqclZnRlhEdVZQQzdhWC9zSC9zNm55dlB2eSs4ZW52bXBFU3p1c3FEUmFwZDVVMk9LdnlZNDJkZExQcTA5WnhUQ2l3amRBdlVZQldXb1lONVM0NEI1ST0mQStkNU43QkpRdVpLS1oyM3JyTzUyWE1NdTZZPQ==;'
}

@app.get("/")
def home():
    return {"status": "running", "target": "pinterest"}

@app.get("/get-shorts")
def get_shorts(query: str = "Rain video"):
    # Pinterest ki API ko parameters ke sath tayyar karna
    endpoint = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    
    # Data object ko dynamic banana taake "query" change ho sake
    options = {
        "options": {
            "query": query,
            "scope": "pins",
            "rs": "trending",
            "redux_normalize_feed": True
        },
        "context": {}
    }
    
    params = {
        "source_url": f"/search/pins/?q={query}",
        "data": json.dumps(options),
        "_": "1778141466450"
    }

    try:
        # Request with full headers and cookies
        response = requests.get(endpoint, params=params, headers=PINTEREST_HEADERS)
        
        if response.status_code != 200:
            return {"error": f"Pinterest block level: {response.status_code}", "msg": response.text[:100]}

        data = response.json()
        results = data.get('resource_response', {}).get('data', {}).get('results', [])
        
        clean_data = []
        for pin in results:
            # Check if video exists
            if 'videos' in pin and pin['videos'] is not None:
                video_list = pin['videos'].get('video_list', {})
                # 720p priority, otherwise HLS
                video_obj = video_list.get('V_720P') or video_list.get('V_HLSV3')
                
                if video_obj:
                    clean_data.append({
                        "id": pin.get('id'),
                        "video_url": video_obj.get('url'),
                        "thumbnail": pin.get('images', {}).get('orig', {}).get('url'),
                        "title": pin.get('title') or pin.get('grid_title') or "Pinterest Shorts"
                    })
        
        return {"videos": clean_data}

    except Exception as e:
        return {"error": "Critical Parsing Error", "details": str(e)}
