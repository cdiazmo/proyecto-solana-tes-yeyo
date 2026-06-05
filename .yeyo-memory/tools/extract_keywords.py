import sqlite3
import re
import math
import json
import csv
from collections import Counter, defaultdict
import os

DB_PATH = ".yeyo-memory/sqlite/yeyo-memory.sqlite"
OUTPUT_JSON = ".yeyo-memory/reports/keyword-cache.json"
OUTPUT_CSV = ".yeyo-memory/reports/global-keywords.csv"

STOP_WORDS = set([
    # English
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we", "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one", "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their", "news", "out", "use", "any", "there", "see", "only", "so", "his", "when", "contact", "here", "business", "who", "web", "also", "now", "help", "get", "pm", "view", "online", "first", "am", "been", "would", "how", "were", "me", "s", "services", "some", "these", "click", "its", "like", "service", "x", "than", "find", "price", "date", "back", "top", "people", "had", "list", "name", "just", "over", "state", "year", "day", "into", "email", "two", "health", "n", "world", "re", "next", "used", "go", "b", "work", "last", "most", "products", "music", "buy", "data", "make", "them", "should", "product", "system", "post", "her", "city", "t", "add", "policy", "number", "such", "please", "available", "copyright", "support", "message", "after", "best", "software", "then", "jan", "good", "video", "well", "d", "where", "info", "rights", "public", "books", "high", "school", "through", "m", "each", "links", "she", "review", "years", "order", "very", "privacy", "book", "items", "company", "read", "group", "sex", "need", "many", "user", "said", "de", "does", "set", "under", "general", "research", "university", "january", "mail", "full", "map", "reviews", "program", "life",
    # Spanish
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos", "estáis", "están", "esté", "estés", "estemos", "estéis", "estén", "estaré", "estarás", "estará", "estaremos", "estaréis", "estarán", "estaría", "estarías", "estaríamos", "estaríais", "estarían", "estaba", "estabas", "estábamos", "estabais", "estaban", "estuve", "estuviste", "estuvo", "estuvimos", "estuvisteis", "estuvieron", "estuviera", "estuvieras", "estuviéramos", "estuvierais", "estuvieran", "estuviese", "estuvieses", "estuviésemos", "estuvieseis", "estuviesen", "estando", "estado", "estada", "estados", "estadas", "estad", "he", "has", "ha", "hemos", "habéis", "han", "haya", "hayas", "hayamos", "hayáis", "hayan", "habré", "habrás", "habrá", "habremos", "habréis", "habrán", "habría", "habrías", "habríamos", "habríais", "habrían", "había", "habías", "habíamos", "habíais", "habían", "hube", "hubiste", "hubo", "hubimos", "hubisteis", "hubieron", "hubiera", "hubieras", "hubiéramos", "hubierais", "hubieran", "hubiese", "hubieses", "hubiésemos", "hubieseis", "hubiesen", "habiendo", "habido", "habida", "habidos", "habidas", "soy", "eres", "es", "somos", "sois", "son", "sea", "seas", "seamos", "seáis", "sean", "seré", "serás", "será", "seremos", "seréis", "serán", "sería", "serías", "seríamos", "seríais", "serían", "era", "eras", "éramos", "erais", "eran", "fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron", "fuera", "fueras", "fuéramos", "fuerais", "fueran", "fuese", "fueses", "fuésemos", "fueseis", "fuesen", "siendo", "sido", "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen", "tenga", "tengas", "tengamos", "tengáis", "tengan", "tendré", "tendrás", "tendrá", "tendremos", "tendréis", "tendrán", "tendría", "tendrías", "tendríamos", "tendríais", "tendrían", "tenía", "tenías", "teníamos", "teníais", "tenían", "tuve", "tuviste", "tuvo", "tuvimos", "tuvisteis", "tuvieron", "tuviera", "tuvieras", "tuviéramos", "tuvierais", "tuvieran", "tuviese", "tuvieses", "tuviésemos", "tuvieseis", "tuviesen", "teniendo", "tenido", "tenida", "tenidos", "tenidas", "tened",
    # Additional generic docs and tech
    "proyecto", "documento", "fecha", "página", "rev", "código", "titulo", "descripción", "planos", "plano", "tipo", "solana", "yeyo", "tes", "system", "systems", "nº", "n", "m", "mm", "cm", "kg", "pdf", "xlsx", "xls", "dwg"
])

def tokenize(text):
    text = text.lower()
    # Replace non-alphanumeric with spaces, allowing basic accents
    words = re.findall(r'\b[a-záéíóúñ]+\b', text)
    # Filter length and stop words
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Fetching documents and chunks...")
    cursor.execute("SELECT document_id, text FROM chunks")
    rows = cursor.fetchall()

    doc_texts = defaultdict(list)
    for doc_id, text in rows:
        doc_texts[doc_id].append(text)

    print(f"Found {len(doc_texts)} documents with text.")

    doc_tf = {}
    df_counts = Counter()
    total_docs = len(doc_texts)

    print("Tokenizing and counting term frequencies...")
    for doc_id, texts in doc_texts.items():
        full_text = " ".join(texts)
        tokens = tokenize(full_text)
        tf = Counter(tokens)
        doc_tf[doc_id] = tf
        for term in tf:
            df_counts[term] += 1

    print("Calculating TF-IDF and picking top keywords per doc...")
    doc_keywords = {}
    for doc_id, tf in doc_tf.items():
        tfidf_scores = {}
        for term, count in tf.items():
            df = df_counts[term]
            idf = math.log((total_docs + 1) / (df + 1)) + 1
            tfidf_scores[term] = count * idf
        
        # Sort terms by score
        top_terms = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:15]
        doc_keywords[doc_id] = [t[0] for t in top_terms]

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc_keywords, f, indent=2, ensure_ascii=False)
    print(f"Saved keyword cache to {OUTPUT_JSON}")

    # Calculate global top keywords based on overall frequency
    # We'll weigh them by DF and total frequency
    global_term_score = []
    for term, df in df_counts.items():
        if df > 1 and df < total_docs * 0.8:  # ignore terms appearing in >80% docs
            total_freq = sum(doc_tf[d].get(term, 0) for d in doc_tf)
            global_term_score.append((term, total_freq, df))

    global_term_score.sort(key=lambda x: x[1], reverse=True)
    
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Total Frequency", "Document Frequency"])
        for row in global_term_score[:500]:
            writer.writerow(row)
    print(f"Saved global keywords to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
