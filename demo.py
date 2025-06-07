# gradio_manim_gemini_app.py – **v3**
"""Gradio demo 
============
— third revision —
• **Правильная структура history** — теперь `Chatbot` получает список *пар*
  `(user_text, bot_text)`.  Чанки бота апдей‑тят второй элемент последней пары,
  поэтому «дубли» и «робот‑юзер» исчезают.  
• **Ошибки рендера** публикуются *как пользовательское сообщение* и немедленно
  отправляются в Gemini; модель отвечает, мы снова пытаемся сгенерировать код —
  полностью автоматический цикл, как в вашем CLI‑скрипте.  
• Управление состоянием сведено к чётким этапам: `await_task`, `coding_loop`,
  `await_feedback`, `finished`.
• После каждого рендера пользователь может дать дополнительные указания —
  видео отправляется в Gemini и код генерируется заново с учётом замечаний.

Запуск:
```bash
pip install --upgrade gradio google-genai manim_video_generator
export GEMINI_API_KEY="YOUR_KEY"
python gradio_manim_gemini_app.py
```
"""
from __future__ import annotations

import asyncio
import os
import re
import traceback
from pathlib import Path
from typing import List, Tuple

import gradio as gr
from google import genai
from google.genai.chats import Chat, AsyncChat
from google.genai.types import GenerateContentConfig, ThinkingConfig, UploadFileConfig

from manim_video_generator.video_executor import VideoExecutor  # type: ignore
from prompts import SYSTEM_PROMPT_SCENARIO_GENERATOR, SYSTEM_PROMPT_CODEGEN

# ────────────────────────────────  Config  ─────────────────────────────────────

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY env variable not set.")

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash-preview-05-20"
video_executor = VideoExecutor()

# ───────────────────────  Helpers to work with Chatbot  ─────────────────────────

def add_user_msg(history: List[Tuple[str, str]], text: str):
    """Append new (user, «») pair."""
    history.append((text, ""))


def append_bot_chunk(history: List[Tuple[str, str]], chunk: str):
    """Add chunk to bot part of the last pair."""
    user, bot = history[-1]
    history[-1] = (user, bot + chunk)


class StreamPart:
    def __init__(self, text: str):
        self.text = text

class ThinkingStreamPart(StreamPart): pass
class TextStreamPart(StreamPart): pass


async def stream_parts(chat, prompt):
    cfg = GenerateContentConfig(thinking_config=ThinkingConfig(include_thoughts=True))
    async for chunk in await chat.send_message_stream(prompt, config=cfg):
        if chunk.candidates:
            cand = chunk.candidates[0]
            if cand.content and cand.content.parts:
                for part in cand.content.parts:
                    if part.text:
                        if part.thought:
                            yield ThinkingStreamPart(part.text)
                        else:
                            yield TextStreamPart(part.text)


def extract_python(md: str) -> str:
    m = re.search(r"```python(.*?)```", md, re.S)
    if not m:
        raise ValueError("No ```python``` block found in model output.")
    return m.group(1).strip()


async def coding_cycle(state: "Session", history: List[Tuple[str, str]], prompt):
    """Generate code, render video and return once rendering succeeds."""
    while True:
        async for chunk in stream_parts(state.chat, prompt):
            append_bot_chunk(history, chunk.text)
            yield history, state, state.last_video
            await asyncio.sleep(0)

        full_answer = history[-1][1]
        try:
            py_code = extract_python(full_answer)
        except ValueError as e:
            err_msg = f"Error: {e}. Please wrap the code in ```python``` fence."
            prompt = err_msg
            add_user_msg(history, err_msg)
            yield history, state, state.last_video
            continue

        try:
            video_path = video_executor.execute_manim_code(py_code)
            state.last_video = video_path
        except Exception as e:
            tb = traceback.format_exc(limit=10)
            err_msg = (
                f"Error, your code is not valid: {e}. Traceback: {tb}. Please fix this error and regenerate the code again."
            )
            prompt = err_msg
            add_user_msg(history, err_msg)
            yield history, state, state.last_video
            continue

        append_bot_chunk(history, "\n🎞️ Rendering done! Feel free to request changes or type **finish** to end.")
        state.phase = "await_feedback"
        yield history, state, state.last_video
        return

