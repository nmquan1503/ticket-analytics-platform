from app.services.chat.workflow.graph_state import GraphState
from app.db.oracle_client import db_client
from app.services.chat.bot import get_embedding

def _get_db_description():
    return db_client.fetch_one("""
        SELECT comments
        FROM user_tab_comments
        WHERE table_name = 'KEYWORDS';
    """)["comments"]

def _find_columns_by_values(query, limit=10, threshold=0.5, limit_val=10):
    sql = """
    WITH scored_values AS (
        SELECT
            table_name,
            column_name,
            value_text,
            UTL_MATCH.JARO_WINKLER_SIMILARITY(
                LOWER(value_text),
                LOWER(:query)
            ) AS value_score
        FROM unique_value_columns
    ),

    filtered_values AS (
        SELECT *
        FROM scored_values
        WHERE value_score >= :threshold_score
    ),

    column_scores AS (
        SELECT
            table_name,
            column_name,
            MAX(value_score) AS score
        FROM filtered_values
        GROUP BY table_name, column_name
    ),

    top_columns AS (
        SELECT *
        FROM (
            SELECT *
            FROM column_scores
            ORDER BY score DESC
        )
        WHERE ROWNUM <= :limit_val
    )

    SELECT
        tc.table_name,
        tc.column_name,
        tc.score,
        rv.value_text,
        rv.value_score,
        tcom.comments AS table_comment,
        ccom.comments AS column_comment

    FROM top_columns tc

    JOIN scored_values rv
      ON tc.table_name = rv.table_name
     AND tc.column_name = rv.column_name

    LEFT JOIN user_tab_comments tcom
      ON tc.table_name = tcom.table_name

    LEFT JOIN user_col_comments ccom
      ON tc.table_name = ccom.table_name
     AND tc.column_name = ccom.column_name

    ORDER BY tc.score DESC, rv.value_score DESC
    """

    try:
        rows = db_client.fetch_all(sql, params={
            "query": query,
            "threshold_score": int(threshold * 100),
            "limit_val": limit_val
        })
    except Exception as e:
        print("===== SQL ERROR =====")
        print(str(e))
        print("=====================")
        print("===== SQL =====")
        print(sql)
        print("=================")
        raise

    result = []
    table_map = {}

    for r in rows:
        tkey = r["table_name"]
        ckey = (r["table_name"], r["column_name"])

        if tkey not in table_map:
            table_map[tkey] = {
                "table_name": r["table_name"],
                "table_comment": r.get("table_comment"),
                "columns": [],
                "_col_map": {}
            }

        table_item = table_map[tkey]

        if ckey not in table_item["_col_map"]:
            col_item = {
                "column_name": r["column_name"],
                "column_comment": r.get("column_comment"),
                "values": []
            }
            table_item["_col_map"][ckey] = col_item
            table_item["columns"].append(col_item)

        table_item["_col_map"][ckey]["values"].append({
            "value": r["value_text"],
            "score": r["value_score"]
        })

    for t in table_map.values():
        t.pop("_col_map", None)
        result.append(t)

    return result

def _find_ex(query_emb, limit=2, threshold=0.5):
    distance_threshold = 1 - threshold

    rows = db_client.fetch_all("""
        SELECT question, answer
        FROM (
            SELECT
                question,
                answer,
                VECTOR_DISTANCE(emb, :query_emb, COSINE) AS distance
            FROM examples
        )
        WHERE distance <= :distance_threshold
        ORDER BY distance ASC
        FETCH FIRST :limit ROWS ONLY
    """, {
        "query_emb": query_emb,
        "distance_threshold": distance_threshold,
        "limit": limit
    })

    return [
        {
            "question": r["question"],
            "answer": r["answer"]
        }
        for r in rows
    ]

def _find_tables(query_emb, limit=5, threshold=0.5):
    distance_threshold = 1 - threshold

    rows = db_client.fetch_all("""
        SELECT
            t.table_name,
            tc.comments AS table_comment
        FROM (
            SELECT
                table_name,
                VECTOR_DISTANCE(emb, :query_emb, COSINE) AS distance
            FROM table_embeddings
        ) t
        LEFT JOIN user_tab_comments tc
          ON t.table_name = tc.table_name
        WHERE t.distance <= :distance_threshold
        ORDER BY t.distance ASC
        FETCH FIRST :limit ROWS ONLY
    """, {
        "query_emb": query_emb,
        "distance_threshold": distance_threshold,
        "limit": limit
    })

    return [
        {
            "table_name": r["table_name"],
            "table_comment": r.get("table_comment"),
            "columns": []
        }
        for r in rows
    ]

