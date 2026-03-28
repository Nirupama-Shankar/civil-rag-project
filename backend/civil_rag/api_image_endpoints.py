# Add this to api.py

from .image_ingest import search_images

@app.post("/search_images")
async def search_images_endpoint(request: Request):
    """Search for images using text query"""
    data = await request.json()
    query = data.get('query', '')
    
    try:
        results = search_images(query, k=5)
        
        images = []
        for img in results:
            images.append({
                "filename": img['filename'],
                "path": img['path'],
                "score": img['score'],
                "url": f"/image/{img['filename']}"
            })
        
        return {"images": images}
    except Exception as e:
        print(f"❌ Image search error: {e}")
        return {"images": []}

@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve image file"""
    from fastapi.responses import FileResponse
    
    # Search for image in images folder
    images_folder = "/Users/apple/Documents/Projects/civil_rag_project/backend/images"
    
    for root, dirs, files in os.walk(images_folder):
        if filename in files:
            return FileResponse(os.path.join(root, filename))
    
    return JSONResponse(status_code=404, content={"error": "Image not found"})
