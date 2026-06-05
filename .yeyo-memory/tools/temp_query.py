import sqlite3
import re

c = sqlite3.connect('.yeyo-memory/sqlite/yeyo-memory.sqlite')
q = """
SELECT d.path, c.text 
FROM documents d 
JOIN chunks c ON d.id = c.document_id 
WHERE (d.path LIKE '%ESP%' OR d.path LIKE '%Pliego%' OR d.path LIKE '%SPEC%') 
AND ((lower(c.text) LIKE '%pump%' AND lower(c.text) LIKE '%install%') 
  OR (lower(c.text) LIKE '%bomba%' AND lower(c.text) LIKE '%instala%')
  OR (lower(c.text) LIKE '%bomba%' AND lower(c.text) LIKE '%montaje%'))
"""
res = c.execute(q).fetchall()
for p, text in res[:3]:
    print(f"\n--- {p.split('/')[-1]} ---")
    idx = max(0, text.lower().find("pump"))
    if idx == -1: idx = max(0, text.lower().find("bomba"))
    print(text[max(0, idx-100) : min(len(text), idx+200)])