# ──────────────────────────  Session state  ────────────────────────────────────

class Session(dict):
    phase: str  # await_task | coding_loop | await_feedback | finished
    chat: AsyncChat | None
    last_video: Path | None

    def __init__(self):
        super().__init__(phase="await_task", chat=None, last_video=None)
        self.phase = "await_task"
        self.chat = None
        self.last_video = None

# ────────────────────────  Main chat handler  ──────────────────────────────────

async def chat_handler(user_msg: str, history: List[Tuple[str, str]], state: Session):
    history = history or []

    # 0. Always reflect user input
    add_user_msg(history, user_msg)
    yield history, state, state.last_video

    # bootstrap chat on very first user request
    if state.phase == "await_task":
        if not state.chat:
            # First time - create chat and generate scenario
            state.chat = client.aio.chats.create(model=MODEL)
            scenario_prompt = f"{SYSTEM_PROMPT_SCENARIO_GENERATOR}\n\n{user_msg}"
            async for txt in stream_parts(state.chat, scenario_prompt):
                append_bot_chunk(history, txt.text)
                yield history, state, state.last_video
                await asyncio.sleep(0)
            append_bot_chunk(history, "\n\n*(type **continue** to proceed to code generation)*")
            yield history, state, state.last_video
            return
        else:
            # Chat exists - check if user wants to proceed or modify scenario
            if user_msg.strip().lower() in {"c", "continue", "с"}:
                # User is ready to proceed to code generation
                state.phase = "coding_loop"
            else:
                # User wants to discuss/modify scenario
                async for chunk in stream_parts(state.chat, user_msg):
                    append_bot_chunk(history, chunk.text)
                    yield history, state, state.last_video
                    await asyncio.sleep(0)
                append_bot_chunk(history, "\n\n*(type **continue** when ready to proceed to code generation)*")
                yield history, state, state.last_video
                return

    # later phases require chat obj
    if not state.chat:
        raise ValueError("Chat not found")

    # ── Coding loop ─────────────────────────────────────────────────────────────
    if state.phase == "coding_loop":
        prompt = "Thanks. It is good scenario. Now generate code for it.\n\n" + SYSTEM_PROMPT_CODEGEN
        async for out in coding_cycle(state, history, prompt):
            yield out
        return
    # ── Awaiting user feedback after rendering ────────────────────────────────
    if state.phase == "await_feedback":
        if user_msg.strip().lower() in {"finish", "done", "f"}:
            state.phase = "finished"
            append_bot_chunk(history, "Session complete. Refresh page to start over.")
            yield history, state, state.last_video
            return
        file_ref = client.files.upload(file=state.last_video, config=UploadFileConfig(display_name=state.last_video.name))
        while file_ref.state and file_ref.state.name == "PROCESSING":
            await asyncio.sleep(3)
            if file_ref.name:
                file_ref = client.files.get(name=file_ref.name)
        if file_ref.state and file_ref.state.name == "FAILED":
            raise RuntimeError("Gemini failed to process upload")
        prompt = [file_ref, f"{user_msg}\n\n{SYSTEM_PROMPT_CODEGEN}"]
        state.phase = "coding_loop"
        async for out in coding_cycle(state, history, prompt):
            yield out
        return

    # ── Finished phase ──────────────────────────────────────────────────────────
    if state.phase == "finished":
        append_bot_chunk(history, "Session complete. Refresh page to start over.")
        yield history, state, state.last_video

# ───────────────────────────────  UI  ──────────────────────────────────────────

def build_app():
    with gr.Blocks(title="Gemini‑Manim Video Creator") as demo:
        gr.Markdown("# 🎬 Gemini‑Manim Video Creator\nCreate an explanatory animation from a single prompt.")

        history = gr.Chatbot(height=850)
        session = gr.State(Session())

        with gr.Row():
            txt = gr.Textbox(placeholder="Describe the concept…", scale=4)
            btn = gr.Button("Send", variant="primary")

        vid = gr.Video(label="Rendered video", interactive=False)

        def get_vid(state: Session):
            return state.last_video if state.last_video else None

        btn.click(chat_handler, [txt, history, session], [history, session, vid]) \
           .then(lambda: "", None, txt)

    return demo


if __name__ == "__main__":
    build_app().launch()
