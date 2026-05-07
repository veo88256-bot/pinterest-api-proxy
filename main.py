from fastapi import FastAPI
import requests
import json

app = FastAPI()

# Fresh Headers aur Cookies jo aapne abhi bheji hain
# Inko "as is" use karna zaroori hai
PINTEREST_HEADERS = {
    'accept': 'application/json, text/javascript, */*, q=0.01',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    'referer': 'https://www.pinterest.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    'x-app-version': '587f0d4',
    'x-pinterest-appstate': 'active',
    'x-requested-with': 'XMLHttpRequest',
    'priority': 'u=1, i',
    # Poori fresh cookie string yahan hai
    'Cookie': 'csrftoken=1fcb40469199714f57bb9cbfb543da02; _b="AZOfDedlGDBONLB1kFEtUMbIBwFh1tB3WYoUlRFxgouNXEsLudGqnXBqMdKnXC3RMQ4="; _auth=0; _pinterest_sess=TWc9PSZUMC9KdndRNTEwL1lnR1FnMEpma2hDNFNKa1NtZk5iUE9HenRaeHk1aWx0U3UyTG5mR1hKRTZrZWEzL3ZBeGljakcvbGpYdGdiV0c4MjlrMG5RUFNweVJSVG4rdkc2Nmh5aWJYb2I2TXh5UT0mNTBhSG14S0Q5UzR3RFlwakg4eXpiZVdqK0JFPQ==; l_o=MVpsOG5hYkxHSkJSSGYrbXNIemxwdkVJRU1iS1JXN1IrUzNoUEs5d08wWk1weGN0cEozalY3YkprUGNpYVlVaWdIRmx5ZG9wQzArbWZRVkRPNE9wc28vak1YaktrR3F4QjNIYkttN1JLcjQ9JlJYQWhURTNmZjFqc21uWityUGVNTnNabG9tRT0=; __Secure-s_a=TFdaNXVOdXJzZkNrK2lvdGwvdDVRRElsdmk4MlRLMHFCSUpML2RnZWtRbz0mMngyaVVtZDllelBZV1dYTUx3UGFDOUE0cWhnPQ==; fba=True; _routing_id="afbba23d-e66f-4517-9461-959137bc8638"; sessionFunnelEventLogged=1; g_state={"i_l":0,"i_ll":1778141466761,"i_e":{"enable_itp_optimization":0},"i_et":1776146536348,"i_b":"jGVM5KyppBmUVvjmvJFecAfdk2MY1p+Ds7UmItx+rKk"}'
}

@app.get("/")
def home():
    return {"status": "running", "version": "v3_fresh_cookies"}

@app.get("/get-shorts")
def get_shorts(query: str = "Rain video"):
    endpoint = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    
    # Data object ko dynamic banane ke liye query inject kar rahe hain
    data_payload = {
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
        "data": json.dumps(data_payload),
        "_": "1778153821738" # Fresh timestamp
    }

    try:
        # Request with updated headers and fresh cookies
        response = requests.get(endpoint, params=params, headers=PINTEREST_HEADERS, timeout=10)
        
        if response.status_code != 200:
            return {
                "error": f"Pinterest status {response.status_code}",
                "msg": "Still blocked. Pinterest might be tracking Render's IP.",
                "hint": "Try changing Render region or using a rotating proxy."
            }

        data = response.json()
        results = data.get('resource_response', {}).get('data', {}).get('results', [])
        
        clean_data = []
        for pin in results:
            if 'videos' in pin and pin['videos'] is not None:
                video_list = pin['videos'].get('video_list', {})
                # Priority 720p -> HLS -> Default
                video_obj = video_list.get('V_720P') or video_list.get('V_HLSV3')
                
                if video_obj:
                    clean_data.append({
                        "id": pin.get('id'),
                        "video_url": video_obj.get('url'),
                        "thumbnail": pin.get('images', {}).get('orig', {}).get('url'),
                        "title": pin.get('title') or pin.get('grid_title') or "Pinterest Shorts"
                    })
        
        return {"count": len(clean_data), "videos": clean_data}

    except Exception as e:
        return {"error": "Server Error", "details": str(e)}
