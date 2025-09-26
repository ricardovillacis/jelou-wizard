from __future__ import annotations
import asyncio
import sys

from wizard import JelouWizard
import logging
from opencode_ai import Opencode
logging.getLogger("mcp_use").setLevel(logging.CRITICAL)

async def main() -> None:
    jelou_wizard = JelouWizard()
    print("Loading Packages")
    await jelou_wizard.init_packages()
    print("packages loaded")
    result = await jelou_wizard.start_wizard()
    print(f"Wizard completed with result: {result}")

#     client = Opencode(base_url="http://localhost:52461")

#     sessions = client.session.list()
#     session = client.session.create({
#     "name": "test_session"
# })
#     response = client.instruction.create(
#     session_id=session.id,
#     input=result
# )
#     print(response)

if __name__ == "__main__":
    asyncio.run(main())