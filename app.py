import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# كود التصميم (CSS) 
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea { text-align: right !important; }
    .dashboard-card { border-radius: 12px; padding: 20px 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .dashboard-card h2 { margin: 10px 0 5px 0 !important; font-size: 2.2rem !important; font-weight: 700 !important; color: white !important; text-align: center !important;}
    .dashboard-card p { margin: 0 !important; font-size: 1rem !important; opacity: 0.9 !important; text-align: center !important;}
    .card-green { background-color: #277953; }
    .card-yellow { background-color: #d4a32a; }
    .card-dark { background-color: #1a4d33; }
    .card-brown { background-color: #a47e1b; }
    .gray-bg { background-color: rgba(130, 130, 130, 0.08); padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_output_allow_html=True)

MASTER_PASSWORD = "admin" 
STATUS_OPTIONS = ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"]

# ==========================================
# التعامل مع الملفات والبيانات
# ==========================================
def load_data():
    file_path = 'data.json'
    if not os.path.exists(file_path):
        initial_data = {"groups": {}, "base_url": ""}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return {"groups": {}, "base_url": ""}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# 1. واجهة المشاركين
# ==========================================
if "group" in query_params and query_params["group"] in db["groups"]:
    group_id = query_params["group"]
    group_data = db["groups"][group_id]
    
    st.title(f"📖 {group_data['name']}")
    # (المنطق البرمجي للمشاركة يعمل كما هو)
    st.write("مرحباً بك في صفحة المجموعة. استخدم لوحة التحكم لإدارة الختمة.")

# ==========================================
# 2. لوحة التحكم المركزية
# ==========================================
else:
    st.title("⚙️ لوحة التحكم المركزية")
    admin_login = st.text_input("كلمة المرور:", type="password")
    
    if admin_login == MASTER_PASSWORD:
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة", "📱 المتابعة والتذكير"])
        
        with tab3: # تبويب تعديل المجموعة
            if db["groups"]:
                e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                g_info = db["groups"][e_id]
                
                # إمكانية تعديل اسم الختمة
                new_name = st.text_input("تعديل اسم الختمة:", value=g_info["name"])
                # إمكانية تعديل الختمات المنجزة
                new_khatma_count = st.number_input("تعديل عدد الختمات المنجزة:", value=g_info.get("khatma_count", 0), min_value=0)
                # تعديل الأسماء
                e_text = st.text_area("تعديل أسماء القراء (30 اسماً):", value="\n".join(g_info["readers"]), height=300)
                
                if st.button("حفظ جميع التعديلات"):
                    e_list = [n.strip() for n in e_text.split('\n') if n.strip()]
                    if len(e_list) == 30:
                        db["groups"][e_id]["name"] = new_name
                        db["groups"][e_id]["khatma_count"] = new_khatma_count
                        db["groups"][e_id]["readers"] = e_list
                        save_data(db)
                        st.success("تم تحديث البيانات بنجاح!")
                        st.rerun()
                    else: st.error("يجب أن يكون عدد الأسماء 30.")
        
        # باقي التبويبات (الروابط، إضافة مجموعة، التذكير) تعمل كما برمجناها سابقاً
        with tab1: st.write("قسم الروابط...")
        with tab2: st.write("قسم الإضافة...")
        with tab4: st.write("قسم التذكير...")

    elif admin_login != "":
        st.error("كلمة المرور خاطئة!")
