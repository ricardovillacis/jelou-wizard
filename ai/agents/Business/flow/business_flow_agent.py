from ai.agents.Business.business_info_structure import BusinessInfoStructure
from config.models.structured_anthropic import StructuredAnthropicChat


class BusinessFlowAgent(StructuredAnthropicChat):
    def __init__(self):
        super().__init__()
        self.add_system_message(f"""You are an agent that will create a workflow of tasks based on business 
        info and also on what the user tells you needs to be in the workflow""")
        self.response_format = BusinessInfoStructure
    
    
    def get_model_assistant_message(self, model_response):
        return model_response