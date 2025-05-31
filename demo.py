# gradio_manim_gemini_app.py – **v3**
"""Gradio demo 
============
— third revision —
• **Правильная структура history** — теперь `Chatbot` получает список *пар*
  `(user_text, bot_text)`.  Чанки бота апдей‑тят второй элемент последней пары,
  поэтому «дубли» и «робот‑юзер» исчезают.  
• **Ошибки рендера** публикуются *как пользовательское сообщение* и немедленно
  отправляются в Gemini; модель отвечает, мы снова пытаемся сгенерировать код —
  полностью автоматический цикл, как в вашем CLI‑скрипте.  
• Управление состоянием сведено к чётким этапам: `await_task`, `coding_loop`,
  `review_loop`, `finished`.

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
from google.genai.types import GenerateContentConfig, ThinkingConfig, UploadFileConfig

from manim_video_generator.video_executor import VideoExecutor  # type: ignore
from prompts import SYSTEM_PROMPT_SCENARIO_GENERATOR, SYSTEM_PROMPT_CODEGEN, REVIEW_PROMPT

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


def stream_parts(chat: genai.Chat, prompt):
    cfg = GenerateContentConfig(thinking_config=ThinkingConfig(include_thoughts=True))
    for chunk in chat.send_message_stream(prompt, config=cfg):
        if chunk.candidates:
            cand = chunk.candidates[0]
            if cand.content and cand.content.parts:
                for part in cand.content.parts:
                    if part.text:
                        yield part.text


def extract_python(md: str) -> str:
    m = re.search(r"```python(.*?)```", md, re.S)
    if not m:
        raise ValueError("No ```python``` block found in model output.")
    return m.group(1).strip()

# ──────────────────────────  Session state  ────────────────────────────────────

class Session(dict):
    phase: str  # await_task | coding_loop | review_loop | finished
    chat: genai.Chat | None
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
    yield history, state

    # bootstrap chat on very first user request
    if state.phase == "await_task":
        state.chat = client.chats.create(model=MODEL)
        # ── Scenario generation ────────────────────────────────────────────────
        scenario_prompt = f"{SYSTEM_PROMPT_SCENARIO_GENERATOR}\n\n{user_msg}"
        for txt in stream_parts(state.chat, scenario_prompt):
            append_bot_chunk(history, txt)
            yield history, state
            await asyncio.sleep(0)

        append_bot_chunk(history, "\n\n*(type **continue** to proceed)*")
        state.phase = "coding_loop"
        yield history, state
        return

    # later phases require chat obj
    if not state.chat:
        append_bot_chunk(history, "⚠️ Internal error: lost chat session.")
        yield history, state
        return

    # ── Coding loop ─────────────────────────────────────────────────────────────
    if state.phase == "coding_loop":
        if user_msg.strip().lower() not in {"c", "continue", "с"}:
            append_bot_chunk(history, "⚠️ Type **continue** to move on.")
            yield history, state
            return

        while True:  # keep cycling until render succeeds
            # 1. Ask for code
            code_prompt = (
                "Thanks. It is good scenario. Now generate code for it.\n\n" + SYSTEM_PROMPT_CODEGEN
            )
            add_user_msg(history, "# system → generate code")
            for chunk in stream_parts(state.chat, code_prompt):
                append_bot_chunk(history, chunk)
                yield history, state
                await asyncio.sleep(0)

            full_answer = history[-1][1]
            try:
                py_code = extract_python(full_answer)
            except ValueError as e:
                # send formatting error to model, loop again
                err_msg = f"Error: {e}. Please wrap the code in ```python``` fence."
                add_user_msg(history, err_msg)
                yield history, state
                continue  # restart loop

            # 2. Render
            try:
                video_path = video_executor.execute_manim_code(py_code)
                state.last_video = video_path
            except Exception as e:
                tb = traceback.format_exc(limit=10)
                err_msg = f"Error, your code is not valid: {e}. Traceback: {tb}"
                add_user_msg(history, err_msg)  # error == user message
                yield history, state
                continue  # Gemini will answer with a fix

            append_bot_chunk(history, "\n🎞️ Rendering done, uploading for review…")
            yield history, state

            # 3. Upload
            try:
                file_ref = client.files.upload(
                    file=video_path, config=UploadFileConfig(display_name=video_path.name)
                )
                while file_ref.state.name == "PROCESSING":
                    await asyncio.sleep(3)
                    file_ref = client.files.get(name=file_ref.name)
                if file_ref.state.name == "FAILED":
                    raise RuntimeError("Gemini failed to process upload")
            except Exception as up_err:
                err_msg = f"Upload error: {up_err}"
                add_user_msg(history, err_msg)
                yield history, state
                continue  # ask Gemini to fix

            # 4. Review
            review_prompt = [file_ref, REVIEW_PROMPT]
            add_user_msg(history, "# system → review video")
            for chunk in stream_parts(state.chat, review_prompt):
                append_bot_chunk(history, chunk)
                yield history, state
                await asyncio.sleep(0)

            if "no issues found" in history[-1][1].lower():
                append_bot_chunk(history, "\n✅ Video accepted! 🎉")
                state.phase = "finished"
                yield history, state
                return
            else:
                append_bot_chunk(history, "\n🔄 Issues found. Trying again…")
                # let the loop run again (Gemini will generate corrected code)
                continue

    # ── Finished phase ──────────────────────────────────────────────────────────
    if state.phase == "finished":
        append_bot_chunk(history, "Session complete. Refresh page to start over.")
        yield history, state

# ───────────────────────────────  UI  ──────────────────────────────────────────

def build_app():
    with gr.Blocks(title="Gemini‑Manim Video Creator") as demo:
        gr.Markdown("# 🎬 Gemini‑Manim Video Creator\nCreate an explanatory animation from a single prompt.")

        history = gr.Chatbot()
        session = gr.State(Session())

        with gr.Row():
            txt = gr.Textbox(placeholder="Describe the concept…", scale=4)
            btn = gr.Button("Send", variant="primary")

        vid = gr.Video(label="Rendered video", interactive=False)

        def get_vid(state: Session):
            return state.last_video if state.last_video else None

        btn.click(chat_handler, [txt, history, session], [history, session]) \
           .then(lambda: "", None, txt)

        session.change(get_vid, session, vid)

    return demo


if __name__ == "__main__":
    build_app().launch()
