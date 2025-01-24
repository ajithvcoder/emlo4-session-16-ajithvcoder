import os
import json
import logging
import socket
import traceback
import requests
import httpx
import io
from PIL import Image
import numpy as np
from fastapi import FastAPI, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import Annotated

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - WebServer - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add constants
HOSTNAME = socket.gethostname()

# MODEL_SERVER_URL = os.environ.get("MODEL_SERVER_URL", "http://localhost:80")

MODEL_SERVER_URL = os.environ.get("MODEL_SERVER_URL", "http://0.0.0.0:8080")
# MODEL_SERVER_URL = "http://0.0.0.0:8080"
# MODEL_SERVER_URL = "http://model-server-service"

@app.on_event("startup")
async def initialize():
    logger.info(f"Initializing web server on host {HOSTNAME}")
    logger.info("Web server initialization complete")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup connection pool on shutdown"""
    logger.info("Shutting down web server")
    logger.info("Cleanup complete")


@app.post("/generate_image")
async def generate_image(text: str):
    logger.info("Received generation request")


    # logger.info("MODEL_SERVER_URL-", str(MODEL_SERVER_URL))
    infer_cache = None

    print("MODEL_SERVER_URL-", MODEL_SERVER_URL)
    # print("url-", url)
    url = f"{MODEL_SERVER_URL}/v1/models/sd_small:predict"
    # response = requests.post(, data=text)
    # Headers
    print("url-", url)
    headers = {
        "Host": "torchserve-sd3-default.example.com",
        "Content-Type": "application/json",
    }

    # Format payload according to handler's expectations
    payload = {"instances": [{"data": text}]}

    async with httpx.AsyncClient(timeout=httpx.Timeout(80.0)) as client:
        try:
            print("sending post request")
            response = requests.post(
                url,
                json=payload,  # Use json parameter to properly serialize
                headers=headers,
            )
            print("recieved post request response")
            if response.status_code != 200:
                raise Exception(f"Torchserve error: {response.text}")
            # print(response.text)
            # Construct image from response
            # image = Image.fromarray(np.array(json.loads(response.text), dtype="uint8"))
            image = Image.fromarray(np.array(response.json()["predictions"][0], dtype="uint8"))
            image.save("output_image.png")

            # Save the image to a BytesIO stream
            img_io = io.BytesIO()
            image.save(img_io, 'PNG')
            img_io.seek(0)

            # Get the bytes from the BytesIO stream
            image_bytes = img_io.getvalue()

            # Return the image bytes as a response with the appropriate media type
            return Response(content=image_bytes, media_type="image/png")
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Model server request failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Error from Model Endpoint")

    return "Error"

@app.get("/health")
async def health_check():
    """Health check endpoint for kubernetes readiness/liveness probes"""

    try:
        # Test Model Server connection
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(f"{MODEL_SERVER_URL}/health")
            response.raise_for_status()
            model_health = response.json()
            model_connected = True
    except Exception as e:
        logger.error(f"Model server health check failed: {str(e)}")
        model_connected = False
        model_health = None

    health_status = {
        "status": "healthy" if (model_connected) else "degraded",
        "hostname": HOSTNAME,
        "model_server": {
            "url": MODEL_SERVER_URL,
            "connected": model_connected,
            "health": model_health,
        },
    }

    logger.info(f"Health check status: {health_status['status']}")
    return health_status

# uvicorn server:app --host 0.0.0.0 --port 9000 --reload

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9090)