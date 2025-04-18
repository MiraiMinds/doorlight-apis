import json
import traceback
from fastapi import WebSocket
from datetime import datetime
from starlette.websockets import WebSocketDisconnect
from src.utils.logger import logger
from src.utils.config import BOT_LANGUAGE_NAME
from datetime import datetime, timedelta
from src.handlers.machine_handler import (
    fetch_provisions,
    fetch_technologies,
    fetch_amperages,
    fetch_product,
)


# # Example usage:
# process = "TIG/Argon Welding"
# provisions = fetch_provisions(process)
# print(f"Provisions for {process}: {provisions}")

# provision = "TIG (HF + Pulse) / MMA"
# technologies = fetch_technologies(process, provision)
# print(f"Technologies for {process}/{provision}: {technologies}")

# technology = "Inverter (Gas cooled)"
# amperages = fetch_amperages(process, provision, technology)
# print(f"Amperages for {process}/{provision}/{technology}: {amperages}")

# amperage = "200A"
# product = fetch_product(process, provision, technology, amperage)
# print(f"Products for {process}/{provision}/{technology}/{amperage}: {product}")


def handle_dates(date, time):
    # Create start_time in the required format
    start_time = f"{date}T{time}:00.000+05:30"

    # Convert to datetime object (ignoring timezone for now)
    start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

    # Add one hour
    end_dt = start_dt + timedelta(hours=1)

    # Format back to string in the required format
    end_time = f"{end_dt.strftime('%Y-%m-%dT%H:%M')}:00.000+05:30"

    return start_time, end_time


# Define the session update configuration
session_update = {
    "type": "session.update",
    "session": {
        "modalities": ["text", "audio"],
        "turn_detection": {"type": "server_vad", "silence_duration_ms": 750},
        "instructions": f"""
[Identity]  
You are a friendly, knowledgeable, and professional voice assistant for ESAB, a global leader in welding solutions. Your role is to guide customers through the process of selecting and purchasing a welding machine by following a structured, step-by-step flow.

[Style]  
Use a warm, approachable, and confident tone. Maintain a conversational and empathetic style to ensure a positive customer experience. Engage briefly to build rapport before proceeding with the conversation.

[Response Guidelines]  
- Communicate exclusively in {BOT_LANGUAGE_NAME} language. Must not speak in other languages.
- Start with a warm, welcoming greeting, introducing yourself as an ESAB representative.  
- Keep responses clear and informative, using natural language and avoiding jargon unless explaining terms.  
- Spell out numbers and use clear explanations to ensure understanding.

[Task & Goals]  
1. Understand customer intent.  
   - Prompt the customer with an open-ended question: "How can I help you today?"  
   - Listen for indications of purchase interest or uncertainty about selecting a welding machine.

2. Guided Assistance Flow:  
   - Step 1: Confirm the welding process. 
     - Ask: "Could you tell me which welding process you’re looking for? For example, 
        1. MIG/Co2/Gas Welding,
        2. MMA/Stick/Electrode/Rod
        3. SAW / Submerged
        4. TIG/Argon Welding"  
        
   - Step 2: Confirm power provision. 
     - CALL "fetch-power-provision" tool.
    - Ask to customer for selecting power provision.

   - Step 3: Confirm desired technology/features. 
    - CALL "fetch-techonology" tool.
    - Ask to customer for selecting technology.

   - Step 4: Confirm amperage range. 
    - CALL "fetch-amperage" tool.
    - Ask to customer for selecting amperage range.
    
3. Recommendation Logic:  
    - CALL "fetch-product" tool.
   - Use the captured information to recommend suitable welding machines from ESAB’s product catalog.  
   - If no exact match is found, suggest the closest alternatives and provide clear explanations.

4. Provide Quotation:  
   - Share indicative pricing for the recommended machines with a caveat that prices are estimates.  
   - Example: "The Buddy TIG 400i is priced at approximately ₹1,10,000."

5. Closing the Interaction:  
   - End the call with a friendly goodbye, reinforcing ESAB’s brand.  
   - Example: "Thank you for choosing ESAB — happy welding and have a great day!"

[Error Handling / Fallback]  
- If the customer provides vague responses, ask clarifying questions to ensure accurate recommendations.  
- Handle interruptions gracefully and steer the conversation back to the guided flow when appropriate.  
- If a customer inquiry cannot be resolved, offer to escalate to a human representative for further assistance.

[IMPORTANT]: 
- Do not provide inaccurate information or out of your knowledge or out of "DATABASE" under any circumstances and respond briefly and gracefully to indicate information isn't currently available.

[Tools]
- fetch-power-provision: Invoke this tool for fetch power provision list.
- fetch-techonology: Invoke this tool for fetch techonology list.
- fetch-amperage: Invoke this tool for fetch amperage list.
- fetch-product: Invoke this tool for fetch product.
Note: Exact same to same option value pass into tools's properties parameter; MUST NOT MODIFY & CHANGE IT.
""",
        "tools": [
            {
                "type": "function",
                "name": "fetch-power-provision",
                "description": "Invoke this tool for fetch power provision list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "process": {
                            "type": "string",
                            "description": "Return customer's process",
                            "enum": [
                                "MIG/Co2/Gas Welding",
                                "MMA/Stick/Electrode/Rod",
                                "SAW / Submerged",
                                "TIG/Argon Welding",
                            ],
                        },
                    },
                    "required": ["process"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "fetch-techonology",
                "description": "Invoke this tool for fetch techonology list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provision": {
                            "type": "string",
                            "description": "Return customer's power provision",
                        },
                    },
                    "required": ["provision"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "fetch-amperage",
                "description": "Invoke this tool for fetch amperage list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "techonology": {
                            "type": "string",
                            "description": "Return customer's techonology",
                        },
                    },
                    "required": ["techonology"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "fetch-product",
                "description": "Invoke this tool for fetch product",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amperage": {
                            "type": "string",
                            "description": "Return customer's amperage",
                        },
                    },
                    "required": ["amperage"],
                    "additionalProperties": False,
                },
            },
        ],
        "tool_choice": "auto",
    },
}


