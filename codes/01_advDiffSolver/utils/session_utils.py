import streamlit as st


def init_session_state():
    defaults = {
        'program1_code': '', 
        'program1_filename': '', 
        'program1_language': '',
        'program2_code': '', 
        'program2_filename': '', 
        'program2_language': '',
        'config_content': '', 
        'config_filename': '', 
        'benchmark_results': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
