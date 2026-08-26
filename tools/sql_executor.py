from database.db import get_connection


def execute_sql(sql: str):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql)

        result = cursor.fetchall()

        return result, None

    except Exception as e:

        return None, str(e)

    finally:

        cursor.close()
        conn.close()