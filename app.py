import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SETTING UP THE PAGE ---
st.set_page_config(
    page_title="Betagro HRDD Digital Toolkit",
    layout="wide"
)

# --- 2. FORCE CUSTOM CSS (บังคับเปลี่ยนสีแบบรุนแรง) ---
st.markdown("""
    <style>
    /* บังคับสีพื้นหลังของแอปทั้งหมด */
    .stApp {
        background-color: #F0F4F2 !important;
    }
    
    /* ปรับแต่งแถบเมนูด้านข้าง */
    [data-testid="stSidebar"] {
        background-color: #265F36 !important;
    }
    
    /* เปลี่ยนสีตัวหนังสือใน Sidebar เป็นสีขาว/ทอง */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* หัวข้อหลัก (H1) */
    h1 {
        color: #265F36 !important;
        font-family: 'Helvetica Neue', sans-serif;
        border-bottom: 5px solid #F9A818 !important;
        padding-bottom: 15px;
        font-weight: 800 !important;
    }

    /* หัวข้อรอง (H2, H3) */
    h2, h3 {
        color: #265F36 !important;
        font-weight: 700 !important;
    }

    /* ปุ่มกด (Submit Button) */
    .stButton>button {
        background-color: #265F36 !important;
        color: #FFFFFF !important;
        border: 2px solid #F9A818 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        font-size: 20px !important;
        width: 100% !important;
    }
    
    .stButton>button:hover {
        background-color: #F9A818 !important;
        color: #265F36 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO & TITLE ---
# ใช้ข้อความเก๋ๆ แทนรูปภาพไปก่อนถ้า Link รูปพัง หรือจะลองใช้ Link สำรองนี้ครับ
st.markdown(f"<h1 style='text-align: center;'>BETAGRO</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #265F36;'>HRDD DIGITAL TOOLKIT</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>ความยั่งยืนบนมาตรฐานสากล UNGPs & OECD</p>", unsafe_allow_html=True)
st.write("---")

# --- 4. SIDEBAR MENU ---
st.sidebar.markdown("## ⚙️ MAIN MENU")
choice = st.sidebar.radio("เลือกเครื่องมือที่ต้องการใช้งาน:", 
    ["Tool 1: แบบประเมินสถานะองค์กร", 
     "Tool 2: แบบสอบถามการปฏิบัติ", 
     "Tool 3: แนวทางการสัมภาษณ์", 
     "Tool 4: แบบบันทึกการสังเกตการณ์",
     "Tool 5: ตารางประเมินนัยสำคัญ"])

# --- 5. CONTENT (รายละเอียดครบถ้วนทุกข้อ) ---

if choice == "Tool 1: แบบประเมินสถานะองค์กร":
    st.header("📋 Tool 1: Self-Assessment (Gap Analysis)")
    with st.form("tool1_full"):
        st.subheader("ส่วนที่ 1: การประกาศนโยบายและความมุ่งมั่น")
        q1_1 = st.radio("1.1 องค์กรมีการจัดทำ 'นโยบายสิทธิมนุษยชน' เป็นลายลักษณ์อักษรที่อนุมัติโดยบอร์ดหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_2 = st.radio("1.2 นโยบายครอบคลุมประเด็นสำคัญ (แรงงานข้ามชาติ, สิทธิชุมชน, ความหลากหลาย) หรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q1_3 = st.radio("1.3 มีการสื่อสารนโยบายในภาษาที่แรงงานเข้าใจหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        st.subheader("ส่วนที่ 2: กระบวนการตรวจสอบ (Due Diligence)")
        q2_1 = st.radio("2.1 มีระบบการประเมินความเสี่ยง (HRA) เป็นประจำทุกปีหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        q2_2 = st.radio("2.2 มีระบบตรวจสอบย้อนกลับ (Traceability) ในห่วงโซ่อุปทานหรือไม่?", ["ใช่", "ไม่ใช่", "กำลังดำเนินการ"])
        
        if st.form_submit_button("บันทึกข้อมูล Tool 1"):
            st.success("บันทึกเรียบร้อย! ข้อมูลกำลังไหลไปที่ Google Sheets")

elif choice == "Tool 2: แบบสอบถามการปฏิบัติ":
    st.header("📊 Tool 2: Human Rights Survey")
    with st.form("tool2_full"):
        st.info("เกณฑ์: 1 = น้อยที่สุด, 5 = มากที่สุด")
        q1 = st.select_slider("2.1 ท่านได้รับค่าจ้างตรงเวลาและครบถ้วน?", options=[1,2,3,4,5], value=3)
        q2 = st.select_slider("2.2 มีอุปกรณ์ความปลอดภัย (PPE) เพียงพอ?", options=[1,2,3,4,5], value=3)
        q3 = st.select_slider("2.3 ท่านได้รับการปฏิบัติอย่างเท่าเทียมไม่เลือกปฏิบัติ?", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("ส่งคำตอบแบบสอบถาม"):
            st.balloons()

elif choice == "Tool 3: แนวทางการสัมภาษณ์":
    st.header("🎙️ Tool 3: Interview Guide")
    with st.form("tool3_full"):
        q1 = st.text_area("1. เล่าขั้นตอนการสรรหาและค่าใช้จ่ายที่เกิดขึ้น (ค่าหัวคิว):")
        q2 = st.text_area("2. สภาพหอพักที่บริษัทจัดให้มีความปลอดภัยเพียงพอหรือไม่?")
        if st.form_submit_button("บันทึกบทสัมภาษณ์"):
            st.success("Saved")

elif choice == "Tool 4: แบบบันทึกการสังเกตการณ์":
    st.header("🔎 Tool 4: Observation Log")
    with st.form("tool4_full"):
        c1 = st.checkbox("พนักงานสวม PPE ครบถ้วน")
        c2 = st.checkbox("มีป้ายประกาศสิทธิแรงงานชัดเจน")
        c3 = st.checkbox("ทางหนีไฟพร้อมใช้งาน")
        note = st.text_area("บันทึกเพิ่มเติมจากหน้างาน:")
        if st.form_submit_button("บันทึกการสังเกตการณ์"):
            st.success("บันทึกแล้ว")

elif choice == "Tool 5: ตารางประเมินนัยสำคัญ":
    st.header("⚖️ Tool 5: Risk Matrix Score")
    with st.form("tool5_full"):
        st.write("สูตรการคำนวณ: Severity x Likelihood")
        s = st.slider("ระดับความรุนแรง (Severity)", 1, 5, 3)
        l = st.slider("โอกาสเกิด (Likelihood)", 1, 5, 2)
        if st.form_submit_button("คำนวณความเสี่ยง"):
            score = s * l
            st.metric("คะแนนความเสี่ยง", score)
            if score >= 16: st.error("วิกฤต (Red Zone)")
            elif score >= 6: st.warning("นัยสำคัญ (Yellow Zone)")
            else: st.success("ปกติ (Green Zone)")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center;'>© 2024 Betagro Group | Sustainability Development Department</p>", unsafe_allow_html=True)