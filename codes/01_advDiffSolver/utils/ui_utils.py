import os
import streamlit as st

def load_custom_css():
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
    
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_language_emoji(language):
    emoji_map = {
        "python": "🐍",
        "cpp": "⚙️",
        "julia": "🔬"
    }
    
    return emoji_map.get(language, "📄")


def get_language_display_name(language):
    display_map = {
        "python": "python",
        "cpp": "cpp",
        "julia": "julia"
    }
    
    return display_map.get(language, "text")
