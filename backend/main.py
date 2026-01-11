import asyncio
import subprocess
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_terminal(ws: WebSocket):
    await ws.accept()

    # Start a bash subprocess
    process = await asyncio.create_subprocess_exec(
        "/bin/bash",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    async def read_output():
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await ws.send_text(line.decode())

    asyncio.create_task(read_output())

    try:
        while True:
            data = await ws.receive_text()
            # Write to the shell
            process.stdin.write(data.encode() + b"\n")
            await process.stdin.drain()
    except Exception:
        process.terminate()
