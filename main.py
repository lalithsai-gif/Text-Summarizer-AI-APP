import re
import os
from fastapi import FastAPI,Request
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration,T5Tokenizer
import torch
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app=FastAPI(title="Text Summarizer APP",description="Text Summarization using T5",version="1.0")

HF_MODEL_NAME = "GRAFTERlalith/Text-summarizer-t5"
LOCAL_MODEL_PATH="./saved_summary_model"

if os.path.exists(LOCAL_MODEL_PATH):
    model = T5ForConditionalGeneration.from_pretrained(LOCAL_MODEL_PATH)
    tokenizer = T5Tokenizer.from_pretrained(LOCAL_MODEL_PATH)
else:
    model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_NAME)
    tokenizer = T5Tokenizer.from_pretrained(HF_MODEL_NAME)

if torch.cuda.is_available():
    device="cuda"
elif torch.backends.mps.is_available():
    device="mps"
else:
    device="cpu"

model.to(device)

templates=Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")


class DialogueInput(BaseModel):
    dialogue: str

def clean_data(text):
    text=re.sub(r"\r\n"," ",text)
    text=re.sub(r"<.*?>"," ",text)
    text=re.sub(r"\s+"," ",text)
    text=text.strip().lower()
    return text

def summarize_dialogue(dialogue : str) -> str:
    dialogue=clean_data(dialogue)

    inputs=tokenizer(
        dialogue,
        padding="max_length",
        max_length=512,
        truncation=True,
        return_tensors="pt"
    ).to(device)

    model.to(device)
    targets=model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=150,
        num_beams=4,
        early_stopping=True
    )

    summary=tokenizer.decode(targets[0],skip_special_tokens=True)
    return summary

@app.post("/summarize/")
async def summarize(dialogue_input: DialogueInput):
    summary=summarize_dialogue(dialogue_input.dialogue)
    return {"summary":summary}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )