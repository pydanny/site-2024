import functools
import pathlib

import jinja2
import markdown as md
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
    extensions=['jinja2_time.TimeExtension', "jinja2.ext.debug"])
templates = Jinja2Templates(env=env)

markdown = functools.partial(md.markdown, extensions=['pymdownx.superfences'])


app = FastAPI(docs_url="/api/docs")

app.mount("/static", StaticFiles(directory="static"), name="static")

@functools.lru_cache
def get_articles(published: bool = True) -> list[dict]:
    articles: list[dict] = []
    for article in pathlib.Path(".").glob("posts/*.md"):
        raw: str = article.read_text().split('---')[1]
        data: dict = yaml.safe_load(raw)
        data['slug'] = article.stem
        articles.append(data)   

    articles = [x for x in filter(lambda x: x['published'] is True, articles)]

    articles.sort(key=lambda x: x['date'], reverse=True)
    return [x for x in filter(lambda x: x['published'] is published, articles)]


@app.get("/api")
async def root():
    return {"message": "Hello World"}


@app.get("/")
async def index(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )




@app.get("/posts/{slug}")
async def post(slug: str, request: Request, response_class=HTMLResponse):
    article = [x for x in filter(lambda x: x['slug'] == slug, get_articles())][0]
    content = pathlib.Path(f"posts/{slug}.md").read_text().split('---')[2]
    article['content'] = markdown(content)

    return templates.TemplateResponse(
        request=request, name="post.html", context={"article": article}
    )    

@app.get("/posts")
async def posts(request: Request, response_class=HTMLResponse):
    articles: list[dict] = get_articles()

    articles.sort(key=lambda x: x['date'], reverse=True)

    return templates.TemplateResponse(
        request=request, name="posts.html", context={"articles": articles}
    )


@app.get("/tags")
async def tags(request: Request, response_class=HTMLResponse):
    articles: list[dict] = get_articles()

    tags: dict = {}
    for article in articles:
        for tag in article.get('tags', []):
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1

    return templates.TemplateResponse(
        request=request, name="tags.html", context={"tags": tags}
    )


@app.get("/tags/{tag}")
async def tag(tag: str, request: Request, response_class=HTMLResponse):
    articles: list[dict] = get_articles()
    articles = [x for x in filter(lambda x: tag in x.get('tags', []), articles)]


    return templates.TemplateResponse(
        request=request, name="tag.html", context={"tag": tag, "articles": articles}
    )