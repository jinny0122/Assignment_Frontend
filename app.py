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

# 💡 核心改动：固定后端网址，不再让用户在页面手动输入
# 本地测试时保持 "http://127.0.0.1:8000"
# 未来 Render 部署后端后，直接把这里的地址换成 Render 的公网 URL 即可
BACKEND_URL = "http://127.0.0.1:8000"

# ==========================================
# 🎨 UI HEADER & BRANDING
# ==========================================
st.title("💼 Employee Burnout Analytics Dashboard")
st.markdown("""
    Welcome to the Enterprise Burnout Prediction Platform. 
    This system leverages advanced **Random Forest Regressors** hosted on a secure backend API 
    to analyze employee workplace metrics and quantify psychological burnout risks.
""")
st.divider() # 高级精细分割线

# ==========================================
# 📋 INTERACTIVE INPUT FORM (Tabbed & Organized)
# ==========================================
st.subheader("📋 Employee Profile & Metrics")

# 使用 Container 容器包裹输入区域，形成类似卡片（Card）的内凹美观视觉感
with st.container(border=True):
    
    # 使用 Tabs 标签页把基本信息和工作压力指标分开，让界面看起来非常专业、干净
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
        # 使用滑块美化，加上明确的说明，比单调的框看起来更具交互感
        designation = st.slider("Designation Level (0.0 = Entry, 5.0 = Executive)", 0.0, 5.0, 2.0, 0.5)
        resource = st.slider("Resource Allocation (1.0 = Low, 10.0 = Overloaded)", 1.0, 10.0, 4.0, 1.0)
        fatigue = st.slider("Mental Fatigue Score (0.0 = Energetic, 10.0 = Exhausted)", 0.0, 10.0, 5.0, 0.1)

# Feature Engineering: Tenure calculation aligned with training pipeline
days_in_company = (pd.to_datetime('2016-12-31') - pd.to_datetime(f"{int(joining_year)}-{int(joining_month):02d}-01")).days

st.write("") # 留空增加视觉呼吸感

# ==========================================
# 🚀 API REQUEST & RISK ASSESSMENT
# ==========================================
# 使用 use_container_width 让按钮拉满整行，更符合现代 Web 扁平化设计大按钮趋势
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
            response = requests.post(f"{BACKEND_URL.strip('/')}/predict", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result["burn_rate"]
                burn_rate_pct = prediction * 100
                
                st.divider()
                st.subheader("📊 Quantitative Risk Assessment Result")
                
                # 结果大卡片区域
                with st.container(border=True):
                    # 大字号核心指标展示
                    st.metric(label="Predicted Employee Burnout Rate", value=f"{burn_rate_pct:.2f}%")
                    
                    # 针对不同等级风险，通过漂亮的警告框 + 精心设计的全英文业务建议，提升作业的 Business Sense
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
            st.error(f"❌ Connection Failed: Unable to reach the API server. Please verify if your FastAPI backend is running locally at {BACKEND_URL}.")