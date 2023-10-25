import os
import segno
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
import aiofiles

app = FastAPI()


class Item(BaseModel):
    data: str


@app.post("/generate_qrcode/")
async def generate_qrcode(item: Item):
    try:
        qr = segno.make(item.data)
        filename = "qrcode.png"
        qr.save(filename, scale=10, border=0)

        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(filename, mode='rb') as f:
                binary_data = await f.read()

                data = {
                    'name': 'qrcode',
                    'image': binary_data
                }

                response = await session.post('https://api.imgbb.com/1/upload?key=c793634661b542c39568732fe21627ff',
                                              data=data)
                json_result = await response.json()

        os.remove(filename)
        return {"qrcode": json_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))