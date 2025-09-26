from ai.agents.Business.business_info_structure import BusinessInfoStructure
from config.models.structured_anthropic import StructuredAnthropicChat

class BusinessAgent(StructuredAnthropicChat):
    def __init__(self):
        super().__init__()
        self.add_system_message(f"""You are a agent that reads what the user said about a business and your tasks is to answer what type of business it is. """)
        self.response_format = BusinessInfoStructure

    
    def get_model_assistant_message(self, model_response):
        return model_response.business_type