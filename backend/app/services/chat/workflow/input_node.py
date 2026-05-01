from app.services.chat.workflow.graph_state import GraphState
from app.db.oracle_client import db_client
import re

def _get_kws():
    items = db_client.fetch_all("""
        SELECT
            keyword,
            detail_value
        FROM keywords;    
    """)
    return {item['keyword']: item['detail_value'] for item in items}

def expand_abbreviations(query, mapping):
    def replacer(match):
        abbr = match.group(0)
        try:
            return mapping[abbr.lower()]
        except:
            return abbr  # If not found, return the original abbreviation
    
    pattern = r'\b(' + '|'.join(re.escape(k) for k in mapping.keys()) + r')\b'
    new_q = re.sub(pattern, replacer, query, flags=re.IGNORECASE)
    return f"{new_q}"

def input_node(state: GraphState):
    keywords = _get_kws()
    state['question'] = expand_abbreviations(state['question'], keywords)
    state['keywords'] = keywords
    return state