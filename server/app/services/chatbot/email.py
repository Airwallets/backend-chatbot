from app.services.chatbot.chatbot import get_chatbot
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


# Prompt template for summary
summary_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", 
            "You are an expert at summarizing a user's email."
            "Summarize the email into a 4-line short and comprehensive \
                summary and place them into the field: "
            "- summary: the summary of the email"
        ),
        ("human", "{text}"),
    ]
)

class Summary(BaseModel):
  summary: str

def get_ai_summary(message: str):
  model = get_chatbot()
  prompt = summary_prompt_template.invoke({"text": message})
  # Structured output
  structured_llm = model.with_structured_output(schema=Summary)
  result = structured_llm.invoke(prompt)
  return result

# Prompt template for draft
draft_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", 
            "You are an expert at writing email to response to customer Q&A as \
                the head of customer assistance for team AirWallets in the \
                2025 Feit Hackathon, tackling the company Smec AI's problem statement: \
                automate or streamline a common repetitive task (e.g., invoicing, scheduling, customer inquiries) to help business \
                owners save time and focus on growth. Do not use any template in the email.\
                If the question involves anything outside of your knowledge, reply with \
                'I don't know'. Do not make things up. "
            "Read the email, draft the response email, and place the response email's \
                subject and body: "
            "- draft_subject: the title of the response email"
            "- draft_body: the body of the response email"
        ),
        ("human", "{text}"),
    ]
)

class Draft(BaseModel):
  draft_subject: str
  draft_body: str

def get_ai_draft(message: str) -> Draft:
  model = get_chatbot()
  prompt = draft_prompt_template.invoke({"text": message})
  # Structured output
  structured_llm = model.with_structured_output(schema=Draft)
  result = structured_llm.invoke(prompt)
  return result