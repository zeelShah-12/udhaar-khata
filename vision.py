import base64
import io
import json
import os

from groq import Groq
from PIL import Image

# Groq's current vision-capable model (multimodal, text + image input)
MODEL_NAME = "qwen/qwen3.8-27b"

PROMPT = """You are digitizing a page from a small Indian shop's handwritten "udhaar" (credit)
notebook. Shop owners write down customer names with amounts they owe (credit given) or
amounts they've paid back, often in a mix of Hindi/English/Hinglish, sometimes messy
handwriting, tally marks, or shorthand like "+500" (owes more) or "-200" (paid back).

Look at this photo and extract every entry you can read. For each entry report:
- customer_name: the name as written (clean up obvious spelling but keep it recognizable)
- amount: a positive number
- type: "given" if this is credit given to the customer (they now owe more — usually a plain
  number, a "+", or just written without a minus), or "received" if this is a payment the
  customer made back (often has "-", "paid", "wapas", "diya", or is in a separate paid column)
- date: in YYYY-MM-DD format if a date is visible, else null (do not guess a year you can't see)
- notes: what the credit was for if mentioned (e.g. "atta, chai"), else empty string

If you cannot confidently read an entry, skip it rather than guessing wildly.

Respond with ONLY valid JSON, no markdown fences:
{
  "entries": [
    {"customer_name": str, "amount": number, "type": "given" | "received", "date": str | null, "notes": str}
  ]
}
"""


def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Groq(api_key=api_key)


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def extract_entries(image: Image.Image) -> dict:
    client = _get_client()
    data_url = _image_to_data_url(image)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        response_format={"type": "json_object"},
        reasoning_effort="none",
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)
