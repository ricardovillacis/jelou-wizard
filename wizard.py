




from typing import List

from ai.agents.Business.business_agent import BusinessAgent
from ai.agents.Business.business_type import BusinessType
from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.QA.QAAgent import QAAgent
from ai.agents.jelouai.jelou_mcp import JelouMCP



class JelouWizard():

    def initialize_graph(self):
        pass

    async def start_wizard(self):
        try:
            #business_info = self.basic_business_info()
            #business_type = self.check_business_info(business_info=business_info)
            print("Searching for database creation package...")
            database_package = await self.search_package("database creation")
            print(f"Found package: {database_package.name}")
            print(f"Version: {database_package.version}")
            print(f"Usage: {database_package.usage}")
            # if business_type == BusinessType.e_commerce:
            #     ecommerce_info = self.ecommerce__business_info()
            #     business_info += "\n" + ecommerce_info
            #     database_package = self.search_package()

            return database_package
        except Exception as e:
            print(f"Error in start_wizard: {e}")
            raise 

    def basic_business_info(self):
        questions = [{"question":"Me podrias describir tu negocio?","required":True},
        {"question":"Que vendes? Como lo vendes?"},
        {"question":"Me podrias decir la ubicación/ubicaciones de tu negocio?","required":True},
        {"question":"Qué es lo que hace tu negocio diferente?"},
        {"question":"¿Que frases frecuentes usan tus clientes para referirse a tu negocio, tus producto/servicio?"},
        {"question":"¿Cómo te conocen tus clientes?"},
        {"question":"¿Con que frases saludas a tus clientes? ¿Cómo quieres que se presente el Agente IA a tus clientes?"},
        {"question":"Cual es el proposito de crear al agente(Vender productos, agente)"}]

        answers = self.ask_questions(questions=questions)
        return self._format_answers(answers)
    
    def ecommerce__business_info(self):
        questions =[{"question":"Que tipo de agente se creará?(Agente conversacional, Agente conversacional con carrito, Agente  catalogo nativo, Agente de agendamiento)"}, {"question":"Cuales son los metodos de pagos?"},
        {"question":"Será productos o servicios?"},{"question":"Lleva pma(conectar con asesores humanos) y notificaciones?"},
        {"question":"Lleva pasarela de pagos?"}]
        answers = self.ask_questions(questions=questions)
        return self._format_answers(answers)


    def business_flow_questions(self):
        questions = [{}]
    
    async def search_package(self, prompt):
        
        jelou_mcp = JelouMCP(mcp_server_config=mcp_config)
        response = await jelou_mcp.get_package_info(prompt)
        return response
        

    def check_business_info(self,business_info):
        business_agent = BusinessAgent()
        response = business_agent.send_message(business_info)
        return response.business_type

    def ask_questions(self,questions:List[dict]):
        answers = []
        for question_dict in questions:
            question = question_dict.get("question")
            required  = question_dict.get("required")
            print(question)
            still_responding = True
            user_answer = None
            while(still_responding):
                user_message = input(">>>")
                if not user_message:
                    print("No se ha respondido la pregunta,porfavor respondala.")
                    continue
                qa_agent = QAAgent(question=question)
                response = qa_agent.send_message(user_message)
                print(response.bot_response)
                if response.finished:
                    if not user_answer:
                        print("No se ha respondido la pregunta,porfavor respondala.")
                        continue
                    answers.append(user_answer)
                    still_responding = False
                else:
                    user_answer = {"question":question,"answer":response.user_description}
        return answers

    def _format_answers(self, answers:List[dict]) -> str:
        """Return a single string concatenating questions and answers."""
        parts: List[str] = []
        for item in answers:
            q = item.get("question", "")
            a = item.get("answer", "")
            parts.append(f"Q: {q}\nA: {a}")
        return "\n\n".join(parts)