def _find_columns(query_emb, limit=20, threshold=0.5):
    distance_threshold = 1 - threshold

    rows = db_client.fetch_all("""
        WITH scored AS (
            SELECT
                table_name,
                column_name,
                VECTOR_DISTANCE(emb, :query_emb, COSINE) AS distance
            FROM column_embeddings
        ),
        filtered AS (
            SELECT *
            FROM scored
            WHERE distance <= :distance_threshold
        ),
        top_cols AS (
            SELECT
                table_name,
                column_name
            FROM filtered
            ORDER BY distance ASC
            FETCH FIRST :limit ROWS ONLY
        )
        SELECT
            c.table_name,
            tc.comments AS table_comment,
            c.column_name,
            cc.comments AS column_comment
        FROM top_cols c
        LEFT JOIN user_tab_comments tc
          ON c.table_name = tc.table_name
        LEFT JOIN user_col_comments cc
          ON c.table_name = cc.table_name
         AND c.column_name = cc.column_name
        ORDER BY c.table_name
    """, {
        "query_emb": query_emb,
        "distance_threshold": distance_threshold,
        "limit": limit
    })

    # ===== group theo table =====
    result = []
    table_map = {}

    for r in rows:
        tkey = r["table_name"]

        if tkey not in table_map:
            table_map[tkey] = {
                "table_name": r["table_name"],
                "table_comment": r.get("table_comment"),
                "columns": []
            }

        table_map[tkey]["columns"].append({
            "column_name": r["column_name"],
            "column_comment": r.get("column_comment"),
            "values": []
        })

    return list(table_map.values())

def _merge(schema, schema_new):
    table_map = {}

    def upsert_table(t):
        tname = t["table_name"]

        if tname not in table_map:
            table_map[tname] = {
                "table_name": tname,
                "table_comment": t.get("table_comment"),
                "columns": [],
                "_col_map": {}
            }

        table_item = table_map[tname]

        # update table_comment nếu schema_new có
        if t.get("table_comment"):
            table_item["table_comment"] = t["table_comment"]

        # xử lý columns
        for col in t.get("columns", []):
            cname = col["column_name"]

            if cname not in table_item["_col_map"]:
                col_item = {
                    "column_name": cname,
                    "column_comment": col.get("column_comment"),
                    "values": []
                }
                table_item["_col_map"][cname] = col_item
                table_item["columns"].append(col_item)

            col_item = table_item["_col_map"][cname]

            # update column_comment nếu có
            if col.get("column_comment"):
                col_item["column_comment"] = col["column_comment"]

            # merge values
            if col.get("values"):
                col_item["values"].extend(col["values"])

    # merge schema cũ trước
    for t in schema or []:
        upsert_table(t)

    # merge schema_new (ưu tiên)
    for t in schema_new or []:
        upsert_table(t)

    # cleanup
    result = []
    for t in table_map.values():
        t.pop("_col_map", None)
        result.append(t)

    return result

