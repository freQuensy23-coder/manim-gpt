---
title: Manim GPT - AI Video Creator
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.0.0"
app_file: demo.py
pinned: false
license: mit
---

# 🎬 Manim GPT - AI Video Creator

Create beautiful explanatory animations from simple text prompts using AI and Manim!

## Features

- 🤖 **AI-Powered**: Uses Gemini AI to generate Manim code from natural language
- 🎥 **Automatic Rendering**: Creates high-quality MP4 videos 
- 🎵 **Background Music**: Automatically adds background music to all videos
- 🔄 **Auto-Fix**: AI reviews and fixes rendering errors automatically
- ⚡ **Fast**: Medium quality rendering for quick results

## How to Use

1. Describe the concept you want to visualize (e.g. "Explain how neural networks work")
2. Click "Send" to start the generation process
3. The AI will create a scenario and generate Manim code
4. Type "continue" when prompted to proceed with code generation
5. Wait for the video to render with background music
6. Download your animated explanation!

## Technical Details

- **AI Model**: Gemini 2.5 Flash Preview
- **Animation Engine**: Manim Community Edition
- **Video Processing**: MoviePy for audio mixing
- **Background Music**: Automatically loops/trims to match video duration

## Requirements

Set your Gemini API key as an environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"
``` 