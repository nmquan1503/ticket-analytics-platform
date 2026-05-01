from typing import TypedDict

class GraphState(TypedDict):
    question: str
    # sql_query_raw: str
    sql_query: str
    results: list
    # columns: list
    answer: str
    validated: bool
    retry_count: int
    schema: list
    # distinct_vals: dict
    # current_tokens: int  # Track current token count
    # token_limit_exceeded: bool  # Flag for token limit exceeded
    keywords: dict
    db_description: str
    examples: list
    # session_id: str
    # history_question_sql: str
    # anchor_detection: str
    # current_question_standalone: str
    # previous_question: str
    # history_question: str
    # history_schema: dict
    # history_sql: str
    # history_answer: str
    # user_id: str
    # user_email: str
    # room_id: str
    # rewritten_question: str
    # detail_results: list
    # detail_columns: list
    # is_sc: bool