def _update_with_fk(schema):
    fk_rows = db_client.fetch_all("""
        SELECT
            a.table_name AS src_table,
            a.column_name AS src_column,
            c_pk.table_name AS dst_table,
            b.column_name AS dst_column
        FROM user_constraints c
        JOIN user_cons_columns a
          ON c.constraint_name = a.constraint_name
        JOIN user_constraints c_pk
          ON c.r_constraint_name = c_pk.constraint_name
        JOIN user_cons_columns b
          ON c_pk.constraint_name = b.constraint_name
        WHERE c.constraint_type = 'R'
    """)

    # ===== build FK graph =====
    fk_graph = {}
    for r in fk_rows:
        src = r["src_table"]
        fk_graph.setdefault(src, []).append({
            "dst_table": r["dst_table"],
            "src_column": r["src_column"],
            "dst_column": r["dst_column"]
        })

    # ===== map schema =====
    table_map = {t["table_name"]: t for t in schema}

    def ensure_table(table_name):
        if table_name not in table_map:
            table_map[table_name] = {
                "table_name": table_name,
                "table_comment": None,
                "columns": []
            }
        return table_map[table_name]

    def ensure_column(table, column_name):
        cols = table.setdefault("columns", [])
        if not any(c["column_name"] == column_name for c in cols):
            cols.append({
                "column_name": column_name,
                "column_comment": None,
                "values": []
            })

    # ===== 1. direct FK (chỉ khi cả 2 bảng đã có) =====
    for r in fk_rows:
        src = r["src_table"]
        dst = r["dst_table"]

        if src in table_map and dst in table_map:
            ensure_column(table_map[src], r["src_column"])
            ensure_column(table_map[dst], r["dst_column"])

    # ===== 2. bridge table =====
    table_names = list(table_map.keys())

    for i in range(len(table_names)):
        for j in range(i + 1, len(table_names)):
            A = table_names[i]
            B = table_names[j]

            # skip nếu đã có direct FK
            direct = any(
                (fk["dst_table"] == B) for fk in fk_graph.get(A, [])
            ) or any(
                (fk["dst_table"] == A) for fk in fk_graph.get(B, [])
            )

            if direct:
                continue

            # tìm bảng trung gian X
            for X, fks in fk_graph.items():
                targets = [fk["dst_table"] for fk in fks]

                if A in targets and B in targets:
                    # thêm bảng trung gian
                    x_table = ensure_table(X)

                    # thêm columns FK trong X
                    for fk in fks:
                        if fk["dst_table"] in (A, B):
                            ensure_column(x_table, fk["src_column"])

                    break  # chỉ cần 1 bridge là đủ

    return list(table_map.values())

def _filter_schema(query):
    columns_by_values = _find_columns_by_values(query)
    query_emb = get_embedding(query)
    exs = _find_ex(query_emb)
    tables = _find_tables(query_emb)
    columns = _find_columns(query_emb)

    schema = _merge(_merge(tables, columns), columns_by_values)

    schema = _update_with_fk(schema)

    schema = _fill_plus_values(schema)

    return schema, exs

def _fill_plus_values(schema):
    # lấy list columns cần fill
    plus_cols = db_client.fetch_all("""
        SELECT table_name, column_name
        FROM plus_value_columns
    """)

    plus_set = {(r["table_name"], r["column_name"]) for r in plus_cols}

    for t in schema:
        table_name = t["table_name"]

        for c in t.get("columns", []):
            column_name = c["column_name"]

            if (table_name, column_name) in plus_set:
                rows = db_client.fetch_all(f"""
                    SELECT DISTINCT {column_name}
                    FROM {table_name}
                    WHERE {column_name} IS NOT NULL
                """)

                # lấy raw value, giữ nguyên type
                c["values"] = [list(r.values())[0] for r in rows]

    return schema

def retrieve_tables_and_columns(state: GraphState):
    state["db_description"] = _get_db_description()
    schema, exs = _filter_schema(state["question"])
    state["schema"] = schema
    state["examples"] = exs
    return state

if __name__ == "__main__":
    import json

    def print_json(obj, title=""):
        print(f"\n{'='*20} {title} {'='*20}")
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))

    try:
        # 1. Lấy mô tả database
        desc = _get_db_description()
        print(f"DB Description: {desc[:100]}...")

        # 2. Tìm cột theo giá trị
        print("\n--- Tìm cột theo giá trị ---")
        result = _find_columns_by_values("Hà Nội", limit=5)
        print_json(result, "Columns by value 'Hà Nội'")

        # 3. Lấy embedding cho query test
        query_text = "Số lượng ticket SC hôm qua"
        query_emb = get_embedding(query_text)
        print(f"Embedding size: {len(query_emb)}")

        # 4. Tìm examples
        exs = _find_ex(query_emb, limit=2)
        print_json(exs, f"Examples for '{query_text}'")

        # 5. Tìm bảng liên quan
        tables = _find_tables(query_emb, limit=5)
        print_json(tables, "Tables")

        # 6. Tìm cột liên quan
        columns = _find_columns(query_emb, limit=10)
        print_json(columns, "Columns")

        # 7. Merge schema
        schema = _merge(tables, columns)
        print(f"\nMerged schema có {len(schema)} bảng")

        # 8. Thêm FK
        schema_with_fk = _update_with_fk(schema)
        print(f"Schema with FK: {len(schema_with_fk)} bảng")

        # 9. Filter schema toàn bộ (có thể gọi retrieve_tables_and_columns nếu có state)
        state = {"question": query_text}
        state = retrieve_tables_and_columns(state)
        print_json(state["schema"], "Final Schema")
        print(f"Examples: {len(state['examples'])}")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()