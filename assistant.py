import re
import json
import time
import datetime as dt
from openai import OpenAI

from settings import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY,)


def character_count_by_sec(text):
    """
    :param text: raw text with the following format:
        <start_time> --> <end_time>
        <subtitle>
        Example:
            00:01:36:05 --> 00:01:37:22
            hacen de la política.
    :return: int => characters per second (cps)
    """
    def compute_time_diff_in_seconds():
        start_time, end_time = time_line.split("-->")
        start_time = dt.datetime.strptime(f'{start_time.strip()}', "%H:%M:%S.%f")
        end_time = dt.datetime.strptime(f'{end_time.strip()}', "%H:%M:%S.%f")
        num_seconds = round((end_time - start_time).total_seconds())
        return num_seconds

    new_blocs = []
    break_blocs = re.split(r"(?:\r?\n){2,}", text.strip())
    for bloc in break_blocs:
        bloc_lines = bloc.split('\n')
        time_line = bloc_lines[0]
        subtitle = ''.join(bloc_lines[1:])
        subtitle_time_elapsed = compute_time_diff_in_seconds()
        subtitle_num_chars = len(subtitle.replace(" ", "").strip())
        cps = subtitle_num_chars/max(subtitle_time_elapsed, 1)
        new_blocs.append(f"{bloc}\ncps: {cps}\nchars: {subtitle_num_chars}")

    return '\n'.join(new_blocs)


TOOLS_LIST = [{
    "type": "function",
    "function": {
        "name": "character_count_by_sec",
        "description": "Cuenta el número de caracteres por segundo dado el tiempo de inicio y de fin junto con el texto",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto con múltiples subtitulos como bloques de tiempo de inicio y fin junto con el subtítulo"
                }
            },
            "required": ["text"]
        }
    }
}]


class AssistantManager:

    assistant_id = "asst_b5ERhgOkfItwM48e74foQwXO"
    thread_id = None

    def __init__(self, model: str = "gpt-3.5-turbo-1106"):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.responses = []

        # Retrieve existing assistants and thread if IDs are already
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )

        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    # @retry(max_retries=2)
    def run_assistant(self):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            if self.run.status in ('cancelled', 'cancelling', 'failed'):
                raise Exception(f"FAILED EXECUTION::: {self.run.status}")

    def submit_and_run_task_to_thread(self, role, prompt):
        self.add_message_to_thread(
            role=role,
            content=prompt
        )
        self.run_assistant()

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order="asc"
            )

            last_message = messages.data[-1]
            # role = last_message.role
            response = last_message.content[0].text.value
            self.responses.append(response)
            # summary.append(response)
            # self.response = "\n".join(summary)
            # print(f"SUMMARY ----> {role.capitalize()}: ==> {response}")

    def call_required_functions(self, required_actions):
        if not self.run:
            return

        tools_ouputs = []
        for action in required_actions["tool_calls"]:
            func_name = action['function']["name"]
            arguments = json.loads(action['function']["arguments"])

            if func_name == "character_count_by_sec":
                output = character_count_by_sec(text=arguments["text"])
                # print(f"Text words: {output}")

                tools_ouputs.append({
                    "tool_call_id": action["id"],
                    "output": str(output)
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tools_ouputs
        )

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )
                # print(f"RUN STATUS::: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

                elif run_status.status in ('cancelled', 'cancelling', 'failed'):
                    print("Assitant execution failed")
                    # raise Exception(f"FAILED EXECUTION::: {run_status.status}")

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        print(f"RUN STEPS::: {run_steps}")
