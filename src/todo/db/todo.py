import psycopg2

from todo.payload.todo import Todo


class TodoDB(object):
    # This class is supposed to be used as a singleton, where a new instance is aquired, via creation
    # or via return of the existing instance via the instance() classmethod below.
    _instance: Todo = None

    def __init__(self):
        self._conn = self.connect()

    def connect(self):
        # FIXME: The database connection string values should be read from environment variables.
        return psycopg2.connect("dbname=todoapp user=todouser password=todosecret host=postgres port=5432")

    def create(self, payload: Todo):
        cur = self._conn.cursor()
        sql: str = "INSERT INTO todo (todo_id, text, status) VALUES (%s, %s, %s)"
        cur.execute(sql, (str(payload.get_id()), payload.get_text(), payload.get_status()))
        self._conn.commit()
        cur.close()

    def get(self, todoid: str):
        cur = self._conn.cursor()
        sql: str = "SELECT todo_id, text, status FROM todo WHERE todo_id=%s"
        cur.execute(sql, (todoid,))
        row = cur.fetchone()
        cur.close()
        return Todo(row[1], row[0], row[2]) if row is not None else None

    def list(self, textmatch: str = None, status: str = None):
        cur = self._conn.cursor()
        sql: str = "SELECT todo_id, text, status FROM todo"

        parameters = []
        first_where_criteria = True
        if textmatch:
            sql += " WHERE " if first_where_criteria else ''
            sql += "text LIKE %s ESCAPE ''"
            parameters.append('%' + textmatch + '%')
            first_where_criteria = False

        if status:
            sql += " WHERE " if first_where_criteria else ''
            sql += " AND " if not first_where_criteria else ''
            sql += "status = %s"
            parameters.append(status)
            first_where_criteria = False

        if not parameters:
            cur.execute(sql)
        else:
            cur.execute(sql, tuple(parameters))

        found_payloads = []
        for row in cur:
            found_payloads.append(Todo(row[1], row[0], row[2]))

        cur.close()
        return found_payloads

    def update(self, payload: Todo):
        cur = self._conn.cursor()
        sql: str = "UPDATE todo SET text=%s, status=%s WHERE todo_id=%s"
        cur.execute(sql, (payload.get_text(), payload.get_status(), str(payload.get_id())))
        self._conn.commit()
        cur.close()

        return self.get(payload.get_id())

    def delete(self, todoid: str):
        cur = self._conn.cursor()
        sql: str = "DELETE FROM todo WHERE todo_id=%s"
        cur.execute(sql, (todoid,))
        is_delete_successful = cur.rowcount == 1
        self._conn.commit()
        cur.close()
        return is_delete_successful

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
