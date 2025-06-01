import asyncio
import time
from google import genai
import os
from dotenv import load_dotenv
from google.genai.chats import Chat
from manim_video_generator.video_executor import VideoExecutor
from prompts import SYSTEM_PROMPT_SCENARIO_GENERATOR, SYSTEM_PROMPT_CODEGEN, REVIEW_PROMPT
from google.genai.types import (
    GenerateContentResponse,
    ThinkingConfig,
    GenerateContentConfig,
    UploadFileConfig,
)
from pathlib import Path
import traceback

load_dotenv()



async def main():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    video_executor = VideoExecutor()

    chat: Chat = client.chats.create(model="gemini-2.5-flash-preview-05-20")

    user_task = input("Enter your task: ")
    assert (
        len(user_task) > 0 and len(user_task) < 10000
    ), "Task must be between 1 and 10000 characters"

    user_input = SYSTEM_PROMPT_SCENARIO_GENERATOR + "\n\n" + user_task
    # Generate scenario
    for iter in range(1000):
        answer = ""
        chunk: GenerateContentResponse
        for chunk in chat.send_message_stream(
            user_input,
            config=GenerateContentConfig(
                thinking_config=ThinkingConfig(
                    include_thoughts=True,
                ),
            ),
        ):
            print()
            if chunk.candidates:
                candidate = chunk.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.thought:
                            print('💭: ', part.text, end="", flush=True)
                        elif part.text:
                            print(part.text, end="", flush=True)
                            answer += part.text
        user_input = input("Answer answer to scenario manager or continue (c)?")
        if user_input.lower() in ("c", "continue", 'с'):
            print("Scenario created")
            scenario = answer
            break
    
    # Generate code
    user_input = "Thanks. It is good scenario. Now generate code for it.\n\n" + SYSTEM_PROMPT_CODEGEN 
    print('Generating code...')
    for iter in range(1000):
        answer = ""
        chunk: GenerateContentResponse
        for chunk in chat.send_message_stream(
            user_input,
            config=GenerateContentConfig(
                thinking_config=ThinkingConfig(
                    include_thoughts=True,
                ),
            ),
        ):
            print()
            if chunk.candidates:
                candidate = chunk.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.thought:
                            print('💭: ', part.text, end="", flush=True)
                        elif part.text:
                            print(part.text, end="", flush=True)
                            answer += part.text
        try:
            code = answer.split("```python")[1].split("```")[0]
        except Exception as e:
            print(f"Error: {e}")
            user_input = f"Error, your answer is not valid formated manim code."
            continue

        
        try:
            video_path: Path = video_executor.execute_manim_code(code)
            print(f"Video generated at {video_path}")
        except Exception as e:
            print(f"Error: {e}")
            traceback_str = traceback.format_exc()
            user_input = f"Error, your code is not valid: {e}. Please fix it. Traceback: {traceback_str}"
            continue
        
        myfile = client.files.upload(file=video_path.absolute(),
                                    config=UploadFileConfig(
                                        display_name=video_path.name
                                    ))
        assert myfile.name, "File name is not set"
        assert myfile.state, "File state is not set"
        
        print('Uploading video file to google genai...')
        while myfile.state.name == "PROCESSING":
            print('.', end='', flush=True)
            time.sleep(10)
            myfile = client.files.get(name=myfile.name)
        print(f"File uploaded at {myfile.name}")

        if myfile.state.name == "FAILED":
            raise ValueError(myfile.state.name)
        
        print(f"File uploaded at {myfile.name}")



        for chunk in chat.send_message_stream(
            [myfile, REVIEW_PROMPT],
            config=GenerateContentConfig(
                thinking_config=ThinkingConfig(
                    include_thoughts=True,
                ),
            ),
        ):
            if chunk.candidates:
                candidate = chunk.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.text:
                            if part.thought:
                                print('💭: ', part.text, end="", flush=True)
                            else:
                                print(part.text, end="", flush=True)
                                answer += part.text
        if "no issues found" in answer.lower():
            print("No issues found")
            break
        else:
            print("Issues found")
            user_prompt = input("Prompt for fixing issues (or n to exit): ")
            if user_prompt.lower() == 'n':
                break
            else:
                user_input = f"Fix this problems please."
                if user_prompt.strip():
                    user_input += f" TIP: {user_prompt}"
        

if __name__ == "__main__":
    asyncio.run(main())
