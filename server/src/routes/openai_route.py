import json
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from src.utils.config import OPENAI_API_BASE_URL, OPENAI_MODEL, OPENAI_API_KEY
from src.handlers.common_handler import make_api_call


openai_router = APIRouter(prefix="/openai", tags=["openai"])


class SDP(BaseModel):
    offer_sdp: str


@openai_router.post("/sdp")
async def handle_ephemeral_key(request: SDP):
    try:
        # Fetch ephemeral key.
        response = await make_api_call(
            url=f"{OPENAI_API_BASE_URL}/realtime/sessions",
            method="post",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "model": OPENAI_MODEL,
                    "voice": "ash",
                }
            ),
        )
        ephemeral_key = response["client_secret"]["value"]

        # Fetch SDP(Session Description Protocol).
        response = await make_api_call(
            url=f"{OPENAI_API_BASE_URL}/realtime?model={OPENAI_MODEL}",
            method="post",
            headers={
                "Authorization": f"Bearer {ephemeral_key}",
                "Content-Type": "application/sdp",
            },
            data=request.offer_sdp,
        )
        answer = {"type": "answer", "sdp": response["content"]}

        return JSONResponse(
            content={"message": "SDP get successfully.", "content": answer},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
