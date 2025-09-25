from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent

class EcommerceBusinessFlowAgent(BusinessFlowAgent):
    def __init__(self):
        super().__init__()
        self.add_system_message(f"""You are an agent that will create a workflow of tasks based on business 
        info and also on what the user tells you needs to be in the workflow.
        **Workflow Template**
        1.
        """)
    
