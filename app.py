import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 

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
    .dashboard-card * { text-align: center !important; }

    div[data-testid="stMarkdownContainer"] > p { margin-bottom: 0px; }
    div[data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] { gap: 10px; }
    
    div[data-testid="stHorizontalBlock"]:has(.gray-bg) {
        background-color: rgba(130, 130, 130, 0.08); 
        padding-top: 10px;
        padding-bottom: 5px;
        padding-right: 15px;
        border-radius: 10px;
        margin-bottom: 5px;
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

def sanitize_status(status):
    if status is True or status == "تمت القراءة": return "تمت التلاوة"
    if status is False or status == "جاري القراءة": return "لم تبدأ"
    if status not in STATUS_OPTIONS: return "لم تبدأ"
    return status

def render_status_label(status, name, strike=False):
    if strike and status == "تمت التلاوة":
        name_html = f"<span style='color: #888; text-decoration: line-through;'>{name}</span>"
    else:
        name_html = f"<span style='font-weight: bold;'>{name}</span>"
        
    if status == "تمت التلاوة":
        sub = "<small style='color: #277953; font-weight: bold;'>🟩🟩🟩🟩 تمت التلاوة</small>"
    elif status == "حزب ونص":
        sub = "<small style='color: #d4a32a; font-weight: bold;'>🟩🟩🟩⬜ حزب ونص</small>"
    elif status == "حزب":
        sub = "<small style='color: #a47e1b; font-weight: bold;'>🟩🟩⬜⬜ حزب</small>"
    elif status == "نص جزء":
        sub = "<small style='color: #e67e22; font-weight: bold;'>🟩⬜⬜⬜ نص جزء</small>"
    else:
        sub = "<small style='color: #888;'>⬜⬜⬜⬜ لم يبدأ بعد</small>"
        
    return f"<div style='line-height: 1.4;'>{name_html}<br>{sub}</div>"

def get_wa_status_text(status):
    if status == "حزب ونص": return " 🟩🟩🟩⬜ (حزب ونص)"
    elif status == "حزب": return " 🟩🟩⬜⬜ (حزب)"
    elif status == "نص جزء": return " 🟩⬜⬜⬜ (نص جزء)"
    elif status == "لم تبدأ": return " ⬜⬜⬜⬜ (لم يبدأ)"
    return ""

db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# 1. واجهة المشاركين 
# ==========================================
if "group" in query_params and query_params["group"] in db["groups"]:
    group_id = query_params["group"]
    group_data = db["groups"][group_id]
    
    def update_part_status(part_index, source_key):
        new_status = st.session_state[source_key]
        
        if "last_updates" not in group_data:
            group_data["last_updates"] = {}
            
        now_dt = datetime.datetime.now()
        now_time = now_dt.strftime("%Y-%m-%d  %I:%M %p")
        
        group_data["last_updates"][str(part_index)] = {
            "time": now_time,
            "timestamp": now_dt.timestamp()
        }

        group_data['parts'][part_index] = new_status
        save_data(db)
        
        other_key = f"late_s_{part_index}" if source_key.startswith("s_") else f"s_{part_index}"
        if other_key in st.session_state:
            st.session_state[other_key] = new_status
    
    progress_weights = {
        "لم تبدأ": 0.0,
        "نص جزء": 0.25,
        "حزب": 0.50,
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

    tab_overview, tab_mark, tab_details, tab_schedule = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة", "📖 تفاصيل", "📅 الخطة"])

    with tab_overview:
        for i in range(30):
            col1, col2, col3, col4 = st.columns([1, 2, 6, 1])
            current_status = sanitize_status(group_data['parts'][i])
            bg_span = '<span class="gray-bg"></span>' if i % 2 == 0 else ''
            
            with col1:
                if current_status == "تمت التلاوة":
                    st.markdown(f"{bg_span}<s style='color: #888;'>الجزء {i+1}</s>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{bg_span}**الجزء {i+1}**", unsafe_allow_html=True)
            
            with col2: 
                st.markdown(render_status_label(current_status, group_data['readers'][i], strike=True), unsafe_allow_html=True)
                
            with col3:
                st.radio(
                    f"الحالة_{i}", 
                    STATUS_OPTIONS, 
                    index=STATUS_OPTIONS.index(current_status), 
                    key=f"s_{i}", 
                    horizontal=True,
                    label_visibility="collapsed",
                    on_change=update_part_status,
                    args=(i, f"s_{i}")
                )
                    
            with col4:
                if current_status == "تمت التلاوة":
                    st.markdown("<span style='color: #277953; font-weight: bold;'>✅ مكتمل</span>", unsafe_allow_html=True)
                else:
                    st.write("")
                    
        st.write("---")
        if completed_parts == 30.0:
            pwd = st.text_input("كلمة المرور لإغلاق الختمة وترحيل الأسماء:", type="password")
            if st.button("إغلاق الختمة"):
                if pwd == group_data["password"]:
                    group_data["khatma_count"] = group_data.get("khatma_count", 0) + 1
                    readers = group_data["readers"]
                    group_data["readers"] = [readers[-1]] + readers[:-1] 
                    group_data["parts"] = ["لم تبدأ"] * 30 
                    group_data["last_updates"] = {} 
                    save_data(db)
                    st.success("تم إغلاق الختمة وترحيل الأسماء!")
                    st.rerun()
                else:
                    st.error("الرقم السري خاطئ!")

    with tab_mark:
        st.write("### ⏳ القراء الذين لم يكملوا التلاوة")
        has_incomplete = False
        display_counter = 0 
        
        for i in range(30):
            current_status = sanitize_status(group_data['parts'][i])
            
            if current_status != "تمت التلاوة":
                has_incomplete = True
                col1_m, col2_m, col3_m = st.columns([1, 2, 7])
                
                with col1_m:
                    if display_counter % 2 == 0:
                        st.markdown(f'<span class="gray-bg"></span>**الجزء {i+1}**', unsafe_allow_html=True)
                    else:
                        st.write(f"**الجزء {i+1}**")
                
                with col2_m: 
                    st.markdown(render_status_label(current_status, group_data['readers'][i], strike=False), unsafe_allow_html=True)
                
                with col3_m:
                    st.radio(
                        f"الحالة_متأخر_{i}", 
                        STATUS_OPTIONS, 
                        index=STATUS_OPTIONS.index(current_status), 
                        key=f"late_s_{i}", 
                        horizontal=True,
                        label_visibility="collapsed",
                        on_change=update_part_status,
                        args=(i, f"late_s_{i}")
                    )
                
                display_counter += 1
                
        if not has_incomplete:
            st.success("🎉 ما شاء الله! جميع القراء أتموا تلاوتهم بنجاح.")

    with tab_details: 
        st.write("### ⏳ أحدث القراء تفاعلاً (غير المكتملين بعد)")
        
        incomplete_list = []
        last_updates_dict = group_data.get("last_updates", {})
        
        for i in range(30):
            p_status = sanitize_status(group_data['parts'][i])
            if p_status != "تمت التلاوة":
                part_update = last_updates_dict.get(str(i), {})
                time_str = "لم يُحدّث في هذه الختمة بعد"
                timestamp = 0
                
                if isinstance(part_update, dict):
                    time_str = part_update.get("time", "لم يُحدّث في هذه الختمة بعد")
                    timestamp = part_update.get("timestamp", 0)
                    
                incomplete_list.append({
                    "reader": group_data['readers'][i],
                    "part": i + 1,
                    "status": p_status,
                    "time": time_str,
                    "timestamp": timestamp
                })
        
        if not incomplete_list:
            st.success("🎉 ما شاء الله! جميع القراء أتموا تلاوتهم بنجاح ولا توجد أجزاء متأخرة.")
        else:
            sorted_incomplete = sorted(incomplete_list, key=lambda x: x["timestamp"], reverse=True)
            last_5_late = sorted_incomplete[:5]
            
            for idx, item in enumerate(last_5_late):
                status_color = "#e67e22" if item['status'] != "لم تبدأ" else "#888"
                
                st.markdown(f"""
                <div style='padding: 12px 15px; background-color: rgba(130, 130, 130, 0.08); border-radius: 8px; margin-bottom: 10px; border-right: 4px solid {status_color}; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.1rem; font-weight: bold;'>{idx + 1}. {item['reader']}</span> 
                        <span style='color: {status_color}; font-weight: bold; margin-right: 15px;'>(الجزء {item['part']})</span>
                        <span style='color: #666; font-size: 0.95rem; margin-right: 15px;'>الحالة: <b>{item['status']}</b></span>
                    </div>
                    <div style='color: #888; font-size: 0.9rem;'>
                        📅 {item['time']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    with tab_schedule: st.info("قريباً.")

# ==========================================
# 2. لوحة التحكم المركزية 
# ==========================================
else:
    st.title("⚙️ لوحة التحكم المركزية لمدير النظام")
    admin_login = st.text_input("كلمة المرور:", type="password")
    
    if admin_login == MASTER_PASSWORD:
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 إعداد الروابط", "➕ إضافة مجموعة", "📝 تعديل الأسماء", "📱 تذكير ومتابعة القراء"])
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
                    db["groups"]["group_" + str(uuid.uuid4())[:8]] = {"name": g_name, "password": g_pass, "khatma_count": 0, "parts": ["لم تبدأ"] * 30, "readers": r_list, "last_updates": {}}
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
                w_id = st.selectbox("اختر المجموعة لمتابعة تقدم قرائها وتذكيرهم:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                w_info = db["groups"][w_id]
                
                # طبقة الحماية الجديدة: طلب كلمة مرور المجموعة لفتح القسم
                st.write("---")
                group_pass_input = st.text_input(f"🔒 يرجى إدخال كلمة مرور مجموعة ({w_info['name']}) لعرض التفاصيل وإرسال التذكيرات:", type="password", key=f"pass_check_{w_id}")
                
                if group_pass_input == w_info["password"]:
                    st.write("### ⏳ القراء المتأخرون حالياً وتفاصيل تقدمهم")
                    has_remaining = False
                    
                    for i in range(30):
                        p_status = sanitize_status(w_info['parts'][i])
                        if p_status != "تمت التلاوة":
                            has_remaining = True
                            col1_adm, col2_adm, col3_adm = st.columns([2, 2, 1])
                            with col1_adm:
                                st.write(f"**الجزء {i+1}**: {w_info['readers'][i]}")
                            with col2_adm:
                                st.write(f"التقدم الحالي: `{p_status}`")
                            with col3_adm:
                                app_link_to_use = BASE_URL if BASE_URL else "الرابط_غير_متوفر"
                                indiv_msg = f"السلام عليكم\nتذكير بقراءة *الجزء {i+1}*\nالقارئ: *{w_info['readers'][i]}*\nالتقدم الحالي: *{p_status}*\nرابط تسجيل التقدم أو الإتمام المباشر:\n{app_link_to_use}/?group={w_id}"
                                st.link_button("📱 تذكير", f"https://wa.me/?text={urllib.parse.quote(indiv_msg)}", key=f"indiv_wa_{i}")
                    
                    if not has_remaining:
                        st.success("🎉 ما شاء الله! اكتملت قراءة جميع الأجزاء الـ 30 في هذه المجموعة.")
                    
                    st.write("---")
                    st.write("### 📱 التذكير الجماعي (رسالة واحدة مجمعة بالكامل للقروب)")
                    
                    app_link_to_use = BASE_URL if BASE_URL else "الرابط_غير_متوفر"
                    group_link = f"{app_link_to_use}/?group={w_id}"
                    
                    msg = [f"📖 *تذكير الأجزاء المتبقية - {w_info['name']}* 📖", "ـــــــــــــــــــ"]
                    for i in range(30):
                        p_status = sanitize_status(w_info['parts'][i])
                        if p_status != "تمت التلاوة": 
                            status_note = get_wa_status_text(p_status)
                            msg.append(f"الجزء {i+1} : {w_info['readers'][i]}{status_note}")
                    
                    if not has_remaining:
                        msg.append("🎉 اكتملت قراءة جميع الأجزاء بفضل الله!")
                    
                    msg.extend(["ـــــــــــــــــــ", "🔗 *رابط التسجيل المباشر:*", group_link])
                    whatsapp_text = "\n".join(msg)
                    
                    st.link_button("📱 إرسال التذكير الجماعي الموحد بالواتساب", f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}", use_container_width=True)
                    
                    st.write("أو يمكنك نسخ نص الرسالة يدوياً من المربع أدناه:")
                    st.code(whatsapp_text, language="text")
                    
                elif group_pass_input != "":
                    st.error("كلمة مرور المجموعة غير صحيحة! لا يمكنك عرض بيانات هذه المجموعة.")
            else:
                st.info("لا توجد مجموعات مسجلة حالياً.")
                
    elif admin_login != "":
        st.error("كلمة المرور خاطئة!")
