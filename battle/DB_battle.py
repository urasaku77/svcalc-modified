import sqlite3

class DB_battle:

    def register_battle(battle):
        dbname = 'battle/battle.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        cur.executemany('INSERT INTO battle values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (battle, ))
        cur.close()
        conn.commit()
        conn.close()