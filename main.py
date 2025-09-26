from __future__ import annotations
import asyncio

from wizard import JelouWizard
import logging
logging.getLogger("mcp_use").setLevel(logging.CRITICAL)

async def main() -> None:
    jelou_wizard = JelouWizard()
    print("Loading Packages")
    await jelou_wizard.init_packages()
    print("packages loaded")
    result = await jelou_wizard.start_wizard()
    print(f"Wizard completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())