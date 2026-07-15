import streamlit as st
import json
import uuid
import urllib.parse 

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# كود التصميم (CSS) للغة العربية وتنسيق الأزرار
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea { text-align: right !important; }
    [data-testid="column"] { direction: rtl; }
    
    /* تنسيق بطاقات الإحصائيات العلوية */
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
    .dashboard-card * { text-align: center !important; }

    /* تحسين مظهر أزرار الخيارات الأفقية لتبدو كأزرار حقيقية متناسقة */
    div[data-testid="stMarkdownContainer"] > p { margin-bottom: 0px; }
    div[data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] {
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)

MASTER_PASSWORD = "admin" 
STATUS_OPTIONS = ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"]

# دوال التعامل مع البيانات
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

# تحويل وتنظيف حالات القراءة القديمة لتجنب المشاكل
def sanitize_status(status):
    if status is True or status == "تمت القراءة":
        return "تمت التلاوة"
    if status is False or status == "جاري القراءة":
        return "لم تبدأ"
    if status not in STATUS_OPTIONS:
        return "لم تبدأ"
    return status

db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# 1. واجهة المشاركين (تفتح مباشرة من الرابط بدون كلمة مرور)
# ==========================================
if "group" in query_params and query_params["group"] in db["groups"]:
    group_id = query_params["group"]
    group_data = db["groups"][group_id]
    
    # حساب الإنجاز الذكي بناءً على الخيارات الجديدة
    progress_weights = {
        "لم تبدأ": 0.0,
        "نص جزء": 0.5,
        "حزب": 0.5,
        "حزب ونص": 0.75,
        "تمت التلاوة": 1.0
    }
    
    completed_parts = 0.0
    for status in group_data['parts']:
        sanitized = sanitize_status(status)
        completed_parts += progress_weights.get(sanitized, 0.0)
        
    progress_percentage = completed_parts / 30.0
    completed_disp = int(completed_parts) if completed_parts.is_integer() else completed_parts
    remaining_disp = int(30 - completed_parts) if (30 - completed_parts).is_integer() else (30 - completed_parts)
    
    st.title(f"📖 {group_data['name']}")
    st.markdown("<div class='main-subtitle'>متابعة الختمة · 30 جزء · 30 قارئ</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<div class='dashboard-card card-green'><div class='icon'>👥</div><h2>30</h2><p>المشاركين</p></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='dashboard-card card-yellow'><div class='icon'>✅</div><h2>{completed_disp}</h2><p>الأجزاء المكتملة</p></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='dashboard-card card-dark'><div class='icon'>⏳</div><h2>{remaining_disp}</h2><p>المتبقية</p></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='dashboard-card card-brown'><div class='icon'>🔄</div><h2>{group_data.get('khatma_count', 0)}</h2><p>الختمات المنجزة</p></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='stats-row'><span class='stats-text'>نسبة الإنجاز الإجمالية: {int(progress_percentage * 100)}%</span></div>", unsafe_allow_html=True)
    st.progress(progress_percentage)
    st.write("---")

    tab_overview, tab_mark, tab_details, tab_schedule = st.tabs(["📊 الجدول", "✅ تأكيد الحفظ", "📖 تفاصيل", "📅 الخطة"])

    with tab_overview:
        for i in range(30):
            # تم تعديل نسب الأعمدة لإعطاء مساحة كافية لأزرار الخيارات الأفقية
            col1, col2, col3, col4 = st.columns([1, 2, 5.5, 1])
            with col1: st.write(f"**الجزء {i+1}**")
            
            current_status = sanitize_status(group_data['parts'][i])
            
            # عمود القارئ مع إظهار الحالة الملونة تحته
            with col2: 
                st.write(f"**{group_data['readers'][i]}**")
                if current_status == "تمت التلاوة":
                    st.markdown("<small style='color: #277953; font-weight: bold;'>● تمت التلاوة</small>", unsafe_allow_html=True)
                elif current_status == "حزب ونص":
                    st.markdown("<small style='color: #d4a32a; font-weight: bold;'>● حزب ونص</small>", unsafe_allow_html=True)
                elif current_status in ["حزب", "نص جزء"]:
                    st.markdown(f"<small style='color: #a47e1b; font-weight: bold;'>● {current_status}</small>", unsafe_allow_html=True)
                else:
                    st.markdown("<small style='color: #888;'>● لم يبدأ بعد</small>", unsafe_allow_html=True)
                
            # استبدال القائمة المنسدلة بأزرار خيارات أفقية (Radio Buttons)
            with col3:
                selected = st.radio(
                    f"الحالة_{i}", 
                    STATUS_OPTIONS, 
                    index=STATUS_OPTIONS.index(current_status), 
                    key=f"s_{i}", 
                    horizontal=True,
                    label_visibility="collapsed"
                )
                if selected != current_status:
                    group_data['parts'][i] = selected
                    save_data(db)
                    st.rerun()
                    
            with col4:
                if current_status != "تمت التلاوة":
                    msg = f"تذكير بقراءة *الجزء {i+1}*\nالقارئ: *{group_data['readers'][i]}*\nالحالة الحالية: *{current_status}*\nرابط تسجيل الإتمام:\n{BASE_URL}/?group={group_id}"
                    st.link_button("📱 تذكير", f"https://wa.me/?text={urllib.parse.quote(msg)}")
                else:
                    st.markdown("<span style='color: #277953; font-weight: bold;'>✅ مكتمل</span>", unsafe_allow_html=True)
                    
        st.write("---")
        if completed_parts == 30.0:
            pwd = st.text_input("كلمة المرور لإغلاق الختمة وترحيل الأسماء:", type="password")
            if st.button("إغلاق الختمة"):
                if pwd == group_data["password"]:
                    group_data["khatma_count"] = group_data.get("khatma_count", 0) + 1
                    readers = group_data["readers"]
                    group_data["readers"] = [readers[-1]] + readers[:-1] 
                    group_data["parts"] = ["لم تبدأ"] * 30 
                    save_data(db)
                    st.success("تم إغلاق الختمة وترحيل الأسماء!")
                    st.rerun()
                else:
                    st.error("الرقم السري خاطئ!")

    with tab_mark: st.info("سيتم تفعيل الخصائص الإضافية لاحقاً.")
    with tab_details: st.info("قريباً.")
    with tab_schedule: st.info("قريباً.")

