import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Analysis Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp {background:#142D4E;}
[data-testid="stSidebar"] {background:#14B8A6;}
[data-testid="stSidebar"] * {color:white !important;}
.title {font-size:32px;font-weight:800;color:#172B4D;margin-bottom:0;}
.subtitle {font-size:15px;color:#667085;margin:0 0 22px 0;}
.kpi {background:white;border:1px solid #E5EAF2;border-radius:14px;padding:18px 20px;box-shadow:0 3px 12px #172b4d12;}
.klabel {font-size:13px;color:#667085;font-weight:600;}
.kvalue {font-size:27px;font-weight:800;color:#172B4D;margin-top:5px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    assessments = pd.read_csv("assessments.csv")
    courses = pd.read_csv("course.csv")
    assessments["score"] = pd.to_numeric(assessments["score"], errors="coerce")
    assessments["attendance_pct"] = pd.to_numeric(assessments["attendance_pct"], errors="coerce")
    data = assessments.merge(courses, on="course_id", how="left")
    data["Result"] = data["score"].apply(lambda x: "Pass" if pd.notna(x) and x >= 50 else "Fail")
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data["month"] = pd.Categorical(data["month"], categories=order, ordered=True)
    return data

df = load_data()
st.sidebar.title("📊 Dashboard Filters")
batch_opts = sorted(df["batch"].dropna().unique().tolist())
dept_opts = sorted(df["department"].dropna().unique().tolist())
month_opts = [m for m in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] if m in df["month"].astype(str).unique()]
batches = st.sidebar.multiselect("Batch", batch_opts, default=batch_opts)
departments = st.sidebar.multiselect("Department", dept_opts, default=dept_opts)
months = st.sidebar.multiselect("Month", month_opts, default=month_opts)

f = df[df["batch"].isin(batches) & df["department"].isin(departments) & df["month"].astype(str).isin(months)].copy()
st.markdown('<div class="title">📊 Data Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Student Assessment Performance | Scores | Attendance | Course Insights</div>', unsafe_allow_html=True)

if f.empty:
    st.warning("No data matches these filters. Select different filters from the sidebar.")
    st.stop()

n = len(f)
avg = f["score"].mean()
pass_rate = f["score"].ge(50).mean()*100
attendance = f["attendance_pct"].mean()
kpis = [
    ("Total Assessments", f"{n:,}"),
    ("Average Score", f"{avg:.1f}" if pd.notna(avg) else "N/A"),
    ("Pass Rate", f"{pass_rate:.1f}%"),
    ("Average Attendance", f"{attendance:.1f}%" if pd.notna(attendance) else "N/A")
]
cols = st.columns(4)
for col, (label, value) in zip(cols, kpis):
    col.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div></div>', unsafe_allow_html=True)

st.subheader("Department Performance")
left, right = st.columns(2)
dept = f.groupby("department", as_index=False)["score"].mean().sort_values("score", ascending=False)
fig = px.bar(dept, x="department", y="score", text_auto=".1f", title="Average Score by Department",
             labels={"department":"Department","score":"Average Score"})
fig.update_yaxes(range=[0,100])
fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=350,margin=dict(l=15,r=15,t=55,b=15))
left.plotly_chart(fig, use_container_width=True)

passes = f.assign(Pass=f["score"].ge(50)).groupby("department",as_index=False)["Pass"].mean()
passes["Pass Rate (%)"] = passes["Pass"]*100
fig = px.bar(passes, x="department", y="Pass Rate (%)", text_auto=".1f", title="Pass Rate by Department")
fig.update_yaxes(range=[0,100])
fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=350,margin=dict(l=15,r=15,t=55,b=15))
right.plotly_chart(fig, use_container_width=True)

st.subheader("Monthly Score Trend")
monthly = f.groupby("month", observed=False, as_index=False)["score"].mean().dropna().sort_values("month")
fig = px.line(monthly, x="month", y="score", markers=True, text=monthly["score"].round(1),
              title="Average Score by Month", labels={"month":"Month","score":"Average Score"})
fig.update_traces(textposition="top center")
fig.update_yaxes(range=[0,100])
fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=360,margin=dict(l=15,r=15,t=55,b=15))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Course and Batch Insights")
left, right = st.columns(2)
course = f.groupby(["course","department"],as_index=False)["score"].mean().sort_values("score",ascending=False)
fig = px.bar(course,x="course",y="score",color="department",text_auto=".1f",title="Average Score by Course",
             labels={"course":"Course","score":"Average Score"})
fig.update_yaxes(range=[0,100])
fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=350,margin=dict(l=15,r=15,t=55,b=15))
left.plotly_chart(fig,use_container_width=True)

batch = f.groupby("batch",as_index=False)["score"].mean().sort_values("score",ascending=False)
fig = px.bar(batch,x="batch",y="score",text_auto=".1f",title="Average Score by Batch",
             labels={"batch":"Batch","score":"Average Score"})
fig.update_yaxes(range=[0,100])
fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",height=350,margin=dict(l=15,r=15,t=55,b=15))
right.plotly_chart(fig,use_container_width=True)

st.subheader("Assessment Records")
show_cols = ["assessment_id","month","course_id","course","department","batch","score","attendance_pct","Result"]
st.dataframe(f[show_cols].sort_values(["month","assessment_id"]),use_container_width=True,hide_index=True)
st.download_button("⬇️ Download Filtered Data", f.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_data.csv", mime="text/csv")
st.caption("Built with Streamlit, Pandas and Plotly.")
