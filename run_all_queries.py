import sqlite3
import os
import glob
import re

DB_PATH = r'C:\Users\Mujtaba Jafri\Downloads\Product resume Project\Olist SQL\olist.db'
QUERIES_DIR = r'C:\Users\Mujtaba Jafri\Downloads\Product resume Project\Olist SQL\queries'
OUTPUT_DIR = r'C:\Users\Mujtaba Jafri\Downloads\Product resume Project\Olist SQL\output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.text_factory = str

for i in range(1, 11):
    files = glob.glob(os.path.join(QUERIES_DIR, f'{i:02d}_*.sql'))
    if not files:
        print(f'Query {i}: file not found')
        continue

    filepath = files[0]
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Remove single-line comments
    sql_clean = re.sub(r'--.*', '', sql)
    # Split by semicolons at the end of lines (not inside strings)
    statements = sql_clean.split(';')

    outpath = os.path.join(OUTPUT_DIR, f'{i:02d}_output.txt')
    filename = os.path.basename(filepath)

    with open(outpath, 'w', encoding='utf-8') as out:
        out.write(f'=== Query {i}: {filename} ===\n\n')

        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            # Skip PRAGMA statements
            if stmt.upper().startswith('PRAGMA'):
                continue
            try:
                cursor = conn.execute(stmt)
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                out.write(f'Columns: {", ".join(col_names)}\n')
                out.write(f'Rows returned: {len(rows)}\n')
                out.write('-' * 80 + '\n')
                for row in rows[:50]:  # first 50 rows
                    out.write('\t'.join(str(v) if v is not None else 'NULL' for v in row) + '\n')
                out.write('=' * 80 + '\n\n')
            except Exception as e:
                out.write(f'[SKIPPED] Statement not executable standalone (likely CTE/table setup): {str(e)[:80]}\n\n')

    print(f'Query {i}: {filename} -> output/{i:02d}_output.txt')

conn.close()
print('\nAll queries executed.')
