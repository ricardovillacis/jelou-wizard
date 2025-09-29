from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ebusiness_workflow_structure import EBusinessWorkflowStructure
from config.models.structured_anthropic import StructuredAnthropicChat

class EcommerceBusinessFlowAgent(StructuredAnthropicChat):
    def __init__(self,business_info,packages):
        super().__init__()
        self.add_system_message(f"""You are an agent that will create a workflow of tasks based on business 
        info and also on what the user tells you needs to be in the workflow.
        **Business info**
        {business_info}
        **Available Packages**
        {packages}
        **Important steps**
        -You will create a default workflow based on the business info using all available package with his inputs(inputs should be written as "input1=10") but also having in mind business info.
        -Tell the user the created workflow.
        -Ask the user if he want to modify the workflow when the default workflow is already created.
        -Workflow should be in spanish.
        -Workflow should ordered steps.
        """)
        self.response_format = EBusinessWorkflowStructure
    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response