# ==========================================
# 2. لوحة التحكم المركزية (تظهر عند الدخول للرابط الأساسي)
# ==========================================
else:
    st.title("⚙️ لوحة التحكم المركزية لمدير النظام")
    if st.text_input("كلمة المرور:", type="password") == MASTER_PASSWORD:
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 إعداد الروابط", "➕ إضافة مجموعة", "📝 تعديل الأسماء", "📱 تذكير واتساب"])
        with tab1:
            st.info("انسخ رابط موقعك من أعلى المتصفح (مثال: https://khatma-app.streamlit.app) والصقه هنا.")
            new_url = st.text_input("الرابط الأساسي:", value=BASE_URL)
            if st.button("حفظ الرابط"):
                db["base_url"] = new_url.strip("/")
                save_data(db)
                st.success("تم الحفظ!")
                st.rerun()
            st.write("---")
            if not BASE_URL: st.error("احفظ الرابط بالأعلى لتظهر المجموعات.")
            else:
                for g_id, g_info in db["groups"].items():
                    link = f"{BASE_URL}/?group={g_id}"
                    st.write(f"**{g_info['name']}**")
                    st.code(link, language="text")
                    st.markdown(f"[🔗 دخول مباشر]({link})")
        with tab2:
            g_name = st.text_input("اسم المجموعة:")
            g_pass = st.text_input("كلمة المرور لإغلاق الختمة:")
            r_text = st.text_area("أدخل 30 اسماً:", value="\n".join([f"قارئ {i+1}" for i in range(30)]), height=300)
            if st.button("إنشاء"):
                r_list = [n.strip() for n in r_text.split('\n') if n.strip()]
                if not g_name or not g_pass: st.error("أكمل البيانات")
                elif len(r_list) != 30: st.error(f"يجب إدخال 30 اسم (أدخلت {len(r_list)})")
                else:
                    db["groups"]["group_" + str(uuid.uuid4())[:8]] = {"name": g_name, "password": g_pass, "khatma_count": 0, "parts": ["لم تبدأ"] * 30, "readers": r_list}
                    save_data(db)
                    st.success("تم!")
                    st.rerun()
        with tab3:
            if db["groups"]:
                e_id = st.selectbox("المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                e_text = st.text_area("الأسماء:", value="\n".join(db["groups"][e_id]["readers"]), height=300)
                if st.button("حفظ التعديلات"):
                    e_list = [n.strip() for n in e_text.split('\n') if n.strip()]
                    if len(e_list) == 30:
                        db["groups"][e_id]["readers"] = e_list
                        save_data(db)
                        st.success("تم!")
                        st.rerun()
                    else: st.error("يجب أن يبقى العدد 30.")
        with tab4:
            if db["groups"]:
                w_id = st.selectbox("واتساب للمجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                w_info = db["groups"][w_id]
                msg = [f"📖 *تذكير الأجزاء المتبقية - {w_info['name']}* 📖", "ـــــــــــــــــــ"]
                for i in range(30):
                    p_status = sanitize_status(w_info['parts'][i])
                    if p_status != "تمت التلاوة": 
                        status_note = f" ({p_status})" if p_status != "لم تبدأ" else ""
                        msg.append(f"الجزء {i+1} : {w_info['readers'][i]}{status_note}")
                msg.extend(["ـــــــــــــــــــ", f"{BASE_URL}/?group={w_id}"])
                st.code("\n".join(msg), language="text")
