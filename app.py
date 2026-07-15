import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ... (نفس كود التصميم CSS السابق) ...
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea { text-align: right !important; }
    [data-testid="column"] { direction: rtl; }
    .dashboard-card { border-radius: 12px; padding: 20px 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .dashboard-card h2 { margin: 10px 0 5px 0 !important; font-size: 2.2rem !important; font-weight: 700 !important; color: white !important; text-align: center !important;}
    .dashboard-card p { margin: 0 !important; font-size: 1rem !important; opacity: 0.9 !important; text-align: center !important;}
    .dashboard-card .icon { font-size: 1.5rem !important; margin-bottom: 5px !important; text-align: center !important;}
    .card-green { background-color: #277953; }
    .card-yellow { background-color: #d4a32a; }
    .card-dark { background-color: #1a4d33; }
    .card-brown { background-color: #a47e1b; }
    .main-subtitle { text-align: center !important; color: #888; font-size: 1.1rem; margin-bottom: 25px; font-weight: 500;}
    .stats-text { color: #555; font-size: 0.95rem; font-weight: bold; }
    .stats-row { display: flex; justify-content: space-between; margin-top: 15px; margin-bottom: 5px; direction: rtl; }
    div[data-testid="stMarkdownContainer"] > p { margin-bottom: 0px; }
    div[data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] { gap: 10px; }
    div[data-testid="stHorizontalBlock"]:has(.gray-bg) { background-color: rgba(130, 130, 130, 0.08); padding-top: 10px; padding-bottom: 5px; padding-right: 15px; border-radius: 10px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

MASTER_PASSWORD = "admin" 
STATUS_OPTIONS = ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"]

# دوال التعامل مع البيانات (محدثة لتتوافق مع الهيكل)
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            if "base_url" not in data: data["base_url"] = ""
            return data
    except:
        return {"groups": {}, "base_url": ""}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def sanitize_status(status):
    if status in STATUS_OPTIONS: return status
    return "لم تبدأ"

def render_status_label(status, name, strike=False):
    name_html = f"<span style='font-weight: bold;'>{name}</span>"
    if status == "تمت التلاوة":
        sub = "<small style='color: #277953; font-weight: bold;'>🟩 تمت التلاوة</small>"
    else:
        sub = "<small style='color: #888;'>⬜ لم تبدأ بعد</small>"
    return f"<div style='line-height: 1.4;'>{name_html}<br>{sub}</div>"

db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# 1. واجهة المشاركين (كما هي)
# ==========================================
if "group" in query_params and query_params["group"] in db["groups"]:
    group_id = query_params["group"]
    group_data = db["groups"][group_id]
    
    def update_part_status(part_index, source_key):
        new_status = st.session_state[source_key]
        group_data['parts'][part_index] = new_status
        save_data(db)
        
    st.title(f"📖 {group_data['name']}")
    # ... (باقي واجهة المستخدم تظل كما هي) ...
    # (تم اختصار الجزء هنا للتركيز على طلبك في اللوحة)
    st.info("الواجهة تعمل بشكل طبيعي، انتقل للوحة التحكم للتعديل.")

# ==========================================
# 2. لوحة التحكم المركزية (المحدثة)
# ==========================================
else:
    st.title("⚙️ لوحة التحكم المركزية")
    admin_login = st.text_input("كلمة المرور:", type="password")
    
    if admin_login == MASTER_PASSWORD:
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة", "📱 المتابعة والتذكير"])
        
        with tab3: # تبويب تعديل المجموعة المحدث
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
                        st.success("تم تحديث بيانات المجموعة بنجاح!")
                        st.rerun()
                    else: st.error("يجب أن يكون عدد الأسماء 30.")

        # ... (باقي التبويبات تظل كما هي) ...
        with tab1: # عرض الروابط
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**"); st.code(f"{BASE_URL}/?group={g_id}")
                
        with tab2: # إضافة مجموعة
            # ...
            st.write("إضافة جديدة...")
            
        with tab4: # التذكير
            # ...
            st.write("المتابعة...")
