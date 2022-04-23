from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from story_curve import make_viz, story_curve

app = FastAPI()

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "https://lrthomps.github.io",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the expected JSON format as a class from Pydantic:
class QueryString(BaseModel):
    """
    This class only contains one element, a string called "query".
    This setup will set Pydantic to expect a dictionary of format:
    {"query": "Some sort of string"}
    """
    story: str


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.options("/analysis/")


@app.post("/analysis/")
def form_post(query: QueryString):
    print(query.story)
    if query.story is None:
        return {"error": "no story"}
    mas, story_arc, n = story_curve(query.story)
    vizspec = make_viz(story_arc, n)
    return {
        "mas": str(mas),
        "storyViz": vizspec
    }
