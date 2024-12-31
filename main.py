
from groq import Groq
from actions import get_response_time
from prompts import system_prompt
from json_helper import extract_json
from dotenv import load_dotenv
import json
import os
load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def generate_text_with_conversation(messages):
    chat_completion = client.chat.completions.create(
        #
        # Required parameters
        #
        messages=messages,

        # The language model which will generate the completion.
        model="llama3-8b-8192",

        #
        # Optional parameters
        #

        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become deterministic
        # and repetitive.
        temperature=0.5,

        # The maximum number of tokens to generate. Requests can use up to
        # 32,768 tokens shared between prompt and completion.
        max_tokens=1024,

        # Controls diversity via nucleus sampling: 0.5 means half of all
        # likelihood-weighted options are considered.
        top_p=1,

        # A stop sequence is a predefined or user-specified text string that
        # signals an AI to stop generating content, ensuring its responses
        # remain focused and concise. Examples include punctuation marks and
        # markers like "[end]".
        stop=None,

        # If set, partial message deltas will be sent.
        stream=False,
    )
    return chat_completion.choices[0].message.content

# available actions
available_actions = {
    "get_response_time": get_response_time,
}
user_prompt = "What is the response time of http://www.google.com?"
messages = [
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": system_prompt
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": user_prompt,
            }
        ]


turn_count = 1;
max_turns = 5;


while turn_count <= max_turns:
    print(f"Loops: {turn_count}")
    print("--------------------------")
    turn_count += 1

    response = generate_text_with_conversation(messages)
    print(response)

    json_response = extract_json(response)
    

    if json_response:
        function_name = json_response[0]['function_name']
        function_params = json_response[0]['function_params']
        if function_name not in available_actions:
            raise Exception(f"Function {function_name} not found in available actions.")
        print(f"-- running {function_name} {function_params}")

        action_function = available_actions[function_name]
        # call the function

        result = action_function(**function_params)
        function_result_message = f"Action_Response: {result}"
        messages.append({"role": "system", "content": function_result_message})
        print(function_result_message)

    else:
        break;