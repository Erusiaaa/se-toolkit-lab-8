"""Part B step 6 — Remove the test health check job."""

import asyncio
import json
import websockets


async def main():
    url = "ws://nanobot:8765/ws/chat?access_key=nano-web-pass-789"
    print(f"Connecting to {url}...")

    async with websockets.connect(url, close_timeout=5) as ws:
        # Remove the health check job
        await ws.send(json.dumps({"content": "Remove the health check cron job. It was a test job and is no longer needed."}))
        print("Sent: Remove the health check cron job...")

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
        print("JOB REMOVAL RESPONSE:")
        print("=" * 80)
        print(content)
        print("=" * 80)

        with open("/tmp/task4b_job_removal.txt", "w") as f:
            f.write(content)


if __name__ == "__main__":
    asyncio.run(main())
