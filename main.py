from __future__ import annotations
import asyncio

from wizard import JelouWizard


async def main() -> None:
    jelou_wizard = JelouWizard()
    result = await jelou_wizard.start_wizard()
    print(f"Wizard completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())