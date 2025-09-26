from ai.agents.jelou_package.package_inputs import PackageInputsStructure
from config.models.structured_anthropic import StructuredAnthropicChat
class PackageFillerAgent(StructuredAnthropicChat):
    def __init__(self, package_info):
        super().__init__()
        self.add_system_message(f"""Your are an agent that will ask about a jelou package inputs like it were questions to the user,
         when all inputs are filled tell the user all that is filled and ask for confirmation or correction.
         Package info: {package_info}.
         
         **Important**
         Ask in spanish.
         Ask each required value one by one first.
         After asking about all required values then tell to the user all posible optional values and then ask the user if he wants to add values to them""")
        self.response_format = PackageInputsStructure

    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response