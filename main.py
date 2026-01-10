# Step1: Setup FastAPI backend
from fastapi import FastAPI, Form
from pydantic import BaseModel
import uvicorn
from fastapi import Request
from fastapi.responses import PlainTextResponse
from xml.etree.ElementTree import Element, tostring
from xml.sax.saxutils import escape
from ai_agent import graph, SYSTEM_PROMPT, parse_response

app = FastAPI()

# Step2: Receive and validate request from Frontend
class Query(BaseModel):
    message: str
from xml.sax.saxutils import escape

MAX_LEN = 1500  # keep under Twilio's 1600 limit

def chunk_text(text: str, max_len: int = MAX_LEN):
    """Split long messages into Twilio-safe chunks."""
    text = text.strip()
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]



@app.post("/ask")
async def ask(query: Query):
    inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", query.message)]}
    #inputs = {"messages": [("user", query.message)]}
    stream = graph.stream(inputs, stream_mode="updates")
    tool_called_name, final_response = parse_response(stream)

    # Step3: Send response to the frontend
    return {"response": final_response,
            "tool_called": tool_called_name}

from fastapi.responses import PlainTextResponse
from xml.etree.ElementTree import Element, tostring

from fastapi.responses import PlainTextResponse
from xml.etree.ElementTree import Element, tostring

def _twiml_message_multichunk(body: str) -> PlainTextResponse:
    """
    Create TwiML with multiple <Message> tags if text is too long.
    """
    response_el = Element("Response")

    chunks = chunk_text(body)

    for part in chunks:
        msg_el = Element("Message")
        msg_el.text = escape(part)   # escape XML unsafe chars
        response_el.append(msg_el)

    xml_output = tostring(response_el, encoding="utf-8", method="xml")
    return PlainTextResponse(content=xml_output.decode(), media_type="application/xml")

@app.post("/whatsapp_ask")
async def whatsapp_ask(request: Request):
    form = await request.form()
    user_text = form.get("Body", "").strip()

    # Get AI response
    inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_text)]}
    stream = graph.stream(inputs, stream_mode="updates")
    tool_called_name, final_response = parse_response(stream)

    if not final_response:
        final_response = "I'm here to support you, but I couldn't generate a response just now."

    # Send multi-chunk TwiML reply
    return _twiml_message_multichunk(final_response)




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)







