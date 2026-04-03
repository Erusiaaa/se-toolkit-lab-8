"""Part C — Post-fix investigation: ask agent 'What went wrong?' after the fix."""

import asyncio
import json
import websockets


async def main():
    url = "ws://nanobot:8765/ws/chat?access_key=nano-web-pass-789"
    print(f"Connecting to {url}...")

    async with websockets.connect(url, close_timeout=5) as ws:
        await ws.send(json.dumps({"content": "What went wrong? Please check system health and investigate any errors."}))
        print("Sent: What went wrong?")

        responses = []
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=120 if not responses else 30)
                data = json.loads(raw)
                responses.append(data)
                t = data.get("type", "unknown")
                content_preview = str(data.get("content", ""))[:120]
                print(f"  [{len(responses)}] type={t}, preview={content_preview}...")
            except (TimeoutError, asyncio.TimeoutError):
                if responses:
                    break
                raise TimeoutError("No response from agent")

        final = responses[-1]
        content = final.get("content", "")
        print("\n" + "=" * 80)
        print("POST-FIX INVESTIGATION RESPONSE:")
        print("=" * 80)
        print(content)
        print("=" * 80)

        with open("/tmp/task4c_investigation.txt", "w") as f:
            f.write(content)

        print(f"\nSaved: {len(content)} chars")


if __name__ == "__main__":
    asyncio.run(main())
