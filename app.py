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

# 💡 ✅ 修改位置 1：把这里的地址替换为你用 Web Service 部署好后端后拿到的真实 Render 公网 URL
# ⚠️ 注意：末尾不要加斜杠 /
BACKEND_URL = "https://burnout-backend-api.onrender.com"

# ==========================================
# 🎨 UI HEADER & BRANDING
# ==========================================
st.title("💼 Employee Burnout Analytics Dashboard")
st.markdown("""
    Welcome to the Enterprise Burnout Prediction Platform. 
    This system leverages advanced **Random Forest Regressors** hosted on a secure backend API 
    to analyze employee workplace metrics and quantify psychological burnout risks.
""")
st.divider() 

# ==========================================
# 📋 INTERACTIVE INPUT FORM (Tabbed & Organized)
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

# Feature Engineering: Tenure calculation aligned with training pipeline
days_in_company = (pd.to_datetime('2016-12-31') - pd.to_datetime(f"{int(joining_year)}-{int(joining_month):02d}-01")).days

st.write("") 

# ==========================================
# 🚀 API REQUEST & RISK ASSESSMENT
# ==========================================
if st.button("🚀 Run Remote Risk Assessment", use_container_width=True):
    
    payload = {
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
    
    with st.spinner("Establishing secure connection to AI model..."):
        try:
            # 💡 ✅ 修改位置 2：确保网络请求指向后端的 /predict 路由路径（就像老师代码中的 /predict 一样）
            response = requests.post(f"{BACKEND_URL}/predict", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result["burn_rate"]
                burn_rate_pct = prediction * 100
                
                st.divider()
                st.subheader("📊 Quantitative Risk Assessment Result")
                
                with st.container(border=True):
                    st.metric(label="Predicted Employee Burnout Rate", value=f"{burn_rate_pct:.2f}%")
                    
                    if prediction < 0.3:
                        st.success("""
                            **🟢 LOW RISK STATUS**
                            - **Assessment:** The employee maintains excellent operational metrics. Work pressure is well-balanced within healthy boundaries.
                            - **Action:** No immediate action required. Maintain current work-life balance initiatives.
                        """)
                    elif prediction < 0.7:
                        st.warning("""
                            **🟡 MEDIUM RISK WARNING**
                            - **Assessment:** The employee is showing early signs of psychological fatigue and professional burnout.
                            - **Action:** Management intervention is recommended. Consider optimizing resource allocation or conducting a 1-on-1 check-in.
                        """)
                    else:
                        st.error("""
                            **🔴 HIGH RISK CRITICAL ALERT**
                            - **Assessment:** The employee has reached an extreme state of professional burnout and severe mental exhaustion.
                            - **Action:** Immediate organizational intervention required. Highly recommend mandatory leave, mental wellness support, or critical workload reductions to prevent attrition.
                        """)
            else:
                st.error(f"❌ Backend Server Error: Received status code {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Connection Failed: Unable to reach the API server. Please verify if your FastAPI backend is running properly at {BACKEND_URL}.")