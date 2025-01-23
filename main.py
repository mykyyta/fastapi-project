import random
import string
from typing import Annotated
from fastapi import FastAPI, Form, Request, HTTPException
from starlette import status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import motor.motor_asyncio

app = FastAPI()

MONGO_URL = "mongodb://root:example@localhost:27017"
db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
app_db = db_client["url_shortener"]
collection = app_db["urls"]

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    urls_data = await collection.find().to_list(None)
    return  templates.TemplateResponse(request, 'index.html', {'urls_data': urls_data})

@app.post("/")
async def post(long_url: Annotated[str, Form()]):
    short_url = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(5)])
    await collection.insert_one({"long_url": long_url, "short_url": short_url})
    return RedirectResponse(f'/{short_url}/stats', status_code=status.HTTP_303_SEE_OTHER)

@app.get("/{short_url}")
async def redirect_to_long_url(short_url: str):
    url_data = await collection.find_one({"short_url": short_url})
    if url_data is None:
        raise HTTPException(status_code=404, detail="Short url not found")
    long_url = url_data.get('long_url')
    await collection.update_one({"short_url": short_url}, {"$inc": {"clicks": 1}})
    return RedirectResponse(url=long_url)

@app.get("/{short_url}/stats")
async def stats(request: Request, short_url):
    url_data = await collection.find_one({"short_url": short_url})
    if url_data is None:
        raise HTTPException(status_code=404, detail="Short url not found")
    return templates.TemplateResponse(request, 'stats.html', context={'url_data': url_data})

@app.post("/{short_url}/stats")
async def post(short_url: str, long_url: Annotated[str, Form()]):
    await collection.update_one({"short_url": short_url}, {'$set': {"long_url": long_url}})
    return RedirectResponse(f'/{short_url}/stats', status_code=status.HTTP_303_SEE_OTHER)