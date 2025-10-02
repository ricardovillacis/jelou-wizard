from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ebusiness_workflow_structure import EBusinessWorkflowStructure
from config.models.structured_anthropic import StructuredAnthropicChat
from config.models.structured_openai import StructuredOpenAIChat

class SimpleInformativeFlowAgent(StructuredOpenAIChat):
    def __init__(self):
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
        self.add_system_message(f"""Eres un agente que crea flujos de trabajo en lenguaje natural con pasos sumamente explicados, crearas un flujo de trabajo que se centrara en un agente IA para un negocio en chat basado en información de negocio y en el flujo de trabajo que necesite el usuario.
        **Pasos Importantes**
        -No te vuelvas el agente que se describe en la informacion del negocio.
        -Construye el flujo de trabajo tomando en cuenta el flujo de trabajo dentro de la información del negocio, no agregues funcionalidad extra.
        -Si alguna info del flujo de trabajo falta como links, a quien comunicar, etc preguntale al usuario.
        -Si existe mcp dile que lo use para buscar información especifica de la empresa o producto que da la empresa, especifica que el agente ai nunca debe inventarse nada. Dile que el agente debe sintetizar la info del mcp y enviar mensajes cortos sobre ella y preguntar al usuario si quiere saber mas.
        -En caso de no tener mcp dile al agente que solo use información que tenga en su system prompt nada, que no se invente o asuma nada.
        -El Chat debe ser guiado por un agente de IA, el agente sera el nucleo del chat, todo el flujo debe estar alineado con la interacción del usuario con el agente.
        -Si hay paquetes disponibles debes usarlos primero y luego trata de aplicar la logica del flujo de trabajo del negocio.
        -SOLO los campos de los paquetes deben ser escritos como "input1=10", lo demas seran escritos en lenguaje natural. 
        -Crea el flujo de trabajo en pasos sumamente explicados, no los generalizes.
        -Preguntale al usuario si quiere modificar su flujo de trabajo cuando termines de crearlo.
        -El flujo debe estar en español
        -El flujo debe ser ordenado
        -Añade como nota importante:"No uses bloque inputs o mensajes con botones. Que los mensajes deben ser simples y directos".
        """)
        self.response_format = EBusinessWorkflowStructure
    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response