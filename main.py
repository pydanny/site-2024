from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_blog import add_blog_to_fastapi


# import feeds


app = FastAPI(docs_url="/api/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def root():
    return {"message": "Hello World"}


# @app.get("/feeds/{tag}.xml")
# async def feed(tag: str, request: Request, response_class=Response):
#     xml: str = feeds.generate_feed(tag)

#     return Response(xml, media_type="application/xml")


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


app = add_blog_to_fastapi(app, prefix=None)