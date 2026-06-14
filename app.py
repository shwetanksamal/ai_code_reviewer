import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise AI Code Reviewer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BACKEND DATABASE SETUP ---
# Expanded rules array to account for the new template options
my_rules = [
    "Guideline 1: Always check for secret keys or passwords hardcoded in the script. Security credentials must be hidden.",
    "Guideline 2: Functions should have comments explaining what they do.",
    "Guideline 3: Avoid using infinite loops like 'while True' without a proper break statement, as it crashes the system.",
    "Guideline 4: Do not use generic, bare exception handling blocks like 'except:' without specifying the exact error type.",
    "Guideline 5: Avoid importing unnecessary modules or using wildcards like 'import *' as it pollutes the namespace."
]

docs = [Document(page_content=rule) for rule in my_rules]

@st.cache_resource
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(docs, embeddings)

db = load_vector_db()


# --- SIDEBAR COMPONENT ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/shield.png", width=80)
    st.title("System Status")
    st.markdown("---")
    st.subheader("📋 Active Guardrails")
    st.caption("The vector engine is actively monitoring for violations against these core rules:")
    for rule in my_rules:
        st.markdown(f"• `{rule.split(':')[0]}`")
    st.markdown("---")
    st.markdown("**Core Engine:** `FAISS-CPU`  \n**Analysis Model:** `all-MiniLM-L6-v2`")


# --- MAIN UI WORKSPACE ---
st.title("🛡️ Enterprise AI Code Reviewer")
st.markdown("Analyze your scripts against engineering compliance benchmarks using localized semantic vector searches.")
st.markdown("---")

st.markdown("### 🔍 Code Workspace")
st.write("You can select an automated template to test the system, or clear the editor and write/paste your own custom code completely from scratch.")

# Expanded Quick-Load Dropdown menu with new features
example_selection = st.selectbox(
    "💡 Quick-Load Code Templates:",
    [
        "📝 Write / Paste Custom Code (Manual Mode)", 
        "🟢 Safe Example (Passes Scan)", 
        "🔴 Password Leaked Example (Fails Scan)", 
        "🔴 Infinite Loop Example (Fails Scan)",
        "🔴 Bare Except Clause Example (Fails Scan)",
        "🔴 Wildcard Import Example (Fails Scan)"
    ]
)

# Assign pre-made code snippets to templates, or keep it blank for custom manual writing
placeholder_text = ""
if example_selection == "🟢 Safe Example (Passes Scan)":
    placeholder_text = "# This function safely calculates area\ndef get_area(width, height):\n    return width * height"
elif example_selection == "🔴 Password Leaked Example (Fails Scan)":
    placeholder_text = "def connect():\n    token = 'API_SECRET_KEY_9981'\n    return token"
elif example_selection == "🔴 Infinite Loop Example (Fails Scan)":
    placeholder_text = "while True:\n    print('Running background tasks...')"
elif example_selection == "🔴 Bare Except Clause Example (Fails Scan)":
    placeholder_text = "try:\n    value = 10 / 0\nexcept:\n    print('An error happened somewhere!')"
elif example_selection == "🔴 Wildcard Import Example (Fails Scan)":
    placeholder_text = "from math import *\n\ndef run_calculation(x):\n    return sqrt(x)"

# Interactive Code Box
user_code = st.text_area(
    "Code Editor Window:",
    value=placeholder_text,
    height=220,
    placeholder="Select a template above, or start typing your own code right here..."
)

# Execution Action Button
if st.button("🚀 Run Vector Scan", type="primary"):
    if user_code.strip() == "":
        st.warning("⚠️ The editor window is empty! Please write some code or select a quick-load template first.")
    else:
        with st.spinner("Analyzing code architecture vectors against compliance records..."):
            # Execute similarity distance search via FAISS
            results = db.similarity_search_with_score(user_code, k=1)
            rule_found, distance_score = results[0][0].page_content, results[0][1]
            
            # Metrics Layout Block
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="📊 RAG Proximity Index (Distance)", value=f"{distance_score:.4f}")
            with col2:
                if distance_score < 1.2:
                    st.markdown("### **Scan Status:** 🔴 **REJECTED**")
                else:
                    st.markdown("### **Scan Status:** 🟢 **APPROVED**")

            st.markdown("---")
            
            # Compliance Evaluation Flow
            if distance_score < 1.2:
                st.error("### ❌ Policy Violation Detected")
                st.markdown("The architectural syntax patterns in this code map too close to known organization anti-patterns.")
                with st.expander("🔬 View Flagged Database Policy Reference", expanded=True):
                    st.info(rule_found)
                st.warning("**Remediation Advice:** Refactor the code layout to address the rule violation highlighted above before creating a development branch merge request.")
            else:
                st.success("### ✅ Clear Run - No Policies Violated")
                st.balloons()
                st.markdown("Excellent work! This code sample falls within clean compliance thresholds. No overlapping vector coordinates matched active vulnerability patterns inside the database.")