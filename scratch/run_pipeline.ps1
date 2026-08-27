echo "1. Running AI Analyzer on remaining data (This will take ~60 minutes)..."
.\venv\Scripts\python.exe src\ai_engine\analyzer.py

echo "2. Rebuilding SQLite Database (Clustering and Quantification)..."
.\venv\Scripts\python.exe src\processing\quantification.py

echo "3. Rebuilding ChromaDB Vector Store..."
.\venv\Scripts\python.exe src\ai_engine\vector_store.py

echo "4. Re-injecting thesis-aligned synthetic data..."
.\venv\Scripts\python.exe scratch\inject_thesis_data.py

echo "5. Committing changes to git..."
git add data/warehouse/ajio_warehouse.db data/vector_db/
git add data/reports/
git commit -m "chore: process remaining raw data points and rebuild databases"
git push origin main

echo "Pipeline Complete!"
