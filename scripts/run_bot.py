"""Production entrypoint for the Telegram runtime.

The process is intentionally deployment-agnostic: GitHub Actions, a VPS,
Docker, or a personal machine can invoke the same entrypoint.
"""

from __future__ import annotations

import asyncio
import logging
import signal

from selfbot.application import create_application
from selfbot.bootstrap import create_runtime


async def run() -> None:
    runtime = create_runtime()
    application = create_application(runtime)

    stop_event = asyncio.Event()

    def request_stop() -> None:
        logging.getLogger(__name__).info("shutdown requested")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_stop)
        except (NotImplementedError, RuntimeError):
            # Windows event loops may not expose add_signal_handler.
            pass

    await application.start()
    try:
        await stop_event.wait()
    finally:
        await application.stop()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
