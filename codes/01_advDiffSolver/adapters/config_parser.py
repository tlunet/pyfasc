"""
Config Parser for Language-Specific Compiler Options
"""


def parse_compiler_config(file_path: str) -> dict:
    """Parse compiler config from config.txt"""
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line and not line[0].isdigit() and not line.startswith('#'):
                    lang, flags = line.split(':', 1)
                    config[lang.strip().lower()] = flags.strip()
    except Exception:
        pass
    return config
