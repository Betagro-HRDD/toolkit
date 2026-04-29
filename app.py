import streamlit as st
import pandas as pd

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(page_title="Betagro HRDD Premium Toolkit", layout="wide")

# --- 2. THE PREMIUM STYLING (BETAGRO LUXURY THEME) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    
    .stApp { background: linear-gradient(to bottom, #F0F4F2, #FFFFFF); }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1E3F26 !important; border-right: 5px solid #F9A818; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Header & Cards */
    .header-box { 
        background-color: white; padding: 30px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 8px solid #F9A818;
        margin-bottom: 25px; text-align: center;
    }
    h1 { color: #1E3F26; font-weight: 800; font-size: 2.5rem; margin-bottom: 0; }
    h2 { color: #265F36; border-left: 10px solid #F9A818; padding-left: 15px; }
    
    /* Heat Map Table Styling */
    .heat-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .heat-cell { height: 60px; width: 60px; text-align: center; font-weight: bold; color: white; border-radius: 5px; font-size: 1.2rem; }
    .label-cell { color: #666; font-size: 0.9rem; font-weight: bold; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1E3F26 0%, #2D5A3A 100%);
        color: white; border-radius: 50px; border: none; padding: 10px 40px;
        font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("""
    <div class="header-box">
        <h1>BETAGRO HRDD DIGITAL TOOLKIT</h1>
        <p style='color: #666; font-size: 1.1rem;'>Smart Human Rights Due Diligence Framework</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://www.betagro.com/assets/img/logo/logo.png", width=160)
    st.markdown("---")
    choice = st.radio("MAIN NAVIGATION", [
        "Dashboard & Framework",
        "Tool 1: Policy Assessment",
        "Tool 2: Worker Survey",
        "Tool 3: In-depth Interview",
        "Tool 4: Field Observation",
        "Tool 5: Salient Risk Matrix",
        "Tool 6: AI Data Triangulation"
    ])

# --- 5. LOGIC & CONTENT ---

if choice == "Tool 1: Policy Assessment":
    st.header("เครื่องมือที่ 1: การประเมินนโยบาย (Gap Analysis)")
    with st.form("t1"):
        st.subheader("หมวด A: การกำกับดูแล (Governance)")
        q1 = st.radio("A.1 มีนโยบายสิทธิมนุษยชนที่ลงนามโดย CEO/บอร์ด หรือไม่?", ["ใช่ (3)", "กำลังทำ (1)", "ไม่มี (0)"])
        q2 = st.radio("A.2 มีการแต่งตั้งคณะทำงานด้านสิทธิมนุษยชนโดยเฉพาะ?", ["ใช่ (3)", "ไม่มี (0)"])
        st.subheader("หมวด B: กระบวนการ (Due Diligence)")
        q3 = st.radio("B.1 มีการระบุประเด็นความเสี่ยง (HRA) ประจำปี?", ["ใช่ (3)", "ไม่เคย (0)"])
        if st.form_submit_button("บันทึกข้อมูลนโยบาย"): st.success("บันทึกแล้ว")

elif choice == "Tool 5: Salient Risk Matrix":
    st.header("เครื่องมือที่ 5: การประเมินความเสี่ยงที่มีนัยสำคัญ")
    
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("### 📝 ระบุค่าประเมิน")
        issue = st.text_input("ประเด็นความเสี่ยง:", "แรงงานข้ามชาติ")
        s_scale = st.slider("ขนาดความรุนแรง (Scale)", 1, 5, 3)
        s_scope = st.slider("ขอบเขต (Scope)", 1, 5, 2)
        s_rem = st.slider("การเยียวยา (Remediability)", 1, 5, 3)
        sev_max = max(s_scale, s_scope, s_rem)
        likelihood = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 2)
        score = sev_max * likelihood
        st.metric("SALIENCE SCORE", score)

    with c2:
        st.markdown("### 🗺️ Salient Risk Heat Map")
        # สร้าง HTML Heat Map แบบพรีเมียม
        def draw_heat_map(cur_s, cur_l):
            rows = ""
            for l in range(5, 0, -1):
                rows += "<tr>"
                rows += f"<td class='label-cell'>{l}</td>"
                for s in range(1, 6):
                    val = s * l
                    color = "#EF4444" if val >= 16 else ("#F9A818" if val >= 8 else "#265F36")
                    mark = "★" if s == cur_s and l == cur_l else ""
                    rows += f"<td class='heat-cell' style='background-color:{color}; border: 2px solid white;'>{mark}</td>"
                rows += "</tr>"
            
            return f"""
            <table class='heat-table'>
                {rows}
                <tr class='label-cell'><td></td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr>
            </table>
            """
        st.markdown(draw_heat_map(sev_max, likelihood), unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888;'>แกนนอน: Severity | แกนตั้ง: Likelihood</p>", unsafe_allow_html=True)

    if score >= 16: st.error("🚨 ผลลัพธ์: ความเสี่ยงระดับวิกฤต (Salient Risk)")
    elif score >= 8: st.warning("⚠️ ผลลัพธ์: ความเสี่ยงระดับนัยสำคัญ")
    else: st.success("✅ ผลลัพธ์: ความเสี่ยงในระดับจัดการได้")

elif choice == "Tool 6: AI Data Triangulation":
    st.header("เครื่องมือที่ 6: ระบบวิเคราะห์ความสอดคล้องด้วย AI")
    st.markdown("""
    ระบบนี้ใช้ **NotebookLM Logic** เพื่อเปรียบเทียบข้อมูลจาก 3 แหล่ง (Triangulation):
    1. **Policy (Tool 1):** นโยบายที่ผู้บริหารแจ้ง
    2. **Field Data (Tool 2-4):** เสียงพนักงานและการสังเกตการณ์
    3. **Standards:** มาตรฐานสากล UNGPs/OECD
    """)
    st.text_area("กรอกข้อมูลดิบจากหน้างาน (Raw Data):", placeholder="เช่น แรงงานแจ้งว่าไม่เคยเห็นป้ายนโยบายสิทธิมนุษยชน...")
    if st.button("เริ่มการวิเคราะห์ด้วย AI"):
        st.info("AI กำลังตรวจสอบความสอดคล้อง... (ในเวอร์ชันเต็มจะดึงข้อมูลจาก Database มาเปรียบเทียบอัตโนมัติ)")

# --- FOOTER ---
st.write("---")
st.markdown("<div style='text-align:center; color:#999;'>© 2024 Betagro Group | Human Rights Due Diligence Digital Ecosystem</div>", unsafe_allow_html=True)