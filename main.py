from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running", "target": "pinterest"}

@app.get("/get-shorts")
def get_shorts(query: str = "Rain video"):
    # 1. Pinterest ko asli dikhne ke liye Headers bhejna zaroori hai
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.pinterest.com/"
    }
    
    url = f"https://www.pinterest.com/resource/BaseSearchResource/get/?data=%7B%22options%22%3A%7B%22query%22%3A%22{query}%22%2C%22scope%22%3A%22pins%22%7D%7D"
    
    try:
        # Request bhejte waqt headers shamil karein
        response = requests.get(url, headers=headers)
        
        # Check karein agar response valid hai
        if response.status_code != 200:
            return {"error": f"Pinterest returned status {response.status_code}", "raw": response.text[:200]}

        data = response.json()
        results = data.get('resource_response', {}).get('data', {}).get('results', [])
        
        clean_data = []
        for pin in results:
            # Sirf wo pins uthao jin mein video ho
            if 'videos' in pin and pin['videos'] is not None:
                video_list = pin['videos'].get('video_list', {})
                # 720p link dhoondo, agar na mile toh HLS
                video_obj = video_list.get('V_720P') or video_list.get('V_HLSV3')
                
                if video_obj:
                    clean_data.append({
                        "id": pin.get('id'),
                        "video_url": video_obj.get('url'),
                        "thumbnail": pin.get('images', {}).get('orig', {}).get('url'),
                        "title": pin.get('title') or pin.get('grid_title') or "Pinterest Video"
                    })
        
        return {"videos": clean_data}

    except Exception as e:
        return {"error": "Parsing failed", "details": str(e)}
