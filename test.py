from __future__ import annotations
import asyncio
import httpx
import logging
from opencode_ai import Opencode
logging.getLogger("mcp_use").setLevel(logging.CRITICAL)
def test() -> None:

    client = Opencode(base_url="http://127.0.0.1:5000", timeout=httpx.Timeout(60000.0))
    session = client.session.create(extra_body={"title": "Workflow Builder Session"})
    
    
    show_workflow_response = client.session.chat(
        id=session.id,
        model_id="claude-sonnet-4-5-20250929",
        provider_id="anthropic",
        parts=[{"type": "text", "text": "Show me zabyca .wf file content(not summary, I need code)"}],
        timeout=httpx.Timeout(60000.0)
    )
    show_opencode_response(show_workflow_response)

    
    print("\n" + "=" * 60)
    print("💬 Interactive Workflow Editor")
    print("You can now modify the workflow by describing changes.")
    print("Commands: 'show' (display current workflow), 'quit' (exit)")
    print("-" * 60)
    
    # Interactive modification loop
    while True:
        try:
            user_input = input("\n🔧 Your modification request: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'salir']:
                print("👋 Workflow editing session ended!")
                break
            
                
            if not user_input:
                continue
            
            # Send modification request
            print("⚙️  Processing modification...")
            
            modification_response = client.session.chat(
                id=session.id,
                model_id="claude-sonnet-4-5-20250929",
                provider_id="anthropic",
                parts=[{"type": "text", "text": user_input}],
                timeout=httpx.Timeout(60000.0)
            )
            show_opencode_response(modification_response)
            
                
        except KeyboardInterrupt:
            print("\n👋 Workflow editing session ended!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again...")
    
    print(f"\n📝 Final workflow session completed for session: {session.id}")

def show_opencode_response(response):
            # Display the response/updated workflow
            print("\n✅ Response:")
            print("-" * 40)
            if hasattr(response, 'parts') and response.parts:
                response_text = ""
                for part in response.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
                    elif isinstance(part, dict) and 'text' in part:
                        response_text += part['text']
                
                print(response_text)
                
                # Update current workflow if it seems like a new workflow was provided
                if "workflow" in response_text.lower() and ("dsl" in response_text.lower() or "```" in response_text):
                    current_workflow = response_text
                    print("\n🔄 Workflow updated!")
            else:
                print("No response received from server")
if __name__ == "__main__":
    test()