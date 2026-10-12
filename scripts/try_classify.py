import os

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from release_radar.classify import classify_release
from release_radar.github import fetch_releases

load_dotenv()                                    # reads .env into the environment
model = os.environ["OPENAI_MODEL"]
openai_client = OpenAI()                         # finds OPENAI_API_KEY by itself

with httpx.Client(timeout=10, follow_redirects=True) as http:
    releases = fetch_releases("pallets/flask", http)

latest = next(r for r in releases if r.tag == "3.0.0")
print(f"Classifying Flask {latest.tag}...\n")

result = classify_release(latest.notes, openai_client, model)
for change in result.changes:
    print(f"[{change.category.upper():11}] {change.summary}")
    print(f"              why: {change.reason}\n")