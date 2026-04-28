"""
MarketPulse Streamlit Pages — History Page
Displays all previously generated investment reports from the reports/ directory.
"""

import streamlit as st
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

st.set_page_config(page_title="MarketPulse — Report History", page_icon="📂", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
section[data-testid="stSidebar"]{background:#0d1117;}
.report-card{background:rgba(17,24,39,.8);border:1px solid rgba(99,179,237,.15);border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:.75rem;transition:all .2s ease;}
.report-card:hover{border-color:rgba(99,179,237,.4);}
.report-title{color:#90cdf4;font-weight:600;font-size:.95rem;}
.report-meta{color:#718096;font-size:.78rem;margin-top:.25rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("## 📂 Report History")
st.markdown("All previously generated investment reports are listed below.")

from config.utils import list_saved_reports

reports = list_saved_reports()

if not reports:
    st.info("No reports generated yet. Run an analysis from the main dashboard to create your first report.")
else:
    st.markdown(f"**{len(reports)} report(s) found:**")
    for path in reports:
        filename = os.path.basename(path)
        parts = filename.replace("_report.md", "").split("_")
        ticker = parts[0] if parts else "?"
        try:
            ts = datetime.strptime("_".join(parts[1:3]), "%Y%m%d_%H%M%S")
            date_str = ts.strftime("%B %d, %Y at %H:%M UTC")
        except Exception:
            date_str = "Unknown date"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class='report-card'>
                <div class='report-title'>📄 {ticker} — Investment Report</div>
                <div class='report-meta'>📅 {date_str} &nbsp;·&nbsp; 📁 {filename}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            st.download_button(
                label="⬇️ Download",
                data=content,
                file_name=filename,
                mime="text/markdown",
                key=filename,
            )
            if st.button("👁️ View", key=f"view_{filename}"):
                with st.expander(f"Report: {filename}", expanded=True):
                    st.markdown(content)
