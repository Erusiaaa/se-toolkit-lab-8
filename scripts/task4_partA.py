"""Part A — One-shot investigation: ask the agent 'What went wrong?' and capture response."""

import asyncio
import json
import websockets


async def main():
    url = "ws://nanobot:8765/ws/chat?access_key=nano-web-pass-789"
    print(f"Connecting to {url}...")

    async with websockets.connect(url, close_timeout=5) as ws:
        # Trigger a failure first (make sure there's recent error)
        await ws.send(json.dumps({"content": "What went wrong?"}))
        print("Sent: What went wrong?")

        responses = []
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=120 if not responses else 30)
                data = json.loads(raw)
                responses.append(data)
                t = data.get("type", "unknown")
                content_preview = str(data.get("content", ""))[:80]
                print(f"  Got frame: type={t}, content_preview={content_preview}...")
            except (TimeoutError, asyncio.TimeoutError):
                if responses:
                    break
                raise TimeoutError("No response from agent")

        # Print full final response
        final = responses[-1]
        content = final.get("content", "")
        print("\n" + "=" * 60)
        print("AGENT RESPONSE (FINAL):")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # Write to file for later use
        with open("/tmp/task4a_response.txt", "w") as f:
            f.write(content)

        print(f"\nSaved to /tmp/task4a_response.txt ({len(content)} chars)")


if __name__ == "__main__":
    asyncio.run(main())
