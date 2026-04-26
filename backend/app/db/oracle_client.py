import oracledb
from app.config import settings

class OracleClient:
    def __init__(self):
        self.conn = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=settings.DB_DSN
        )

    def close(self):
        self.conn.close()