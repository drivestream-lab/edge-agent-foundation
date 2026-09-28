"""Main entry point for {{ cookiecutter.agent_name }}."""

import asyncio
import os

import dotenv

from src.app import create_agent
from src.configs.app_settings import AppSettings
from src.logging import get_logger, setup_logging

dotenv_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path=dotenv_path, override=True)

settings = AppSettings.get_instance()
setup_logging(settings)
logger = get_logger()


async def main() -> None:
    agent = create_agent()
    await agent.run_forever()


if __name__ == "__main__":
    logger.info("Launching {{ cookiecutter.agent_name }}", device_id=settings.device_id)
    asyncio.run(main())
