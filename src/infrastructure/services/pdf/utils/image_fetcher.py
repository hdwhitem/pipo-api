import httpx
from io import BytesIO
from typing import Optional
from src.core.config import settings


DUMMY_IMAGE = f"{settings.CLOUDINARY_BASE_URL}/{settings.DUMMY_IMAGE_NAME}"

async def fetch_image_bytes(client: httpx.AsyncClient, url: str) -> Optional[BytesIO]:
    if not url:
        return None
    try:
        response = await client.get(url, timeout=5.0)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception:
        pass
    
    # Fallback si falla la imagen principal
    try:
        response = await client.get(DUMMY_IMAGE, timeout=5.0)
        return BytesIO(response.content)
    except Exception:
        return None