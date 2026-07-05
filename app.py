import requests
import streamlit as st
import pandas as pd

# ==========================================
# ⚙️ GLOBAL CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Employee Burnout Analytics Dashboard", 
    layout="centered", 
    page_icon="💼"
)

# 🔌 两端服务地址清晰解耦
BACKEND_URL = "https://burnout-backend-api.onrender.com"
N8N_WEBHOOK_URL = "https://jinnyy0122.app.n8n.cloud/webhook/burnout-triage"

# ==========================================
# 🎨 UI HEADER & BRANDING
# ==========================================
st.title("💼 Employee Burnout Analytics Dashboard")
st.markdown("""
    Welcome to the Enterprise Burnout Prediction Platform. 
    This system leverages a multi-layer **Agentic Workflow (n8n)** connected to a secure Random Forest 
    FastAPI backend to deliver quantitative calculations and qualitative AI psychological diagnosis.
""")
st.divider() 

# ==========================================
# 📋 INTERACTIVE INPUT FORM
# ==========================================
st.subheader("📋 Employee Profile & Metrics")

with st.container(border=True):
    tab1, tab2 = st.tabs(["👤 Demographic & Company Info", "📊 Workplace & Psychological Metrics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Female", "Male"])
            company_type = st.selectbox("Company Type", ["Service", "Product"])
        with col2:
            wfh = st.selectbox("WFH (Work From Home) Available", ["No", "Yes"])
            joining_year = st.number_input("Joining Year", min_value=2000, max_value=2016, value=2014)
            joining_month = st.slider("Joining Month", 1, 12, 6)

    with tab2:
        designation = st.slider("Designation Level (0.0 = Entry, 5.0 = Executive)", 0.0, 5.0, 2.0, 0.5)
        resource = st.slider("Resource Allocation (1.0 = Low, 10.0 = Overloaded)", 1.0, 10.0, 4.0, 1.0)
        fatigue = st.slider("Mental Fatigue Score (0.0 = Energetic, 10.0 = Exhausted)", 0.0, 10.0, 5.0, 0.1)

days_in_company = (pd.to_datetime('2016-12-31') - pd.to_datetime(f"{int(joining_year)}-{int(joining_month):02d}-01")).days
st.write("") 

# ==========================================
# 🚀 TWO-STAGE INTELLIGENCE ROUTING
# ==========================================
if st.button("🚀 Run Agentic Risk Assessment", use_container_width=True):
    
    # 1. 严格对齐 FastAPI 的 7 个原生标准数字字段，直接请求后端进行机器学习预测
    fastapi_payload = {
        "Gender": gender,
        "Company_Type": company_type,
        "WFH_Setup_Available": wfh,
        "Designation": float(designation),
        "Resource_Allocation": float(resource),
        "Mental_Fatigue_Score": float(fatigue),
        "Joining_Year": int(joining_year),
        "Joining_Month": int(joining_month),
        "Days_In_Company": int(days_in_company)
    }
    
    with st.spinner("⏳ Stage 1: Querying Random Forest Model via FastAPI Backend..."):
        try:
            fastapi_res = requests.post(f"{BACKEND_URL}/predict", json=fastapi_payload, timeout=20)
            if fastapi_res.status_code == 200:
                burn_rate = fastapi_res.json()["burn_rate"]
                burn_rate_pct = burn_rate * 100
                st.toast("⚡ FastAPI quantitative calculation complete!", icon="🔢")
            else:
                st.error(f"❌ Backend Error: Code {fastapi_res.status_code}. Raw response: {fastapi_res.text}")
                st.stop()
        except Exception as e:
            st.error(f"❌ Connection to FastAPI failed: {str(e)}")
            st.stop()
            
    # 2. 将计算好的百分比结果和所有上下文打包，一次性发送给 n8n 触发 AI Agent 做心理学诊断
    with st.spinner("🧙‍♂️ Stage 2: Triggering n8n Workflow & LLM AI Agent..."):
        try:
            n8n_payload = {
                "burn_rate": float(burn_rate),
                "Gender": gender,
                "Company_Type": company_type,
                "WFH_Setup_Available": wfh,
                "Designation": float(designation),
                "Resource_Allocation": float(resource),
                "Mental_Fatigue_Score": float(fatigue),
                "Joining_Year": int(joining_year),
                "Joining_Month": int(joining_month),
                "Days_In_Company": int(days_in_company)
            }
            
            n8n_res = requests.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=60)
            
            if n8n_res.status_code == 200:
                result = n8n_res.json()
                
                # 提取 AI Agent 吐回的诊断、干预和慰问信
                risk_tier = result.get("risk_tier", "UNKNOWN RISK TIER")
                psych_analysis = result.get("psychological_analysis", "No analysis provided.")
                mitigation = result.get("actionable_mitigation", "No recommendations provided.")
                comfort_email = result.get("draft_comfort_email", "No email drafted.")
                
                # ------------------------------------------
                # 🎨 RENDERING WORKSPACE DASHBOARD
                # ------------------------------------------
                st.divider()
                st.subheader("📊 Integrated Intelligence Dashboard")
                
                metric_col, alert_col = st.columns(2)
                with metric_col:
                    st.metric(label="Predicted Employee Burnout Rate", value=f"{burn_rate_pct:.2f}%")
                with alert_col:
                    if "HIGH" in risk_tier.upper():
                        st.error(f"🚨 Triage Action Tier: {risk_tier}")
                    elif "MEDIUM" in risk_tier.upper():
                        st.warning(f"⚠️ Triage Action Tier: {risk_tier}")
                    else:
                        st.success(f"✅ Triage Action Tier: {risk_tier}")
                
                with st.container(border=True):
                    st.markdown("### 📋 AI Expert Psychological Diagnosis")
                    st.write(psych_analysis)
                    st.markdown("### 🛠️ Strategic Management Intervention Steps")
                    st.write(mitigation)
                
                st.write("")
                st.subheader("✉️ Automated HR Support Email Draft")
                st.text_area(label="Copy template:", value=comfort_email, height=240)
                st.toast("🎯 End-to-End Analysis Completed Successfully!", icon="🚀")
            else:
                st.error(f"❌ n8n Gateway Error: Received status code {n8n_res.status_code}. Response: {n8n_res.text}")
        except Exception as e:
            st.error(f"❌ Connection to n8n failed: {str(e)}")