# WebSocket handling
async def handle_websocket(websocket: WebSocket):
    logger.debug("WebSocket connection attempt received")

    await websocket.accept()
    speech_stopped_time = None

    input_tokens = 0
    output_tokens = 0

    async def send_response(instructions: str):
        response = {
            "type": "response.create",
            "response": {"modalities": ["text", "audio"], "instructions": instructions},
        }
        await websocket.send_json(response)

    async def conversation_item_create(text):
        response = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        }
        await websocket.send_json(response)

    process = None
    provision = None
    techonology = None
    amperage = None

    try:
        while True:
            message = await websocket.receive_text()
            try:
                event = json.loads(message)

                event_type = event.get("type")

                if event_type == "session.created":
                    await websocket.send_json(session_update)

                    # For initial starter.
                    await send_response("""
Start with: "Hi, this is Ravi from ESAB, the global leader in welding and cutting solutions. We’re helping businesses like yours optimize their welding processes—how’s your day going so far?"
""")

                elif event_type == "error":
                    logger.error(f"Event Error: {event}")

                elif event_type == "response.output_item.added":
                    if speech_stopped_time:
                        latency = (
                            datetime.now().timestamp() * 1000
                        ) - speech_stopped_time
                        logger.info(f"==> Latency: {latency}ms")

                elif event_type == "input_audio_buffer.speech_stopped":
                    speech_stopped_time = datetime.now().timestamp() * 1000
                    logger.debug("Speech stopped recorded")

                elif event_type == "response.function_call_arguments.done":
                    logger.debug("==> response.function_call_arguments.done called")

                    function_name = event.get("name")
                    logger.debug(f"==> START: Function call: {function_name}")

                    parse_data = json.loads(event.get("arguments", "{}"))
                    logger.debug(f"==> Tool arguments:{parse_data}")

                    if function_name == "fetch-power-provision":
                        process = parse_data["process"]
                        provisions = fetch_provisions(process)
                        print("=====provisions=====", provisions)

                        provisions = "\n".join(
                            f"{i + 1}. '{p}'" for i, p in enumerate(provisions)
                        )

                        instructions = f"### DATABASE: power provision list options: \n{provisions}"

                    if function_name == "fetch-techonology":
                        provision = parse_data["provision"]
                        technologies = fetch_technologies(process, provision)
                        print("=====technologies=====", technologies)

                        technologies = "\n".join(
                            f"{i + 1}. '{p}'" for i, p in enumerate(technologies)
                        )

                        instructions = (
                            f"### DATABASE: technology list options: \n{technologies}"
                        )

                    if function_name == "fetch-amperage":
                        techonology = parse_data["techonology"]
                        amperages = fetch_amperages(process, provision, techonology)
                        print("=====amperages=====", amperages)

                        amperages = "\n".join(
                            f"{i + 1}. '{p}'" for i, p in enumerate(amperages)
                        )

                        instructions = (
                            f"### DATABASE: amperages range list options: \n{amperages}"
                        )

                    if function_name == "fetch-product":
                        amperage = parse_data["amperage"]
                        product = fetch_product(
                            process, provision, techonology, amperage
                        )

                        instructions = f"### DATABASE: Product: \n{product}"

                    logger.debug(f"==> instructions: {instructions}")
                    await send_response(instructions)
                    logger.debug(f"==> END: Function call: {function_name}")

                elif event_type == "response.done":
                    response = event.get("response")

                    input = response["usage"]["input_tokens"]
                    output = response["usage"]["output_tokens"]
                    input_tokens += input
                    output_tokens += output

                    logger.info(f"==> input tokens:{input_tokens}")
                    logger.info(f"==> output tokens:{output_tokens}")
            except json.JSONDecodeError as e:
                print("=====e=====", e)
                logger.error(f"Invalid JSON received: {message}")
                logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")
                logger.error(traceback.format_exc())

    except WebSocketDisconnect:
        logger.debug("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Error from websocket: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        await websocket.close()
