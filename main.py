from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import pyqrcode
from io import BytesIO
import aiohttp
import aiofiles

app = FastAPI()

class Item(BaseModel):
    url: str

    @validator("url")
    def validate_url(cls, v):
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("Invalid URL provided")
        return v

@app.post("/generate_qrcode/")
async def generate_qrcode(item: Item):
    try:
        url = pyqrcode.create(item.url)
        filename = "qrcode.png"
        url.png(filename, scale=8)

        #Step where we upload the QR code to imgBB
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(filename, mode='rb') as f:
                binary_data = await f.read()

                data = {
                    'name': 'qrcode',
                    'image': binary_data
                }
                response = await session.post('https://api.imgbb.com/1/upload?key=c793634661b542c39568732fe21627ff', data=data)
                json_result = await response.json()

        return {"qrcode": json_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))