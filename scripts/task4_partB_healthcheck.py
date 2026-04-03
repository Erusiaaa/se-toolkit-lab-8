"""Part B — Capture the proactive health check report from cron."""

import asyncio
import json
import websockets


async def main():
    url = "ws://nanobot:8765/ws/chat?access_key=nano-web-pass-789"
    print(f"Connecting to {url}...")

    async with websockets.connect(url, close_timeout=5) as ws:
        # Ask the agent to run the health check now
        await ws.send(json.dumps({"content": (
            "Run the health check now. Check for backend errors in the last 2 minutes "
            "using logs_error_count with start='2m'. If errors are found, search for "
            "details using logs_search. Post a short summary here."
        )}))
        print("Sent: Run the health check now...")

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
                raise

        final = responses[-1]
        content = final.get("content", "")
        print("\n" + "=" * 80)
        print("PROACTIVE HEALTH CHECK REPORT:")
        print("=" * 80)
        print(content)
        print("=" * 80)

        with open("/tmp/task4b_proactive_report.txt", "w") as f:
            f.write(content)

        print(f"\nSaved: {len(content)} chars")


if __name__ == "__main__":
    asyncio.run(main())
