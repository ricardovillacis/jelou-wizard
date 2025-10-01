from typing import Dict, List
import datetime
import os
import json
from types import SimpleNamespace

from ai.agents.Business.business_agent import BusinessAgent
from ai.agents.Business.business_type import BusinessType
from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ecommerce_business_flow_agent import EcommerceBusinessFlowAgent
from ai.agents.QA.QAAgent import QAAgent
from ai.agents.jelou_package.package_filler_agent import PackageFillerAgent
from ai.agents.jelouai.jelou_mcp import JelouMCP



class JelouWizard():
    def __init__(self):
        self._package_cache = {}
        self._cache_path = os.path.join(os.getcwd(), ".package_cache.json")
        self._load_cache_from_disk()

    def _load_cache_from_disk(self):
        if os.path.exists(self._cache_path):
            try:
                with open(self._cache_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._package_cache = {}
                for query, rec in raw.items():
                    ts = datetime.datetime.fromisoformat(rec.get("ts"))
                    data_dict = rec.get("data", {})
                    pkg = SimpleNamespace(**data_dict)
                    self._package_cache[query] = (ts, pkg)
            except Exception:
                self._package_cache = {}

    def _save_cache_to_disk(self):
        serializable = {}
        for query, (ts, pkg) in self._package_cache.items():
            if isinstance(pkg, SimpleNamespace):
                data_dict = dict(pkg.__dict__)
            elif isinstance(pkg, dict):
                data_dict = dict(pkg)
            else:
                data_dict = getattr(pkg, "__dict__", {}) if hasattr(pkg, "__dict__") else {"name": getattr(pkg, "name", None)}
            # ensure JSON-serializable values
            for k, v in list(data_dict.items()):
                try:
                    json.dumps(v)
                except TypeError:
                    data_dict[k] = str(v)
            serializable[query] = {"ts": ts.isoformat(), "data": data_dict}
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f)

    async def init_packages(self):
        # In-memory and disk-backed cache for package lookups with 24h freshness
        now = datetime.datetime.utcnow()
        one_day = datetime.timedelta(days=1)

        cache_map = [
            ("database creation", "database_package"),
            ("package-conversational-eco", "conversational_flow_package"),
            ("payment method", "payment_method_package"),
        ]
        for query, attr in cache_map:
            cached = self._package_cache.get(query)
            if cached:
                ts, data = cached
                try:
                    if now - ts < one_day:
                        setattr(self, attr, data)
                        continue
                except Exception:
                    pass
            data = await self.search_package(query)
            setattr(self, attr, data)
            self._package_cache[query] = (now, data)
        self._save_cache_to_disk()

    def initialize_graph(self):
        pass

    async def start_wizard(self):
        try:
            formatted = "No packages"
            business_info = self.basic_business_info()
            # business_info = """**Me podrias describir tu negocio?**\nSocio estratégico experto en la transformación digital empresarial a través de Odoo. Especializados en implementación, personalización y consultoría de ERP, diseñando soluciones a medida alineadas con objetivos de negocio.\n\n**Que vendes? Como lo vendes?**\nImplementación, personalización, soporte y capacitación para Odoo ERP. Integración de módulos: Ventas, CRM, Inventario, Contabilidad, Compras, Nómina, Comercio electrónico, entre otros.\n\n**Me podrias decir la ubicación/ubicaciones de tu negocio?**\nQuito: Luxemburgo N34-80, Guayaquil: Bálsamos 112, Cuenca: Av. Ordóñez Lasso 5-60, Miami: 17861 NW 19TH Street, Pembroke Pines, FL 33029\n\n**Qué es lo que hace tu negocio diferente?**\nExperiencia probada, consultores expertos, metodología propia, módulos integrados, personalización y adaptabilidad, soporte continuo, tecnología actualizada, Primer Partner Gold Oficial de Odoo en Ecuador\n\n**¿Con que frases saludas a tus clientes? ¿Cómo quieres que se presente el Agente IA a tus clientes?**\nMúltiples opciones de saludo personalizadas como agente virtual de ZABYCA\n\n**¿Con que frases te despides a tus clientes?**\nVarias opciones de despedida cordial y profesional\n\n**¿Cual quieres que sea el tono de conversación?**\nAmigable, cercano, profesional, claro, entusiasta, confiable y paciente\n\n**¿Cual sera el flujo de trabajo propuesto?**\n1.Saludo y bienvenida 2.Descubrimiento de necesidades 3.Presentación de servicios/productos 4.Formulario envío de la información\n\n**¿Tienes algun mcp con información del negocio(Brinda el link)?**\nhttps://jelou-marketplace-w9xssz3s5tyx.deno.dev/mcp
            # """
            business_type = self.check_business_info(business_info=business_info)
            if business_type == BusinessType.e_commerce:
                packages = self.fill_packages_inputs([self.conversational_flow_package, self.payment_method_package])
                formatted = self.format_packages_as_calls(packages)
                formatted =f"Paquete {self.database_package.name} con inputs {{}}."+formatted
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
        {"question":"¿Con que frases saludas a tus clientes? ¿Cómo quieres que se presente el Agente IA a tus clientes?"},
        {"question":"¿Con que frases te despides a tus clientes?"},
        {"question":"¿Cual quieres que sea el tono de conversación?"},
        {"question":"¿Cual sera el flujo de trabajo propuesto?"},
        {"question:":"¿Tienes algun mcp con información del negocio(Brinda el link)?"}
        ]

        answers = self.ask_questions(questions=questions)
        return self._format_answers(answers)
    
    async def search_package(self, prompt):
        
        jelou_mcp = JelouMCP()
        response = await jelou_mcp.get_package_info(prompt)
        return response
        
    def check_business_info(self,business_info):
        business_agent = BusinessAgent()
        response = business_agent.send_message(business_info)
        return response.business_type

    def ask_questions(self, questions: List[dict]):
        qa_agent = QAAgent(question=questions)
        response = qa_agent.send_message("Start asking me the questions as you were a Q&A Agent called Jelou Wizard.")
        print(response.bot_response)
        user_answer = None
        

        while True:
            user_message = input(">>> ")
            if not user_message:
                continue
            print("")
            response = qa_agent.send_message(user_message)

            user_answer = response.user_description
            if response.all_questions_answered:
                print(user_answer)
                print(response.bot_response+"\n")
            else:
                print(response.bot_response+"\n")
            if response.finished:  # ya validó la respuesta
                return response.updated_slots

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
                    print(getattr(response, "bot_response", "")+"\n")
                    return response
    def create_ebusiness_workflow(self,business_info, packages_info):
        still_responding = True
        ecom_business_agent = EcommerceBusinessFlowAgent(business_info, packages_info)
        response = ecom_business_agent.send_message("Dame el flujo de trabajo.")
        print(getattr(response, "bot_response", ""))
        while(still_responding):
            user_message = input(">>>")
            response = ecom_business_agent.send_message(user_message)
            user_confirmed = bool(getattr(response, "user_confirmed", False))
            if response.user_want_workflow:
                print(response.business_workflow)
                print(getattr(response, "bot_response", ""))
            else:
                print(getattr(response, "bot_response", ""))

            if user_confirmed:
                print(getattr(response, "bot_response", "")+"\n")
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

    def _format_answers(self, answers: Dict[str, str]) -> str:
        """Return a single string concatenating questions and answers."""
        parts: List[str] = []
        for q, a in answers.items():
            parts.append(f"**{q}**\n{a}")
        return "\n\n".join(parts)
