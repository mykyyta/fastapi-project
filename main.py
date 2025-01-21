import json
import random
import string
from typing import Annotated
import aiofiles
from fastapi import FastAPI, Form, Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return  templates.TemplateResponse(request, 'index.html')

@app.post("/")
async def post(request: Request, long_url: Annotated[str, Form()]):
    short_url = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(5)])
    async with aiofiles.open('urls.json', 'r') as f:
        urls_data = json.loads(await f.read())
    async with aiofiles.open('urls.json','w') as f:
        urls_data[short_url] = long_url
        await f.write(json.dumps(urls_data))
    return {'short_url':short_url}

@app.get("/{short_url}")
async def redirect_to_long_url(short_url: str):
    async with aiofiles.open("urls.json", "r") as f:
        urls_data = json.loads(await f.read())
    long_url = urls_data.get(short_url)
    if not long_url:
        return {"error": "Short URL not found"}
    return RedirectResponse(url=long_url)