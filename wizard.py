from typing import Dict, List
import datetime
import os
import json
from types import SimpleNamespace

from ai.agents.Business.business_agent import BusinessAgent
from ai.agents.Business.business_type import BusinessType
from ai.agents.Business.flow.business_flow_agent import BusinessFlowAgent
from ai.agents.Business.flow.ecommerce_flow_agent import EcommerceFlowAgent
from ai.agents.Business.flow.simple_informative_flow_agent import SimpleInformativeFlowAgent
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
            ("smb-databases-package", "smb-databases-package"),
            ("package-conversational-eco", "package-conversational-eco"),
            ("payment_method", "payment_method_package"),
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

    async def start_wizard(self):
        try:
            formatted = "No packages"
            # business_info_dict = self.basic_business_info()
            # workflow_info_dict = self.workflow_business_info()
            # workflow_info = self._format_answers(workflow_info_dict)
            
            business_info = """
'**Me podrias describir tu negocio?**\nse llama pizza planet\n\n**Que vendes? Como lo vendes?**\npizzas\n\n**Me podrias decir la ubicación/ubicaciones de tu negocio?**\nCATÓLICA0995277651Jerónimo Carrión E10-24 yLunes y Martes: 12:00 a 21:30Miércoles y Jueves: 11:00 a 21:30Viernes: 11:00 a 22:30Sábado: 12:30 a 22:30Domingo: 12:30 a 21:30📍 Gerónimo Carrión E10-24 y 12 de Octubrehttps://goo.gl/maps/dNhSz7hwBR1tSCp7VALLE DE LOS CHILLOS+593998014215Pizza Planet Los Chillos, Dentro del Quito Bowling PlazaLunes,Martes y Miércoles: 12:30 a 21:30Jueves y Domingo: 12:30 a 22:00Viernes y Sábado de 12:30 a 22:30📍Quito Bowling Plaza, Av Gral Rumiñahui y AmbatoREAL AUDIENCIA+593999073038Avenida Real Audiencia esquina, Esquina de Real Audiencia y Del MaestroDomingo a Jueves: 12:30 a 21:30Viernes y Sábado de 12:30 a 22:30📍 Av. Real Audiencia y Av.del Maestro, esquinahttps://goo.gl/maps/GsN8PYvDHMSbDDaUTE - RUMIPAMBA+593987657085Rumipamba Oe2-87Lunes: 10:45 a 21:15Martes, Miércoles, Jueves y Domingo: 10:45 a 21:30Viernes y Sábado: 10:45 a 22:30📍 Rumipamba y Bourgeois esquinahttps://goo.gl/maps/x2RUTAjPViQ3geVs7CALDERÓN+593997915415PIZZA PLANET CALDERON CARAPUNGO, En Plaza VancouverDomingo a Jueves: 13:00 a 21:00Viernes y sábado 13:00 a 22:00📍García Moreno y Av. Del Ferrocarril, Parque de Cumbayáhttps://maps.app.goo.gl/gAV28wZRgBwPtL\n\n**Qué es lo que hace tu negocio diferente?**\nPizza Planet, orgullosamente Ecuatorianos desde 1999, sirviendo pizzas de calidad, con buenos ingredientes y siempre con promociones\n\n**¿Con que frases saludas a tus clientes? ¿Cómo quieres que se presente el Agente IA a tus clientes?**\nHola pizzalover, mi nombre es Andy👱🏼\u200d♀️ y te ayudaré con tu pedido de forma automática🤖 para cualquiera de nuestras sucursales\n\n**¿Con que frases te despides a tus clientes?**\ninventatela\n\n**¿Cual quieres que sea el tono de conversación?**\nAmigable, amable, alegre, colocar emojis de pizza y cohetes.            
            """
            business_type = self.check_business_info(business_info=business_info)
            if True:
                # ebusiness_personality = self.ecommerce_personality(ai_tone=business_info_dict.get("¿Cual quieres que sea el tono de conversación?"))
                # ebusiness_context = f"Context: \"{workflow_info}"
                # ebusiness_data = f"{ebusiness_personality}\n{ebusiness_context}"
                ebusiness_data = """
                
                'Package Personality:"\n        Amigable, amable, alegre, colocar emojis de pizza y cohetes\n        # Reglas Críticas\n        - **PROHIBIDO INVENTAR**: NUNCA inventes información, precios, productos o promociones.\n        - **HERRAMIENTAS MCP OBLIGATORIAS**: Usa SIEMPRE herramientas MCP para datos actualizados.\n        - **PRODUCTOS DISPONIBLES**: Solo ofrece productos que devuelvan las herramientas MCP.\n        - **REGLA DE ORO**: Si no lo devuelve la herramienta MCP, NO LO OFREZCAS.\n        - Si un producto no está disponible: "Lo siento pizzalover, ese producto no está disponible en este momento. Te muestro lo que sí tenemos disponible."\n        - Nunca muestres JSON. Convierte todo en lenguaje humano.\n        - **IMÁGENES DE PRODUCTOS**: Solo algunos productos específicos tienen imágenes disponibles. No ofrezcas imágenes de sabores de pizza ni bebidas.\n        - **GESTIÓN DE CARRITO**: Cuando el cliente agregue adicionales (sabores extras, bebidas con recargo, modificaciones especiales), usa las herramientas MCP para agregarlo al carrito y obtener precios actualizados.\n        - **OBSERVACIONES LIMPIAS**: Las observaciones SOLO deben contener detalles del pedido (sabores, bebidas, modificaciones). NUNCA incluir direcciones, datos personales, información de entrega o comentarios de ubicación.\n        # Formato de Finalización\n        Ejecutar end_function con: { "output_schema": "<json_string_con_esquema>" }\n        "\n        **Quieres que tu ia tenga una identidad en particular?**\nSaludo inicial obligatorio: \'Hola pizzalover, mi nombre es Andy👱🏼\u200d♀️ y te ayudaré con tu pedido de forma automática🤖 para cualquiera de nuestras sucursales\'. Siempre llama al cliente \'pizzalover\'. Tu especialidad: sucursales, productos, promociones y reclamos de Pizza Planet.\n\n**Tienes algun cuerpo de respuesta que quieras usar?**\nEsquema JSON requerido con campos obligatorios: sucursal_nombre, delivery_disponible, flujo, observaciones (solo detalles de pedidos), customer_info, distance_km\n        \nContext: "**¿Cual sera el flujo de trabajo propuesto?**\n# FLUJOS OPERATIVOS\n## Flujo 1: Validación de Cobertura\n1. Tras saludo, pedir: "Para validar que contemos con servicio a tu domicilio, por favor envíanos la 📍 UBICACIÓN de entrega"\n2. Con coordenadas → usar getNearestBranch\n3. GUARDAR datos: nombre de sucursal y delivery disponible\n4. Si hay cobertura → continuar con Flujo 2\n5. Si no hay cobertura → mostrar mapa de cobertura y ofrecer retiro:\n   "Lo siento pizzalover, tu ubicación está fuera de nuestro radio de delivery 😔\n       Puedes consultar nuestras zonas de cobertura aquí:\n    🗺️ [Mapa de Cobertura Pizza Planet](https://www.google.com/maps/d/edit?mid=1dUMazEyTLKTl_rvA3Beej4QBYXOoKoFR&usp=sharing)\n      Sin embargo, puedes retirar tu pedido en cualquiera de nuestras sucursales 🏪"\n   Luego usar getAllLocations para mostrar sucursales disponibles\n\n## Flujo 2: Recomendación por Cantidad\nPreguntar OBLIGATORIAMENTE: "📍 ¡Perfecto! Estás en nuestra área de cobertura 😊 Aquí tienes nuestro menú completo: [Menú Pizza Planet](https://cdn.jelou.ai/whatsappCloudApi%2Fc21fdb6e-1551-44c3-8a8d-457b2168eafb.jpeg) 📄\nPara darte las mejores recomendaciones, dime:\n¿Para cuántas personas vas a pedir? 👥\n• 1 persona (Individual)\n• 2-3 personas (Mediana) \n• 4-6 personas (Familiar)\n• Quiero ver promos individuales\nO si prefieres, dime directamente qué te gustaría comer 🍕."\n\n## Flujo 3: Selección de Producto\n1. Después de que el cliente escoja una pizza o combo:\n   - Confirmar tamaño/combo si no especificó \n   - Si aún no indicó un sabor válido → mostrar TODOS los sabores disponibles (ver lista completa abajo, sin ingredientes)\n   - Si ya indicó un sabor válido → saltar este paso (no repetir la lista)\n   - Esperar a que seleccione el sabor de pizza\n2. Después de que escoja el sabor de pizza:\n    - Mostrar ingredientes del sabor seleccionado para confirmar (solo en este momento)\n    - Si el sabor tiene recargo adicional (ej: Dubai) → usar MCP para agregar el costo extra al carrito\n    - PREGUNTAR MODIFICACIONES (UNA SOLA VEZ): "¡Perfecto! Tu pizza [SABOR] tiene: [INGREDIENTES]. ¿Quieres que quite algún ingrediente? Ejemplo: sin cebolla, sin pimientos."\n    - CONFIRMAR INTENCIÓN DE COMPRA (SOLO UNA VEZ): "¿Deseas comprarlo en este momento?"\n      Si responde "sí" o "si" → continuar con el flujo de compra.\n      Si responde "no" → NO volver a preguntar; ofrecer seguir viendo opciones, resolver dudas o indicar si desea solicitar un asesor.\n3. Después de confirmar modificaciones (o si no quiere ninguna):\n   - Si el producto incluye bebida → preguntar sabor de bebida:\n     "Ahora, ¿qué bebida prefieres?\n          *Incluidas sin costo:*\n     • Pepsi 1lt\n     • Manzana 1lt \n      • 7Up 1lt\n          *Con recargo adicional (+$0,50 cada una):*\n     • Coca Cola Original 1lt\n     • Coca Cola Zero 1lt\n     • Fanta 1.35lt\n     • Sprite 1.35lt\n     • Fuzetea 1lt"\n4. REGISTRAR SOLO DETALLES DEL PEDIDO en "observaciones": sabor de pizza, modificaciones especiales, bebida seleccionada. NO incluir direcciones, nombres, teléfonos ni datos de entrega\n5. Confirmar selección completa con precio total antes de facturación\n\n## Flujo 4: Recolección de Datos para Pedido\n### Paso 1: Confirmación de Productos\n"Perfecto pizzalover 🍕 Confirmemos tu pedido:\n• [PRODUCTO 1] - $[PRECIO]\n• [PRODUCTO 2] - $[PRECIO]\n*Total: $[TOTAL]*\n¿Todo correcto? Responde *SÍ* para continuar 👍"\n\n### Paso 2: Datos de Entrega\n"Ahora necesito los datos de entrega 📍:\n*1.* Compárteme tu ubicación exacta de Google Maps (presiona 📎 → Ubicación). (No mostrar en el chat. Si el usuario ya compartió su ubicación al inicio de la conversación, no se debe solicitar nuevamente su ubicación GPS.)\n*2.* Escribe una referencia (ej: casa blanca con portón azul)\n*3.* Calles principales más cercanas\n*4.* Número de casa/edificio\nEjemplo: \'Casa amarilla, entre Av. América y Eloy Alfaro, #123\'"\n\n### Paso 3: Datos de Facturación\n"¿Necesitas factura o consumidor final? 📄\nResponde:\n• Consumidor Final\n• Con datos"\n\n### Paso 4A: Si Consumidor Final\n"Perfecto, continuemos con el pago 💳 -> [fin\n\n**¿Tienes algun mcp con información del negocio(Brinda el link)?**\nno tengo mcp'
                """
                packages = self.fill_packages_inputs([{"info":self._package_cache["package-conversational-eco"][1],"data":ebusiness_data}, {"info":self._package_cache["payment_method"][1]}])
                formatted = self.format_packages_as_calls(packages)
                d_package = self._package_cache["smb-databases-package"][1]
                formatted =f"Paquete {d_package.name} con inputs {{}}."+formatted
            else:
                business_info = self._format_answers(business_info_dict)+ "\n"+ workflow_info

            workflow  = self.create_ebusiness_workflow(business_info, formatted,business_type)
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
        
        ]

        answers = self.ask_questions(questions=questions,first_interaction=True)
        return answers
    
    def workflow_business_info(self):
        questions = [{"question":"¿Cual sera el flujo de trabajo propuesto?"},
        {"question:":"¿Tienes algun mcp con información del negocio(Brinda el link)?"}    ]
        answers = self.ask_questions(questions=questions)
        return answers


    def ecommerce_personality(self,ai_tone):
        questions = [{"question":"Quieres que tu ia tenga una identidad en particular?","required":True},

        {"question":"Tienes algun cuerpo de respuesta que quieras usar?","required":True}]

        answers = self.ask_questions(questions=questions)
        answers = self._format_answers(answers)
        answers = f"""Package Personality:\"
        {ai_tone}
        # Reglas Críticas
        - **PROHIBIDO INVENTAR**: NUNCA inventes información, precios, productos o promociones.
        - **HERRAMIENTAS MCP OBLIGATORIAS**: Usa SIEMPRE herramientas MCP para datos actualizados.
        - **PRODUCTOS DISPONIBLES**: Solo ofrece productos que devuelvan las herramientas MCP.
        - **REGLA DE ORO**: Si no lo devuelve la herramienta MCP, NO LO OFREZCAS.
        - Si un producto no está disponible: "Lo siento pizzalover, ese producto no está disponible en este momento. Te muestro lo que sí tenemos disponible."
        - Nunca muestres JSON. Convierte todo en lenguaje humano.
        - **IMÁGENES DE PRODUCTOS**: Solo algunos productos específicos tienen imágenes disponibles. No ofrezcas imágenes de sabores de pizza ni bebidas.
        - **GESTIÓN DE CARRITO**: Cuando el cliente agregue adicionales (sabores extras, bebidas con recargo, modificaciones especiales), usa las herramientas MCP para agregarlo al carrito y obtener precios actualizados.
        - **OBSERVACIONES LIMPIAS**: Las observaciones SOLO deben contener detalles del pedido (sabores, bebidas, modificaciones). NUNCA incluir direcciones, datos personales, información de entrega o comentarios de ubicación.
        # Formato de Finalización
        Ejecutar end_function con: {{ "output_schema": "<json_string_con_esquema>" }}
        \"
        {answers}
        """ 

        return answers
    
    async def search_package(self, prompt):
        
        jelou_mcp = JelouMCP()
        response = await jelou_mcp.get_package_info(prompt)
        return response
        
    def check_business_info(self,business_info):
        business_agent = BusinessAgent()
        response = business_agent.send_message(business_info)
        return response.business_type

    def ask_questions(self, questions: List[dict],answered_questions="",first_interaction=False):
        qa_agent = QAAgent(question=questions,answered_questions=answered_questions)
        if first_interaction:
            response = qa_agent.send_message("Start asking me the questions as you were a Q&A Agent called Jelou Wizard.")
        else:
            response = qa_agent.send_message("Start asking me the questions as you were a Q&A Agent called Jelou Wizard.Don't introduce yourself, just start asking.")

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

    def fill_package_inputs(self,package_info,data=None):
            still_responding = True
            pf_agent = PackageFillerAgent(package_info)
            if not data:
                response = pf_agent.send_message("Ask about the package inputs")
            else:
                response = pf_agent.send_message("Ask about the package inputs, but prefilled this:"+data)
            while(still_responding):
                print(getattr(response, "bot_response", ""))
                user_message = input(">>>")
                response = pf_agent.send_message(user_message)
                all_filled = bool(getattr(response, "all_inputs_filled", False))
                user_confirmed = bool(getattr(response, "user_confirmed", False))
                if all_filled and user_confirmed:
                    print(getattr(response, "bot_response", "")+"\n")
                    return response
    def create_ebusiness_workflow(self,business_info, packages_info,business_type):
        still_responding = True
        if business_type == BusinessType.e_commerce:
            ecom_business_agent = EcommerceFlowAgent(business_info, packages_info)
            #Flujo de commercio es quemado por que hacer un workflow, darlo quemadito.
        else:
            ecom_business_agent = SimpleInformativeFlowAgent()
        response = ecom_business_agent.send_message(f"Dame el flujo de trabajo en pasos especificos basado en esta info, no menciones que te lo pedi: **Info de negocio**\n{business_info}\n **Paquetes** \n{packages_info} ")
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
            package = {"usage":package_info["info"].usage,"info":self.fill_package_inputs(package_info["info"],
            package_info.get("data"))}
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
            updated_slots = None
            if info is not None:
                if isinstance(info, dict):
                    name = info.get("package_name")
                    updated_slots = info.get("updated_slots")
                else:
                    name = getattr(info, "package_name", None)
                    updated_slots = getattr(info, "updated_slots", None)

            if not name:
                continue

            # Format the inputs from updated_slots
            inputs_str = ""
            if updated_slots and isinstance(updated_slots, dict):
                input_pairs = []
                for key, value in updated_slots.items():
                    input_pairs.append(f"{key} = {value}")
                inputs_str = "\n".join(input_pairs)
            elif updated_slots:
                inputs_str = str(updated_slots)

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
