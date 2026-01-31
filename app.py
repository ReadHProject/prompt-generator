import streamlit as st
import os
import json
import requests
from typing import Dict, List

# ===========================
# CONFIGURATION
# ===========================

# Set your API keys in Streamlit's secrets or environment variables
# Example: 
#   ANTHROPIC_API_KEY = "your_key_here"
#   OPENAI_API_KEY = "your_key_here"
#   DEEPSEEK_API_KEY = "your_key_here"

# You can get these from:
# - Anthropic (Claude): https://console.anthropic.com/
# - OpenAI (GPT-4o): https://platform.openai.com/api-keys
# - DeepSeek: https://api.deepseek.com/ (free tier available)

# ===========================
# AI API CLIENTS
# ===========================

def call_claude(prompt: str) -> str:
    """Call Anthropic Claude 3.5 Sonnet API."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": st.secrets["ANTHROPIC_API_KEY"],
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

def call_gpt4o(prompt: str) -> str:
    """Call OpenAI GPT-4o API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_deepseek(prompt: str) -> str:
    """Call DeepSeek V3 API (free tier)."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['DEEPSEEK_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ===========================
# META-PROMPT TEMPLATE
# ===========================

META_PROMPT_TEMPLATE = """
You are an Expert AI Prompt Engineer specializing in generating highly effective prompts for coding and development tasks.

Your task is to create a detailed, structured prompt that I can use with any AI model to solve the following problem:

**PROJECT IDEA:**
{project_idea}

**REQUIREMENTS:**
{requirements}

Please follow this exact structure for the output prompt:

---
**Role:** [Describe the expert role, e.g., "Senior Full-Stack Developer with 10+ years of experience in React and Node.js"]
**Context:** [Briefly explain the project, tech stack, and constraints]
**Task Instructions:** 
1. [Step 1]
2. [Step 2]
...
**Constraints:**
- Must include [specific requirement 1]
- Must avoid [specific restriction 1]
...
**Output Format:**
- Provide complete, runnable code blocks.
- Include error handling.
- Add comments explaining key sections.
- Do NOT use placeholders like "// ...".
---
"""

# ===========================
# STREAM LIT UI
# ===========================

st.set_page_config(page_title="🚀 AI Prompt Generator", layout="wide")

st.title("🚀 **AI Prompt Generator for Coding**")
st.markdown("""
Generate **highly accurate, structured prompts** optimized for coding tasks.  
Choose an AI model, describe your task, and get a ready-to-use prompt!
""")

# --- Sidebar: Model Selection ---
st.sidebar.header("🧠 Select AI Model")
model = st.sidebar.selectbox(
    "Choose the AI model to generate your prompt:",
    ["Claude 3.5 Sonnet (Best for Logic)", 
     "GPT-4o (Best for Creativity)", 
     "DeepSeek V3 (Best for Syntax)"]
)

# --- Main Input ---
st.header("📝 Describe Your Coding Task")
project_idea = st.text_area(
    "Enter your project idea or coding task:",
    placeholder="Example: Build a REST API with Flask that connects to PostgreSQL...",
    height=100
)

requirements = st.text_area(
    "Additional requirements (optional):",
    placeholder="Example: Use SQLAlchemy, include JWT authentication, return JSON responses...",
    height=80
)

# --- Generate Button ---
if st.button("🔮 Generate Prompt"):
    if not project_idea:
        st.error("Please enter a project idea.")
    else:
        with st.spinner("Crafting your perfect prompt..."):
            # Build the meta-prompt
            meta_prompt = META_PROMPT_TEMPLATE.format(
                project_idea=project_idea,
                requirements=requirements if requirements else "No extra requirements."
            )
            
            # Call the selected AI
            if "Claude" in model:
                try:
                    result = call_claude(meta_prompt)
                except Exception as e:
                    st.error(f"Error with Claude API: {e}")
                    st.stop()
            elif "GPT" in model:
                try:
                    result = call_gpt4o(meta_prompt)
                except Exception as e:
                    st.error(f"Error with GPT-4o API: {e}")
                    st.stop()
            else:  # DeepSeek
                try:
                    result = call_deepseek(meta_prompt)
                except Exception as e:
                    st.error(f"Error with DeepSeek API: {e}")
                    st.stop()
            
            # Display the generated prompt
            st.header("✅ Generated Prompt")
            st.code(result, language="markdown")
            
            # Copy-to-clipboard button (using Streamlit's built-in)
            st.download_button(
                label="📋 Copy Prompt to Clipboard",
                data=result,
                file_name="ai_prompt.md",
                mime="text/markdown"
            )

# --- Comparison Mode ---
st.header("🆚 Compare Multiple Models")
compare = st.checkbox("Enable comparison mode (generates prompts from all models)")

if compare and project_idea:
    with st.spinner("Comparing models..."):
        cols = st.columns(3)
        
        try:
            # Claude
            with cols[0]:
                st.subheader("Claude 3.5 Sonnet")
                claude_result = call_claude(META_PROMPT_TEMPLATE.format(
                    project_idea=project_idea,
                    requirements=requirements
                ))
                st.code(claude_result, language="markdown")
                st.download_button(
                    "Download",
                    data=claude_result,
                    file_name="claude_prompt.md",
                    key="claude_dl"
                )
        except Exception as e:
            cols[0].error(f"Claude Error: {e}")
        
        try:
            # GPT-4o
            with cols[1]:
                st.subheader("GPT-4o")
                gpt_result = call_gpt4o(META_PROMPT_TEMPLATE.format(
                    project_idea=project_idea,
                    requirements=requirements
                ))
                st.code(gpt_result, language="markdown")
                st.download_button(
                    "Download",
                    data=gpt_result,
                    file_name="gpt_prompt.md",
                    key="gpt_dl"
                )
        except Exception as e:
            cols[1].error(f"GPT-4o Error: {e}")
        
        try:
            # DeepSeek
            with cols[2]:
                st.subheader("DeepSeek V3")
                deepseek_result = call_deepseek(META_PROMPT_TEMPLATE.format(
                    project_idea=project_idea,
                    requirements=requirements
                ))
                st.code(deepseek_result, language="markdown")
                st.download_button(
                    "Download",
                    data=deepseek_result,
                    file_name="deepseek_prompt.md",
                    key="deepseek_dl"
                )
        except Exception as e:
            cols[2].error(f"DeepSeek Error: {e}")