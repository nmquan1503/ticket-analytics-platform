from langgraph.graph import END, StateGraph
from typing import TypedDict
from app.db.oracle_client import OracleClient
from app.services.chat.workflow.input_node import input_node
from app.services.chat.workflow.gen_res import gen_res
from app.services.chat.workflow.gen_sql import gen_sql
from app.services.chat.workflow.retrieve_tables_columns import retrieve_tables_and_columns
from app.services.chat.workflow.validate import validate_sql
from app.services.chat.workflow.graph_state import GraphState

def build_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("input_node", input_node)
    workflow.add_node("retrieve_tables_and_columns", retrieve_tables_and_columns)
    workflow.add_node("gen_sql", gen_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("gen_res", gen_res)

    workflow.set_entry_point('input_node')
    workflow.add_edge('input_node', 'retrieve_tables_and_columns')
    workflow.add_edge('retrieve_tables_and_columns', 'gen_sql')
    workflow.add_edge('gen_sql', 'validate_sql')
    workflow.add_edge('validate_sql', 'gen_res')
    workflow.add_edge("gen_res", END)

    return workflow.compile()

if __name__ == "__main__":
    wf = build_workflow()
    result = wf.invoke({"question": "Liệt kê danh sách 10 thiết bị có downtime <= 100 trong hôm qua"})
    print(result["answer"])


    