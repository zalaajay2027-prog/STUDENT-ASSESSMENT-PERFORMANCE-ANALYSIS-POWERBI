# Data Analysis Dashboard — Streamlit

## Run locally
1. Extract the ZIP file.
2. Open this folder in VS Code.
3. Open Terminal in this folder.
4. Run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The browser will open the dashboard at `http://localhost:8501`.

## Included
- KPI cards for assessment count, average score, pass rate and attendance
- Batch, department and month filters
- Department, course, batch and monthly trend charts
- Data table and filtered CSV download

## Files
- `app.py`: dashboard application
- `assessments.csv`: assessment records
- `course.csv`: course lookup data
- `requirements.txt`: Python dependencies
