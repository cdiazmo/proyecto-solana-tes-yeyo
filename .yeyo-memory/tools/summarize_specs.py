import sqlite3
import json
import os
import re

DB_PATH = ".yeyo-memory/sqlite/yeyo-memory.sqlite"
KEYWORDS_PATH = ".yeyo-memory/reports/keyword-cache.json"
OUTPUT_MD = ".yeyo-memory/reports/specs-summaries.md"

def get_sentences(text):
    # Basic sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
    return [s.strip() for s in sentences if len(s.split()) > 4]

def score_sentence(sentence, keywords):
    score = 0
    words = sentence.lower().split()
    for w in words:
        # Strip punctuation
        w = re.sub(r'[^\w\s]', '', w)
        if w in keywords:
            score += 1
    return score / max(1, len(words))  # normalize by length

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: DB not found at {DB_PATH}")
        return

    # Load keywords
    keywords_cache = {}
    if os.path.exists(KEYWORDS_PATH):
        with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
            keywords_cache = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create summaries table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_summaries (
            document_id TEXT PRIMARY KEY,
            summary_text TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
    """)

    # Get specs documents
    cursor.execute("""
        SELECT id, path, title 
        FROM documents 
        WHERE top_dir = '06 Especificaciones Tecnicas'
    """)
    docs = cursor.fetchall()

    print(f"Found {len(docs)} documents in '06 Especificaciones Tecnicas'.")

    summaries = {}

    for doc_id, path, title in docs:
        cursor.execute("SELECT text FROM chunks WHERE document_id = ?", (doc_id,))
        chunks = cursor.fetchall()
        full_text = " ".join([c[0] for c in chunks])
        
        sentences = get_sentences(full_text)
        doc_keywords = set(keywords_cache.get(doc_id, []))
        
        # If no keywords, fallback to just first sentences
        if not doc_keywords:
            best_sentences = sentences[:3]
        else:
            scored = [(s, score_sentence(s, doc_keywords)) for s in sentences]
            scored.sort(key=lambda x: x[1], reverse=True)
            # Pick top 3 unique sentences
            best_sentences = []
            seen = set()
            for s, score in scored:
                if s not in seen:
                    best_sentences.append(s)
                    seen.add(s)
                if len(best_sentences) == 3:
                    break
            
            # If still empty or poor, add first sentence
            if not best_sentences and sentences:
                best_sentences = sentences[:2]
        
        summary = " ".join(best_sentences)
        summaries[doc_id] = {
            "path": path,
            "title": title if title else os.path.basename(path),
            "summary": summary
        }
        
        # Store in DB
        cursor.execute("""
            INSERT INTO document_summaries (document_id, summary_text)
            VALUES (?, ?)
            ON CONFLICT(document_id) DO UPDATE SET summary_text = excluded.summary_text
        """, (doc_id, summary))

    conn.commit()

    # Generate Markdown report
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# Resumen de Especificaciones Técnicas\n\n")
        f.write("Este documento contiene un resumen extractivo (generado localmente) de las especificaciones técnicas.\n\n")
        
        for doc_id, data in summaries.items():
            f.write(f"### {data['title']}\n")
            f.write(f"- **Archivo:** `{data['path']}`\n")
            if doc_id in keywords_cache:
                f.write(f"- **Keywords:** {', '.join(keywords_cache[doc_id])}\n")
            f.write(f"- **Resumen:** {data['summary']}\n\n")

    print(f"Saved summaries to database table 'document_summaries' and report '{OUTPUT_MD}'")

if __name__ == "__main__":
    main()
