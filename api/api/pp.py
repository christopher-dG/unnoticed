import psycopg2
import requests_cache


sess = requests_cache.CachedSession(backend="memory")
select = """
SELECT * FROM scores
 WHERE pp IS NULL
"""
update = "UPDATE scores SET pp = %s WHERE id = %2"


if __name__ == "__main__":
    conn = pyscopg2.connect("")
    cursor = conn.cursor()
    results = cursor.execute(query)
    for score in results.fetchall():
        pass
