from ai.agents.QA.question_response_structure import QuestionResponseStructure
from config.models.structured_anthropic import StructuredAnthropicChat

class QAAgent(StructuredAnthropicChat):
    def __init__(self, question):
        super().__init__()
        self.add_system_message(f"""You are an ai that will append what the users has being answering about a question., 
        and if the user gives you a answer then respond asking if the info that you saves about what the user has written is correct ,if it is not correct then ask them for corrections,
        if it is correct then say that you will go to the next question.
        **CRITICAL**
        -In user_description don't say "The user told that".
        -Don't write that the user doesn't want to add anything more.
        -Append to user description all the user has said minus that he doesn't want to add anything more.
        -Talk in spanish.
        Question: {question}""")
        self.response_format = QuestionResponseStructure
    
    def get_model_assistant_message(self, model_response):
        return model_response.bot_response