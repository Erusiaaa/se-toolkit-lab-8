"""Part B — Schedule proactive health check and capture the report."""

import asyncio
import json
import websockets


async def main():
    url = "ws://nanobot:8765/ws/chat?access_key=nano-web-pass-789"
    print(f"Connecting to {url}...")

    async with websockets.connect(url, close_timeout=5) as ws:
        # Step 1: Create health check cron job
        prompt = (
            "Create a health check for this chat that runs every 2 minutes. "
            "Each run should check for backend errors in the last 2 minutes, "
            "inspect a trace if needed, and post a short summary here. "
            "If there are no recent errors, say the system looks healthy. "
            "Use your cron tool."
        )
        print(f"\n>>> Sending: {prompt[:100]}...")
        await ws.send(json.dumps({"content": prompt}))

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

        cron_confirmation = responses[-1].get("content", "")
        print("\n" + "=" * 80)
        print("CRON JOB CREATION RESPONSE:")
        print("=" * 80)
        print(cron_confirmation)
        print("=" * 80)

        # Step 2: List scheduled jobs
        print("\n>>> Sending: List scheduled jobs.")
        await ws.send(json.dumps({"content": "List scheduled jobs."}))

        list_responses = []
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=120 if not list_responses else 30)
                data = json.loads(raw)
                list_responses.append(data)
                t = data.get("type", "unknown")
                content_preview = str(data.get("content", ""))[:120]
                print(f"  [{len(list_responses)}] type={t}, preview={content_preview}...")
            except (TimeoutError, asyncio.TimeoutError):
                if list_responses:
                    break
                raise

        jobs_list = list_responses[-1].get("content", "")
        print("\n" + "=" * 80)
        print("SCHEDULED JOBS LIST:")
        print("=" * 80)
        print(jobs_list)
        print("=" * 80)

        # Save all responses
        with open("/tmp/task4b_cron_confirmation.txt", "w") as f:
            f.write(cron_confirmation)
        with open("/tmp/task4b_jobs_list.txt", "w") as f:
            f.write(jobs_list)

        print("\nNow waiting for cron to trigger... Check chat for proactive reports.")
        print("The proactive report will appear in the nanobot logs.")


if __name__ == "__main__":
    asyncio.run(main())
