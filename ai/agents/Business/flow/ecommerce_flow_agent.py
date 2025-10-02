from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ebusiness_workflow_structure import EBusinessWorkflowStructure
from config.models.structured_anthropic import StructuredAnthropicChat
from config.models.structured_openai import StructuredOpenAIChat

class EcommerceFlowAgent(StructuredOpenAIChat):
    def __init__(self,business_info,packages):
        super().__init__()
        # self.add_system_message(f"""You are an agent that will create a ai agent workflow of tasks using for a chat e-business based on business 
        # info and also on what the user tells you needs to be in the workflow.
        # **Business info**
        # {business_info}
        # **Available Packages**
        # {packages}
        # **Important steps**
        # -If theres a business workflow try to make
        # -Make it AI agent driven chat, the core of the chat is an ai agent, having said that all flow should be align to user saying something to the ai, for example write as "If the user tells the ai to schedule a plan then the ai will...".
        # -You will create a default workflow based on the business info using all available package with his inputs.
        # -ONLY package inputs should be written as "input1=10", other should be written as natural language.
        # -Make the workflow in specific micro steps never generalized.
        # -Ask the user if he want to modify the workflow when the default workflow is already created.
        # -Workflow should be in spanish.
        # -Workflow should ordered steps.
        # -Add as a note in your workflow that the ai could use a method of getting specific information of the business with rag methods.
        # -Add as a note to don't use inputs, just use ai.

        # **Example**
        # When the user writes then make the ai agent tell basic info of the business and what are the options

        # If the user writes to the ai to ask for more information the ai will gather information about the categories available that it has and then tell the user the categories.
        # If the user asks about one category the ai will gather information about that category and tell the user this info.
        # In case of having a ai response problem then send a message saying that there was a problem try again.
        # If the user wants to schedule something to the ai then execute a schedule package (**ONLY IF THE PACKAGE IS AVAILABLE**)
        # ...
        # """)
        self.add_system_message(f"""Eres un agente que creara un flujo de trabajo que se centrara en un agente IA para un negocio en chat basado en información de negocio y en el flujo de trabajo que necesite el usuario.
        
        **Información de negocio**
        {business_info}
        **Paquetes disponibles**
        {packages}
        **Pasos Importantes**
        -Usa el primer paquete
        -Usa el segundo paquete luego del primero
        -Usa la respuesta del segundo paquete para hacer un flujo condicional.
        -Si la respuesta del segundo paquete es que el cliente quiere comprar conectalo con el tercer paquete.
        -SOLO los campos de los paquetes deben ser escritos como "input1=10", lo demas seran escritos en lenguaje natural. 
        -Preguntale al usuario si quiere modificar su flujo de trabajo cuando termines de crearlo.
        -El flujo debe estar en español
        -El flujo debe ser ordenado
        -Añade como nota importante:"No uses bloque inputs o mensajes con botones. Di en las notas que los mensajes deben ser simples y directos".
        """)

        self.response_format = EBusinessWorkflowStructure
    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response