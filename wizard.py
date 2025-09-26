




from typing import List

from ai.agents.Business.business_agent import BusinessAgent
from ai.agents.Business.business_type import BusinessType
from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ecommerce_business_flow_agent import EcommerceBusinessFlowAgent
from ai.agents.QA.QAAgent import QAAgent
from ai.agents.jelou_package.package_filler_agent import PackageFillerAgent
from ai.agents.jelouai.jelou_mcp import JelouMCP




class JelouWizard():
    async def init_packages(self):
        self.database_package = await self.search_package("database creation")
        self.conversational_flow_package = await self.search_package("package-conversational-eco")
        self.payment_method_package = await self.search_package("payment method")

    def initialize_graph(self):
        pass

    async def start_wizard(self):
        try:
            business_info = self.basic_business_info()
            # business_info = """
            # 'Q: Me podrias describir tu negocio?\nA: Rayros Motors es concesionario autorizado Yamaha, con presencia en Supía y Riosucio(occidente de Caldas, Colombia). Se especializa en la venta de motocicletas nuevas, repuestos y accesorios originales, además de ofrecer servicio técnico certificado. El propósito es brindar soluciones de movilidad confiables y un servicio cercano a la comunidad.\n\nQ: Que vendes? Como lo vendes?\nA: Venta de motocicletas Yamaha. Venta de repuestos y accesorios originales. Servicio técnico especializado con personal capacitado directamente por Yamaha. Créditos y financiación a través de Rayros Servicios Financieros.\n\nQ: Me podrias decir la ubicación/ubicaciones de tu negocio?\nA: No desea proporcionar la ubicación del negocio.\n\nQ: Qué es lo que hace tu negocio diferente?\nA: Son concesionarios autorizados Yamaha con respaldo de marca mundial. Brindan atención cercana y personalizada en municipios intermedios y rurales. Cuentan con servicio técnico certificado y técnicos capacitados por Yamaha. Tienen más de 10 años de experiencia en el sector. Ofrecen opciones de financiación flexibles mediante una fintech aliada.\n\nQ: ¿Que frases frecuentes usan tus clientes para referirse a tu negocio, tus producto/servicio?\nA: Los clientes llaman al negocio "Raycar".\n\nQ: ¿Cómo te conocen tus clientes?\nA: Known as Raycar by clients.\n\nQ: ¿Con que frases saludas a tus clientes? ¿Cómo quieres que se presente el Agente IA a tus clientes?\nA: No se utilizan frases especiales para saludar al cliente, se utilizan frases comunes.\n\nQ: Cual es el proposito de crear al agente(Vender productos, agente)\nA: El propósito de crear al agente es vender productos por WhatsApp.'
            # """
            business_type = self.check_business_info(business_info=business_info)
            if business_type == BusinessType.e_commerce:
                packages = self.fill_packages_inputs([self.conversational_flow_package, self.payment_method_package])
                formatted = self.format_packages_as_calls(packages)
                formatted =f"Paquete {self.database_package.name} sin inputs."+formatted

            else:
                packages = self.fill_packages_inputs([self.conversational_flow_package])
                formatted = self.format_packages_as_calls(packages)
            workflow  = self.create_ebusiness_workflow(business_info, formatted)
            return f"Business INFO:{business_info}\nFlujo:{workflow.business_workflow}"

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
        {"question":"¿Con que frases te despides a tus clientes?"},
        {"question":"¿Cual quieres que sea el tono de conversación?"},
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
        
        jelou_mcp = JelouMCP()
        response = await jelou_mcp.get_package_info(prompt)
        return response
        

    def check_business_info(self,business_info):
        business_agent = BusinessAgent()
        response = business_agent.send_message(business_info)
        return response.business_type

    def ask_questions(self, questions: List[dict]):
        answers = []
        for question_dict in questions:
            question = question_dict.get("question")
            required = question_dict.get("required", True)

            print(question)
            qa_agent = QAAgent(question=question)
            user_answer = None

            while True:
                user_message = input(">>> ")
                if not user_message:
                    if required:
                        print("La pregunta es obligatoria. Por favor, responde.")
                        continue
                    else:
                        break

                response = qa_agent.send_message(user_message)
                print(response.bot_response)

                user_answer = {"question": question, "answer": response.user_description}

                if response.finished:  # ya validó la respuesta
                    answers.append(user_answer)
                    break  # pasar a la siguiente pregunta
        return answers

    def fill_package_inputs(self,package_info):
            still_responding = True
            pf_agent = PackageFillerAgent(package_info)
            response = pf_agent.send_message("Ask about the package inputs")
            while(still_responding):
                print(getattr(response, "bot_response", ""))
                user_message = input(">>>")
                response = pf_agent.send_message(user_message)
                all_filled = bool(getattr(response, "all_inputs_filled", False))
                user_confirmed = bool(getattr(response, "user_confirmed", False))
                if all_filled and user_confirmed:
                    print(getattr(response, "bot_response", ""))
                    return response
    def create_ebusiness_workflow(self,business_info, packages_info):
        still_responding = True
        ecom_business_agent = EcommerceBusinessFlowAgent(business_info, packages_info)
        response = ecom_business_agent.send_message("Show me the workflow.")
        while(still_responding):
            print(getattr(response, "bot_response", ""))
            user_message = input(">>>")
            response = ecom_business_agent.send_message(user_message)
            user_confirmed = bool(getattr(response, "user_confirmed", False))
            if user_confirmed:
                print(getattr(response, "bot_response", ""))
                return response
    def fill_packages_inputs(self, packages_info):
        packages = []
        for package_info in packages_info:
            package = {"usage":package_info.usage,"info":self.fill_package_inputs(package_info)}
            packages.append(package)
        return packages

    def format_packages_as_calls(self, packages: List) -> str:
        calls: List[str] = []
        for pkg in packages:
            usage = getattr(pkg, "usage", None)
            info = getattr(pkg, "info", None)
            if usage is None and isinstance(pkg, dict):
                usage = pkg.get("usage")
            if info is None and isinstance(pkg, dict):
                info = pkg.get("info")

            name = None
            inputs = None
            if info is not None:
                if isinstance(info, dict):
                    name = info.get("package_name")
                    inputs = info.get("package_inputs")
                else:
                    name = getattr(info, "package_name", None)
                    inputs = getattr(info, "package_inputs", None)

            if not name:
                continue

            inputs_str = "" if inputs is None else (inputs if isinstance(inputs, str) else str(inputs))
            if usage:
                calls.append(f"Paquete \"{name}\" con las siguientes inputs:\n{inputs_str}.")
            else:
                calls.append(f"Paquete \"{name}\" con las siguientes inputs:\n{inputs_str}.")
        return "\n\n".join(calls)

    def _format_answers(self, answers:List[dict]) -> str:
        """Return a single string concatenating questions and answers."""
        parts: List[str] = []
        for item in answers:
            q = item.get("question", "")
            a = item.get("answer", "")
            parts.append(f"Q: {q}\nA: {a}")
        return "\n\n".join(parts)
