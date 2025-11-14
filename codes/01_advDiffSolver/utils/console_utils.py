import sys
import re

def safe_print(text, file=None):
    if file is None:
        file = sys.stdout
    
    try:
        print(text, file=file)
    except (UnicodeEncodeError, UnicodeError):
        # Remove emojis and problematic Unicode characters
        # Emoji range: U+1F300 to U+1F9FF (plus some other ranges)
        text_no_emoji = re.sub(
            r'[\U0001F300-\U0001F9FF'  # Emoticons
            r'\U0001F600-\U0001F64F'   # Emoticons 2
            r'\U0001F680-\U0001F6FF'   # Transport & Map Symbols
            r'\U0001F1E0-\U0001F1FF'   # Flags
            r'\U00002700-\U000027BF'   # Dingbats
            r'\U0000FE00-\U0000FE0F'   # Variation Selectors
            r'\U00002600-\U000026FF'   # Miscellaneous Symbols
            r']+', 
            '', 
            text
        )
        print(text_no_emoji.strip(), file=file)


def configure_windows_console():
    try:
        import io
        # Reconfigure stdout and stderr to use UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        return True
    except Exception as e:
        # If reconfiguration fails, safe_print will handle it
        return False
