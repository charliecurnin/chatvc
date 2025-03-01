import os
import time

from openai import OpenAI
import reflex as rx

OPENAI_ASSISTANT_ID = "asst_DKJRMWO9yngdaMJCmXpZ23EL"

client = OpenAI(
	api_key=os.environ["OPENAI_API_KEY"],
	organization=os.environ["OPENAI_ORG_KEY"]
)
thread = client.beta.threads.create()

class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS = {
    "Intros": [],
}


class State(rx.State):
    """The app state."""

    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    # Whether the drawer is open.
    drawer_open: bool = False

    # Whether the modal is open.
    modal_open: bool = False

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

        # Toggle the modal.
        self.modal_open = False

    def toggle_modal(self):
        """Toggle the new chat modal."""
        self.modal_open = not self.modal_open

    def toggle_drawer(self):
        """Toggle the drawer."""
        self.drawer_open = not self.drawer_open

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]
        self.toggle_drawer()

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name
        self.toggle_drawer()

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    async def process_question(self, form_data: dict[str, str]):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """
        # Check if the question is empty
        if self.question == "":
            return

        # Add the question to the list of questions.
        qa = QA(question=self.question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        self.question = ""
        yield

        # Build the messages.
        qa = self.chats[self.current_chat][-1]
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=qa.question,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=OPENAI_ASSISTANT_ID
        )

        while run.status != "completed":
            time.sleep(0.1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        messages = client.beta.threads.messages.list(thread.id)
        message = messages.data[0]
        answer_text = message.content[0].text.value
        self.chats[self.current_chat][-1].answer += answer_text
        self.chats = self.chats

        # Toggle the processing flag.
        self.processing = False
