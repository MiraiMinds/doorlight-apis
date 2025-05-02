from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from logger import logger
from common_handler import make_api_call
from pprint import pprint

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/fetch-property")
async def get_property(item: dict = Body(...)):
    logger.info("==> API CALL: fetch-property")
    arguments = item["message"]["toolCallList"][0]["function"]["arguments"]
    logger.debug(f"==> arguments: {arguments}")

    params = {
        "page": 1,
        "limit": 3,
        "mls_status": "Active",
        "homeType[]": arguments["homeType"],
    }

    if arguments["bed"] != "Any":
        params["minBeds"] = arguments["bed"]
        params["maxBeds"] = arguments["bed"]

    if "minPrice" in arguments:
        params["minPrice"] = arguments["minPrice"]

    if "maxPrice" in arguments:
        params["maxPrice"] = arguments["maxPrice"]

    print("=====params=====", params)

    response = await make_api_call(
        url="https://preprodapi.doorlight.com/v1/mls/property/list",
        method="get",
        params=params,
    )

    data = response["data"]["results"]

    results = ""

    if len(data):
        print("===iff=======iff")

    for i, p in enumerate(data, start=1):
        results += f"""
Property {i}
- Address: {p["property"]["address"]}
- Price: {p["price"]} dollar
- Price per Sqft: {p["price_per_sqft"]}
- Bedrooms: {p["property"]["bed"]}
- Bathrooms: {p["property"]["baths_sum"]}
- Lot Size: {p["property"]["lot_size"]}
- Living Area: {p["property"]["sqft"]} sqft
- Year Built: {p["property"]["year_built"]}
"""

    print("=====results=====", results)

    toolCallId = item["message"]["toolCallList"][0]["id"]

    return {
        "results": [
            {
                "toolCallId": toolCallId,
                "result": f"### DATABASE: suitable property: \n{results}",
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=3001)
