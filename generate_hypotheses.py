import os
import sqlite3
import json
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq

def generate():
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ensure column exists
    try:
        cursor.execute("ALTER TABLE clusters ADD COLUMN research_hypothesis TEXT")
    except sqlite3.OperationalError:
        pass # Column might already exist
        
    cursor.execute("SELECT cluster_id, cluster_name, opportunity_score FROM clusters ORDER BY opportunity_score DESC")
    top_clusters = cursor.fetchall()
    
    # We will use qwen/qwen3.8-27b as the primary, and fallback to others if needed
    fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]
    
    for cluster in top_clusters:
        c_id = cluster['cluster_id']
        c_name = cluster['cluster_name']
        print(f"Processing cluster: {c_name} (ID: {c_id})")
        
        cursor.execute("""
            SELECT user_segment_clue, observed_problem_summary, conversion_blocker, workaround
            FROM insights
            WHERE cluster_id = ? AND duplicate_status = 'UNIQUE' AND relevance_status = 'RELEVANT'
            LIMIT 30
        """, (c_id,))
        insights = cursor.fetchall()
        
        evidence_str = ""
        for i, ins in enumerate(insights):
            evidence_str += f"Observation {i+1}:\n"
            evidence_str += f"- Segment: {ins['user_segment_clue']}\n"
            evidence_str += f"- Problem: {ins['observed_problem_summary']}\n"
            evidence_str += f"- Blocker: {ins['conversion_blocker']}\n"
            evidence_str += f"- Workaround: {ins['workaround']}\n\n"
            
        prompt = f"""You are an elite product manager. Based on the following raw user friction data from a single opportunity cluster named "{c_name}", synthesize a strict, single-sentence research hypothesis.

Your hypothesis MUST follow exactly this format, replacing the bracketed fields with concrete, synthesized insights from the data:
"For [segment], [problem] prevents [behavior] because [root cause]. Users currently work around it by [workaround]."

Do not output anything else. Just the hypothesis string. Do not wrap it in quotes. Ensure it flows naturally as a single sentence.

Raw Data:
{evidence_str}
"""
        
        hypothesis = None
        for model_name in fallback_models:
            try:
                print(f"Trying model: {model_name}")
                temp_model = ChatGroq(model_name=model_name, groq_api_key=api_key, max_tokens=100)
                response = temp_model.invoke(prompt)
                hypothesis = response.content.strip().strip('"')
                break
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                
        if hypothesis:
            print(f"Generated Hypothesis: {hypothesis}\n")
            cursor.execute("UPDATE clusters SET research_hypothesis = ? WHERE cluster_id = ?", (hypothesis, c_id))
        else:
            print("Failed to generate hypothesis.")
            
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    generate()
