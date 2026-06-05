import sqlite3
import re
import os
import json
from collections import Counter
import math

DB_PATH = ".yeyo-memory/sqlite/yeyo-memory.sqlite"
KEYWORDS_PATH = ".yeyo-memory/reports/keyword-cache.json"

def categorize(path):
    p = path.upper()
    if 'MEM' in p or 'CAL' in p or 'MEMORIA' in p or 'ANEJO' in p:
        return 'Memoria y Anejos'
    if 'PLN' in p or 'PLANO' in p or 'SK' in p:
        return 'Planos'
    if 'ESP' in p or 'PLIEGO' in p or 'SPEC' in p:
        return 'Pliego de Condiciones'
    if 'BOQ' in p or 'MTO' in p or 'ESTIMATE' in p or 'PRESUPUESTO' in p or 'MEDICION' in p:
        return 'Mediciones y presupuestos'
    return None

def get_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
    return [s.strip() for s in sentences if len(s.split()) > 5]

def score_sentence(sentence, keywords):
    score = 0
    words = sentence.lower().split()
    for w in words:
        w = re.sub(r'[^\w\s]', '', w)
        if w in keywords:
            score += 1
    return score / max(1, len(words))

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_cache (
            doc_id TEXT PRIMARY KEY,
            category TEXT,
            path TEXT,
            title TEXT,
            summary TEXT,
            keywords TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kb_cat ON kb_cache(category)")

    keywords_cache = {}
    if os.path.exists(KEYWORDS_PATH):
        with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
            keywords_cache = json.load(f)

    cursor.execute("SELECT id, path, title FROM documents")
    docs = cursor.fetchall()

    count = 0
    for doc_id, path, title in docs:
        cat = categorize(path)
        if not cat:
            continue

        # Check if already processed
        cursor.execute("SELECT 1 FROM kb_cache WHERE doc_id = ?", (doc_id,))
        if cursor.fetchone():
            count += 1
            continue

        cursor.execute("SELECT text FROM chunks WHERE document_id = ?", (doc_id,))
        chunks = cursor.fetchall()
        full_text = " ".join([c[0] for c in chunks])
        
        doc_keywords = keywords_cache.get(doc_id, [])
        doc_keywords_set = set(doc_keywords)
        
        # Extractive summary
        sentences = get_sentences(full_text)
        if not sentences:
            summary = ""
        elif not doc_keywords_set:
            summary = " ".join(sentences[:3])
        else:
            scored = [(s, score_sentence(s, doc_keywords_set)) for s in sentences]
            scored.sort(key=lambda x: x[1], reverse=True)
            best_sentences = []
            seen = set()
            for s, _ in scored:
                if s not in seen:
                    best_sentences.append(s)
                    seen.add(s)
                if len(best_sentences) == 3:
                    break
            summary = " ".join(best_sentences)

        kws = ", ".join(doc_keywords)
        cursor.execute("""
            INSERT OR REPLACE INTO kb_cache (doc_id, category, path, title, summary, keywords)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, cat, path, title, summary, kws))
        
        count += 1
        if count % 100 == 0:
            print(f"Processed {count} documents...")
            conn.commit()

    conn.commit()
    print(f"Knowledge cache build completed. Total categorized docs: {count}")

    # Generate a report to view counts
    cursor.execute("SELECT category, COUNT(*) FROM kb_cache GROUP BY category")
    counts = cursor.fetchall()
    for cat, c in counts:
        print(f"{cat}: {c}")

if __name__ == "__main__":
    main()
