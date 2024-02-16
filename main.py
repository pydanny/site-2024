import collections
import pathlib

import jinja2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import helpers


env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
    extensions=['jinja2_time.TimeExtension', "jinja2.ext.debug"])
templates = Jinja2Templates(env=env)


app = FastAPI(docs_url="/api/docs")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api")
async def root():
    return {"message": "Hello World"}


@app.get("/")
async def index(request: Request, response_class=HTMLResponse):
    posts = helpers.list_posts()
    recent_3 = posts[:3]

    favorite_post_ids: list[str] = [
        "code-code-code",
        "thirty-minute-rule",
        "whats-the-best-thing-about-working-for-octopus-energy-part-1",
        "i-married-audrey-roy",        
    ]
    favorite_posts: list  = filter(lambda x: x['slug'] in favorite_post_ids, posts)

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"recent_3": recent_3, "favorite_posts": favorite_posts}
    )


@app.get("/posts/{slug}")
async def post(slug: str, request: Request, response_class=HTMLResponse):
    post = [x for x in filter(lambda x: x['slug'] == slug, helpers.list_posts())][0]
    content = pathlib.Path(f"posts/{slug}.md").read_text().split('---')[2]
    post['content'] = helpers.markdown(content)

    return templates.TemplateResponse(
        request=request, name="post.html", context={"post": post}
    )    

@app.get("/posts")
async def posts(request: Request, response_class=HTMLResponse):
    posts: list[dict] = helpers.list_posts()

    posts.sort(key=lambda x: x['date'], reverse=True)

    return templates.TemplateResponse(
        request=request, name="posts.html", context={"posts": posts}
    )


@app.get("/tags")
async def tags(request: Request, response_class=HTMLResponse):
    posts: list[dict] = helpers.list_posts()

    unsorted_tags: dict = {}
    for post in posts:
        for tag in post.get('tags', []):
            if tag in unsorted_tags:
                unsorted_tags[tag] += 1
            else:
                unsorted_tags[tag] = 1

    # Sort by value (number of articles per tag)
    tags: dict = collections.OrderedDict(
        sorted(unsorted_tags.items(),
               key=lambda x: x[1], reverse=True))

    return templates.TemplateResponse(
        request=request, name="tags.html", context={"tags": tags}
    )


@app.get("/tags/{tag}")
async def tag(tag: str, request: Request, response_class=HTMLResponse):
    posts: list[dict] = helpers.list_posts()
    posts = [x for x in filter(lambda x: tag in x.get('tags', []), posts)]


    return templates.TemplateResponse(
        request=request, name="tag.html", context={"tag": tag, "posts": posts}
    )


@app.get("/{slug}")
async def page(slug: str, request: Request, response_class=HTMLResponse):
    path = pathlib.Path(f"pages/{slug}.md")
    try:
        page: dict[str, str|dict] = helpers.load_content_from_markdown_file(path)
    except FileNotFoundError:
        return templates.TemplateResponse(
            request=request, name="404.html", status_code=404
        )
    page['slug'] = slug

    return templates.TemplateResponse(
        request=request, name="page.html", context={"page": page}
    )