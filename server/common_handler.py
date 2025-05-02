from fastapi import HTTPException
import httpx
from typing import Optional, Dict, Any


async def make_api_call(
    url: str,
    method: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """
    Common function to make API calls with error handling
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            request_kwargs = {
                "headers": headers or {},
                "params": params or {},
            }

            if data is not None:
                request_kwargs["data"] = data

            # Make the API call based on method
            response = await getattr(client, method)(url, **request_kwargs)

            # Check Content-Type header to determine response handling
            content_type = response.headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                try:
                    return response.json()
                except ValueError as json_error:
                    return {
                        "status_code": response.status_code,
                        "raw_content": response.text,
                        "error": f"Invalid JSON response: {str(json_error)}",
                        "headers": dict(response.headers),
                    }
            else:
                # Handle non-JSON responses
                return {
                    "status_code": response.status_code,
                    "content": response.text,
                    "content_type": content_type,
                    "headers": dict(response.headers),
                }

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API request failed: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"Network error occurred: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
