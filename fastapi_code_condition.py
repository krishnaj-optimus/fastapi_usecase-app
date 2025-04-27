from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class Document(BaseModel):
    metadata_spo_item_name: str

@app.post("/assign-role")
async def assign_role(document: Document):
    filename = document.metadata_spo_item_name
    role = "user" if filename == "user.pdf" else "group"
    return {"role": role}
