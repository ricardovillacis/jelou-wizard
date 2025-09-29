from ai.agents.QA.question_response_structure import QuestionResponseStructure
from config.models.structured_anthropic import StructuredAnthropicChat

class QAAgent(StructuredAnthropicChat):
    def __init__(self, question):
        super().__init__()
        self.add_system_message(f"""You are an ai that will append what the users has being answering about a questions.After all questions have been answered ask if
        the given information is correct and then if not modify the information, if it is correct then tell that the info is correct and consider the process finished.
        **CRITICAL**
        -Ask each question at a time, one by one.
        -In user_description don't say "The user told that".
        -Don't write that the user doesn't want to add anything more.
        -Append to user description all the user has said minus that he doesn't want to add anything more.
        -Talk in spanish.
        Questions: {question}""")
        self.response_format = QuestionResponseStructure
    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response