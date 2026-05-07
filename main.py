from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running", "target": "pinterest"}

@app.get("/get-shorts")
def get_shorts(query: str = "Rain video"):
    url = f"https://www.pinterest.com/resource/BaseSearchResource/get/?data=%7B%22options%22%3A%7B%22query%22%3A%22{query}%22%2C%22scope%22%3A%22pins%22%7D%7D"
    
    try:
        response = requests.get(url).json()
        results = response.get('resource_response', {}).get('data', {}).get('results', [])
        
        clean_data = []
        for pin in results:
            if 'videos' in pin and pin['videos']:
                clean_data.append({
                    "id": pin['id'],
                    "video_url": pin['videos']['video_list']['V_720P']['url'],
                    "thumbnail": pin['images']['orig']['url'],
                    "title": pin.get('title', 'Pinterest Video')
                })
        return {"videos": clean_data}
    except Exception as e:
        return {"error": str(e)}