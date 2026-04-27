import oracledb
from app.config import settings


class OracleClient:
    def __init__(self):
        self.conn = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=settings.DB_DSN
        )

    def cursor(self):
        return self.conn.cursor()

    def fetch_one(self, sql, params=None):
        """
        Return single row (dict) or None
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params or {})

            if not cursor.description:
                return None

            row = cursor.fetchone()
            if not row:
                return None

            columns = [col[0].lower() for col in cursor.description]
            return dict(zip(columns, row))

        finally:
            cursor.close()

    def fetch_all(self, sql, params=None):
        """
        Return list of dict rows
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params or {})

            if not cursor.description:
                return []

            columns = [col[0].lower() for col in cursor.description]
            rows = cursor.fetchall()

            return [dict(zip(columns, row)) for row in rows]

        finally:
            cursor.close()

    def execute(self, sql, params=None):
        """
        For INSERT / UPDATE / DELETE
        Return affected row count
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params or {})
            self.conn.commit()
            return cursor.rowcount

        except Exception:
            self.conn.rollback()
            raise

        finally:
            cursor.close()

    def executemany(self, sql, params_list):
        """
        Bulk insert/update
        """
        cursor = self.conn.cursor()
        try:
            cursor.executemany(sql, params_list)
            self.conn.commit()
            return cursor.rowcount

        except Exception:
            self.conn.rollback()
            raise

        finally:
            cursor.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()
        self.close()