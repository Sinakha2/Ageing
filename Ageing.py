import streamlit as st
import sqlite3
import random
from datetime import datetime, date
import pandas as pd
import base64

# -------------------------------------------------------------------
# 1. تنظیم پیکربندی صفحه (این اولین دستور برنامه می‌باشد)
st.set_page_config(page_title="Ageing & Health Questionnaire", layout="wide")

# -------------------------------------------------------------------
# 2. تبدیل تصویر به Base64 و تزریق پس‌زمینه با استفاده از CSS به container اصلی (div.block-container)
import streamlit as st

# لینک تصویر به صورت raw از GitHub
image_url = "https://raw.githubusercontent.com/Sinakha2/Ageing/8cba47c2e2ef1f050d6f8415911700c47db8a9ba/photo_2025-05-07_20-13-46.jpg"

page_bg_img = f"""
<style>
div.block-container {{
    position: relative;
    background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.6)),
                url("{image_url}") no-repeat center center fixed;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. CSS سفارشی برای استایل‌دهی عمومی اپلیکیشن، expander header، جداول و بخش پرسشنامه
custom_css = """
<style>
/* General styles */
body {
  background-color: #f8f9fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #343a40;
}
h1, h2, h3, h4, h5 {
  color: #343a40;
}
/* Buttons */
div.stButton > button {
  background-color: #007BFF;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
div.stButton > button:hover {
  background-color: #0056b3;
}
/* Card style */
.card {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
/* RTL container (if needed) */
.rtl {
  direction: rtl;
  text-align: right;
}

/* Custom styling for tabs using Baseweb selectors - smaller tabs */
[data-baseweb="tab"] > div {
  background-color: #ffffff !important;
  color: #007BFF !important;
  border: 1px solid #007BFF;
  border-radius: 8px 8px 0 0;
  margin-right: 4px;
  padding: 4px 8px;
  font-weight: 600;
  cursor: pointer;
}
[data-baseweb="tab"] > div[aria-selected="true"] {
  background-color: #007BFF !important;
  color: #ffffff !important;
  border: 1px solid #007BFF;
}

/* Custom styling for expander header in blue */
[data-testid="stExpander"] > div[role="button"] {
  background-color: #007BFF !important;
  color: #ffffff !important;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 10px;
}

/* Styling for HTML tables rendered for questionnaire responses */
table.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin: 0 auto;
}
table.styled-table th,
table.styled-table td {
    border: 1px solid #dee2e6;
    padding: 10px;
    text-align: left;
}
table.styled-table th {
    background-color: #007BFF;
    color: white;
}
table.styled-table tr:nth-child(even) {
    background-color: #f2f2f2;
}

/* Styling for questionnaire form elements */
div[data-baseweb*="radio"] label {
  font-size: 16px !important;
  font-weight: 500;
  color: #343a40;
  margin-bottom: 8px;
}
div[data-testid="stTextInput"] input {
  font-size: 16px;
  padding: 8px;
}
.stForm label {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 4. توابع مربوط به دیتابیس و SQLite
def init_db():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    national_id TEXT,
                    approved INTEGER,
                    patient_code TEXT,
                    approved_at TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_id INTEGER,
                    Q1 TEXT, Q2 TEXT, Q3 TEXT, Q4 TEXT, Q5 TEXT, Q6 TEXT, Q7 TEXT,
                    Q8 TEXT, Q9 TEXT, Q10 TEXT, Q11 TEXT, Q12 TEXT, Q13 TEXT, Q14 TEXT,
                    Q15 TEXT, Q16 TEXT, Q17 TEXT, Q18 TEXT, Q19 TEXT, Q20 TEXT,
                    Q21 TEXT, Q22 TEXT, Q23 TEXT, Q24 TEXT,
                    Q25 TEXT, Q26 TEXT, Q27 TEXT, Q28 TEXT, Q29 TEXT, Q30 TEXT,
                    Q31 TEXT, Q32 TEXT, Q33 TEXT, Q34 TEXT, Q35 TEXT,
                    FOREIGN KEY(registration_id) REFERENCES registrations(id)
                )''')
    conn.commit()
    conn.close()

def update_schema():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(registrations)")
    cols = [info[1] for info in c.fetchall()]
    if "approved_at" not in cols:
        c.execute("ALTER TABLE registrations ADD COLUMN approved_at TEXT")
        conn.commit()
    conn.close()

def insert_registration(name, email, national_id):
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("INSERT INTO registrations (name, email, national_id, approved, patient_code) VALUES (?, ?, ?, 0, '')",
              (name, email, national_id))
    conn.commit()
    reg_id = c.lastrowid
    conn.close()
    return reg_id

def get_registration(email, national_id, patient_code):
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute(
        "SELECT id, name, email, national_id, approved, patient_code, approved_at FROM registrations WHERE email=? AND national_id=? AND patient_code=? AND approved=1",
        (email, national_id, patient_code))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "national_id": row[3],
                "approved": row[4], "patient_code": row[5], "approved_at": row[6]}
    else:
        return None

def get_all_registrations():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("SELECT id, name, email, national_id, approved, patient_code, approved_at FROM registrations")
    rows = c.fetchall()
    conn.close()
    regs = []
    for row in rows:
        regs.append({"id": row[0],
                     "name": row[1],
                     "email": row[2],
                     "national_id": row[3],
                     "approved": row[4],
                     "patient_code": row[5],
                     "approved_at": row[6]})
    return regs

def approve_registration(reg_id, patient_code):
    approved_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("UPDATE registrations SET approved=1, patient_code=?, approved_at=? WHERE id=?",
              (patient_code, approved_time, reg_id))
    conn.commit()
    conn.close()

def insert_response(registration_id, responses):
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    keys = ["Q" + str(i) for i in range(1, 36)]
    values = [responses.get(key, "") for key in keys]
    query = "INSERT INTO responses (registration_id, " + ", ".join(keys) + ") VALUES (?, " + ", ".join(["?"] * 35) + ")"
    c.execute(query, (registration_id, *values))
    conn.commit()
    conn.close()

def get_all_responses():
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("""
    SELECT reg.name, reg.email, reg.national_id, reg.patient_code,
           r.Q1, r.Q2, r.Q3, r.Q4, r.Q5, r.Q6, r.Q7, r.Q8, r.Q9, r.Q10,
           r.Q11, r.Q12, r.Q13, r.Q14, r.Q15, r.Q16, r.Q17, r.Q18, r.Q19, r.Q20,
           r.Q21, r.Q22, r.Q23, r.Q24, r.Q25, r.Q26, r.Q27, r.Q28, r.Q29,
           r.Q30, r.Q31, r.Q32, r.Q33, r.Q34, r.Q35
    FROM responses r JOIN registrations reg ON r.registration_id = reg.id
    """)
    rows = c.fetchall()
    conn.close()
    res_list = []
    for row in rows:
        entry = {"Patient Name": row[0],
                 "Patient Email": row[1],
                 "National ID": row[2],
                 "Patient Code": row[3]}
        for i in range(1, 36):
            entry["Q" + str(i)] = row[3 + i]
        res_list.append(entry)
    return res_list

def delete_patient(reg_id):
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("DELETE FROM registrations WHERE id=?", (reg_id,))
    c.execute("DELETE FROM responses WHERE registration_id=?", (reg_id,))
    conn.commit()
    conn.close()

def has_response(registration_id):
    conn = sqlite3.connect("patients.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM responses WHERE registration_id=?", (registration_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

# -------------------------------------------------------------------
# 5. راه‌اندازی و به‌روزرسانی ساختار (Schema) دیتابیس
init_db()
update_schema()

# -------------------------------------------------------------------
# 6. مقداردهی اولیه به session_state
if "current_patient" not in st.session_state:
    st.session_state.current_patient = None
if "patient_logged_in" not in st.session_state:
    st.session_state.patient_logged_in = False
if "language" not in st.session_state:
    st.session_state.language = "English"  # زبان پیش‌فرض
if "dashboard" not in st.session_state:
    st.session_state.dashboard = "Patient Dashboard"
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# -------------------------------------------------------------------
# 7. انتخاب داشبورد از طریق سایدبار
col1_side, col2_side = st.sidebar.columns(2)
if col1_side.button("Patient Dashboard"):
    st.session_state.dashboard = "Patient Dashboard"
if col2_side.button("Hospital Dashboard"):
    st.session_state.dashboard = "Hospital Dashboard"

# -------------------------------------------------------------------
# 8. توابع رندر داشبورد

def get_text(key):
    translations = {
        "select_language": {"English": "Select Language:", "فارسی": "انتخاب زبان:"},
        "select_action": {"English": "Select Action:", "فارسی": "انتخاب عمل:"},
        "register_subheader": {"English": "Register as Patient", "فارسی": "ثبت نام به عنوان بیمار"},
        "login_subheader": {"English": "Login to Access Questionnaire", "فارسی": "ورود به پرسشنامه"},
        "patient_name": {"English": "Patient Name:", "فارسی": "نام بیمار:"},
        "patient_email": {"English": "Patient Email:", "فارسی": "ایمیل بیمار:"},
        "national_id": {"English": "National ID:", "فارسی": "کد ملی:"},
        "submit_registration": {"English": "Submit Registration", "فارسی": "ارسال ثبت نام"},
        "enter_email": {"English": "Enter your Email:", "فارسی": "ایمیل خود را وارد کنید:"},
        "enter_national_id": {"English": "Enter your National ID:", "فارسی": "کد ملی خود را وارد کنید:"},
        "enter_patient_code": {"English": "Enter your Patient Code:", "فارسی": "کد بیمار خود را وارد کنید:"},
        "login": {"English": "Login", "فارسی": "ورود"}
    }
    return translations.get(key, {}).get(st.session_state.language, "")


def render_patient_dashboard():
    st.header("Patient Dashboard")
    
    # انتخاب زبان قبل از هرگونه ثبت‌نام/ورود؛ این انتخاب زبان برای فرم‌ها و پرسشنامه اعمال خواهد شد.
    language_choice = st.radio("Select Language:", options=["English", "فارسی"], index=0, key="lang_toggle")
    st.session_state.language = language_choice

    # انتخاب حالت (ثبت‌نام یا ورود) با استفاده از ترجمه‌ها
    mode = st.radio(get_text("select_action"), 
                    options=[get_text("register_subheader"), get_text("login_subheader")],
                    index=0, key="patient_mode")
                    
    if mode == get_text("register_subheader"):
        st.subheader(get_text("register_subheader"))
        reg_name = st.text_input(get_text("patient_name"), key="reg_name")
        reg_email = st.text_input(get_text("patient_email"), key="reg_email")
        reg_nid = st.text_input(get_text("national_id"), key="reg_nid")
        
        if st.button(get_text("submit_registration"), key="btn_register"):
            if reg_name and reg_email and reg_nid:
                if not (reg_nid.isdigit() and len(reg_nid) == 10):
                    st.error("کد ملی باید دقیقا 10 رقم و تنها شامل ارقام باشد.")
                else:
                    # عملیات بررسی تکراری بودن در دیتابیس (کد مربوط به DB حفظ می‌شود)
                    conn = sqlite3.connect("patients.db")
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM registrations WHERE national_id=?", (reg_nid,))
                    nid_count = c.fetchone()[0]
                    c.execute("SELECT COUNT(*) FROM registrations WHERE email=?", (reg_email,))
                    email_count = c.fetchone()[0]
                    conn.close()
                    if nid_count > 0:
                        st.error("کد ملی وارد شده قبلاً ثبت شده است. لطفاً کد ملی دیگری وارد کنید.")
                    elif email_count > 0:
                        st.error("ایمیل وارد شده قبلاً ثبت شده است. لطفاً ایمیل دیگری وارد کنید.")
                    else:
                        insert_registration(reg_name, reg_email, reg_nid)
                        st.success("درخواست ثبت نام ارسال شد. لطفاً منتظر تایید بیمارستان باشید.\nیک کد 8 رقمی به ایمیل شما ارسال خواهد شد.")
            else:
                st.error("لطفاً تمامی فیلدها را تکمیل کنید.")
    else:
        st.subheader(get_text("login_subheader"))
        login_email = st.text_input(get_text("enter_email"), key="login_email")
        login_nid = st.text_input(get_text("enter_national_id"), key="login_nid")
        login_code = st.text_input(get_text("enter_patient_code"), key="login_code")
        if st.button(get_text("login"), key="btn_login"):
            reg = get_registration(login_email, login_nid, login_code)
            if reg:
                st.session_state.patient_logged_in = True
                st.session_state.current_patient = reg
                st.success("Login successful! You may now access the questionnaire.")
            else:
                st.error("Login details do not match or registration not approved.")
    
    if st.session_state.patient_logged_in:
        st.header("Questionnaire Form")
        if has_response(st.session_state.current_patient["id"]) or st.session_state.submitted:
            st.info("You have already submitted your questionnaire. Thank you!")
        else:
            st.info("Selected Language: " + st.session_state.language)
            # استفاده از همان زبان انتخاب شده؛ نیازی به انتخاب مجدد نیست.
            with st.form("questionnaire_form"):
                if st.session_state.language == "English":
                    agree_scale = ["Strongly disagree", "Disagree", "Uncertain", "Agree", "Strongly agree"]
                    truth_scale = ["Not at all true", "Slightly true", "Moderately true", "Very true", "Extremely true"]
                    
                    st.subheader("Part 1: Attitudes to Ageing Questions")
                    q1 = st.radio("1. As people get older, they are better able to cope with life.", agree_scale, index=2)
                    q2 = st.radio("2. It is a privilege to grow old.", agree_scale, index=2)
                    q3 = st.radio("3. Old age is a time of loneliness.", agree_scale, index=2)
                    q4 = st.radio("4. Wisdom comes with age.", agree_scale, index=2)
                    q5 = st.radio("5. There are many pleasant things about growing older.", agree_scale, index=2)
                    q6 = st.radio("6. Old age is a depressing time of life.", agree_scale, index=2)
                    q7 = st.radio("7. It is important to take exercise at any age.", agree_scale, index=2)
                    
                    st.subheader("Part 1 (continued): Attitudes to Ageing Questions")
                    q8  = st.radio("8. Growing older has been easier than I thought.", truth_scale, index=2)
                    q9  = st.radio("9. I find it more difficult to talk about my feelings as I get older.", truth_scale, index=2)
                    q10 = st.radio("10. I am more accepting of myself as I have grown older.", truth_scale, index=2)
                    q11 = st.radio("11. I don't feel old.", truth_scale, index=2)
                    q12 = st.radio("12. I see old age mainly as a time of loss.", truth_scale, index=2)
                    q13 = st.radio("13. My identity is not defined by my age.", truth_scale, index=2)
                    q14 = st.radio("14. I have more energy now than I expected for my age.", truth_scale, index=2)
                    q15 = st.radio("15. I am losing my physical independence as I get older.", truth_scale, index=2)
                    q16 = st.radio("16. Problems with my physical health do not hold me back from doing what I want to.", truth_scale, index=2)
                    q17 = st.radio("17. As I get older, I find it more difficult to make new friends.", truth_scale, index=2)
                    q18 = st.radio("18. It is very important to pass on the benefits of my experiences to younger people.", truth_scale, index=2)
                    q19 = st.radio("19. I believe my life has made a difference.", truth_scale, index=2)
                    q20 = st.radio("20. I don't feel involved in society now that I am older.", truth_scale, index=2)
                    q21 = st.radio("21. I want to give a good example to younger people.", truth_scale, index=2)
                    q22 = st.radio("22. I feel excluded from things because of my age.", truth_scale, index=2)
                    q23 = st.radio("23. My health is better than I expected for my age.", truth_scale, index=2)
                    q24 = st.radio("24. I keep myself as fit and active as possible by exercising.", truth_scale, index=2)
                    
                    st.subheader("Part 2: Additional Health Questions")
                    q25 = st.text_input("25. Do you currently take any medications? If yes, which ones?")
                    q26 = st.text_input("26. Do you have any chronic illnesses? If yes, since when?")
                    q27 = st.text_input("27. Do you require any mobility aids (e.g., cane, walker, etc.)?")
                    q28 = st.radio("28. Are you independent in carrying out daily activities?", ("Yes", "No"))
                    q29 = st.radio("29. Do you use any hearing assistive devices (e.g., hearing aids)?", ("Yes", "No"))
                    q30 = st.date_input("30. When was the last time you had a comprehensive test? (Select a date)", key="q30")
                    q31 = st.text_input("31. What were the results of the test?")
                    q32 = st.radio("32. Are you under the care of a family physician?", ("Yes", "No"))
                    q33 = st.text_input("33. When was your last visit to the doctor?")
                    q34 = st.text_input("34. Do you live alone, or do you have family members around?")
                    q35 = st.radio("35. Do you engage in daily exercise or walking?", ("Yes", "No"))
                else:
                    agree_scale_fa = ["کاملاً مخالفم", "مخالفم", "بی‌طرف", "موافقم", "کاملاً موافقم"]
                    truth_scale_fa = ["اصلاً درست نیست", "کمی درست است", "تا حدودی درست است", "بسیار درست است", "کاملاً درست است"]
                    
                    st.subheader("بخش 1: سوالات نگرش به پیری")
                    q1 = st.radio("1. با پیر شدن، افراد بهتر می‌توانند با مشکلات زندگی کنار بیایند.", agree_scale_fa, index=2)
                    q2 = st.radio("2. پیر شدن یک امتیاز است.", agree_scale_fa, index=2)
                    q3 = st.radio("3. پیری زمانی از تنهایی است.", agree_scale_fa, index=2)
                    q4 = st.radio("4. خرد با سن همراه است.", agree_scale_fa, index=2)
                    q5 = st.radio("5. چیزهای خوشایندی در پیر شدن وجود دارد.", agree_scale_fa, index=2)
                    q6 = st.radio("6. پیری زمانی افسرده‌کننده است.", agree_scale_fa, index=2)
                    q7 = st.radio("7. انجام تمرین ورزشی در هر سنی مهم است.", agree_scale_fa, index=2)
                    
                    st.subheader("بخش 1 (ادامه): سوالات نگرش به پیری")
                    q8  = st.radio("8. پیر شدن برای من آسان‌تر از آنچه تصور می‌کردم بوده است.", truth_scale_fa, index=2)
                    q9  = st.radio("9. بیان احساسات در سنین بالا برایم دشوارتر شده است.", truth_scale_fa, index=2)
                    q10 = st.radio("10. با گذشت زمان به خودم پذیراتر شده‌ام.", truth_scale_fa, index=2)
                    q11 = st.radio("11. احساس پیری نمی‌کنم.", truth_scale_fa, index=2)
                    q12 = st.radio("12. پیری را عمدتاً زمانی از دست دادن می‌بینم.", truth_scale_fa, index=2)
                    q13 = st.radio("13. هویت من تنها به سن من محدود نمی‌شود.", truth_scale_fa, index=2)
                    q14 = st.radio("14. انرژی بیشتری نسبت به انتظارات سنی دارم.", truth_scale_fa, index=2)
                    q15 = st.radio("15. استقلال فیزیکی‌ام در حال کاهش است.", truth_scale_fa, index=2)
                    q16 = st.radio("16. مشکلات جسمی جلوی فعالیت‌های من را نمی‌گیرد.", truth_scale_fa, index=2)
                    q17 = st.radio("17. در پیری، یافتن دوستان جدید برایم سخت‌تر شده است.", truth_scale_fa, index=2)
                    q18 = st.radio("18. انتقال تجربیات به نسلی جوانتر برایم بسیار مهم است.", truth_scale_fa, index=2)
                    q19 = st.radio("19. معتقدم زندگی‌ام تفاوت ایجاد کرده است.", truth_scale_fa, index=2)
                    q20 = st.radio("20. به عنوان یک فرد مسن، احساس می‌کنم در جامعه دخالتی ندارم.", truth_scale_fa, index=2)
                    q21 = st.radio("21. می‌خواهم برای افراد جوان مثال خوبی باشم.", truth_scale_fa, index=2)
                    q22 = st.radio("22. به دلیل سنم از فعالیت‌ها کنار گذاشته شده است.", truth_scale_fa, index=2)
                    q23 = st.radio("23. سلامت من از انتظارات سنی بهتر است.", truth_scale_fa, index=2)
                    q24 = st.radio("24. خودم را تا جایی که شده فعال نگه می‌دارم.", truth_scale_fa, index=2)
                    
                    st.subheader("بخش 2: سوالات اضافی سلامت")
                    q25 = st.text_input("25. آیا در حال حاضر دارو مصرف می‌کنید؟ در صورت بله، کدام‌ها؟")
                    q26 = st.text_input("26. آیا بیماری مزمنی دارید؟ در صورت بله، از کی؟")
                    q27 = st.text_input("27. آیا از کمک‌های حرکتی (مانند عصا) استفاده می‌کنید؟")
                    q28 = st.radio("28. آیا در انجام فعالیت‌های روزانه مستقل هستید؟", ("بله", "خیر"))
                    q29 = st.radio("29. آیا از دستگاه‌های کمکی شنوایی استفاده می‌کنید؟", ("بله", "خیر"))
                    q30 = st.date_input("30. آخرین بار چه زمانی تست جامعی انجام دادید؟", key="q30")
                    q31 = st.text_input("31. نتایج تست چه بود؟")
                    q32 = st.radio("32. آیا تحت نظر پزشک خانواده هستید؟", ("بله", "خیر"))
                    q33 = st.text_input("33. آخرین باری که به پزشک مراجعه کردید چه زمانی بود؟")
                    q34 = st.text_input("34. آیا به تنهایی زندگی می‌کنید یا خانواده دارید؟")
                    q35 = st.radio("35. آیا روزانه فعالیت ورزشی انجام می‌دهید؟", ("بله", "خیر"))
                submitted = st.form_submit_button("Submit Responses")
                if submitted:
                    responses_obj = {
                        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5, "Q6": q6, "Q7": q7,
                        "Q8": q8, "Q9": q9, "Q10": q10, "Q11": q11, "Q12": q12, "Q13": q13, "Q14": q14,
                        "Q15": q15, "Q16": q16, "Q17": q17, "Q18": q18, "Q19": q19, "Q20": q20,
                        "Q21": q21, "Q22": q22, "Q23": q23, "Q24": q24, "Q25": q25, "Q26": q26,
                        "Q27": q27, "Q28": q28, "Q29": q29, "Q30": str(q30), "Q31": q31, "Q32": q32,
                        "Q33": q33, "Q34": q34, "Q35": q35
                    }
                    insert_response(st.session_state.current_patient["id"], responses_obj)
                    st.success("Questionnaire submitted successfully.")
                    st.session_state.submitted = True

def render_hospital_dashboard():
    st.header("Hospital Dashboard")
    # این قسمت در بیمارستان ثابت است؛ نیازی به تغییر زبان ندارد.
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Pending Registrations", 
        "Approved Registrations", 
        "Complete Data Table", 
        "Search & Delete Patients", 
        "Questionnaire Responses"
    ])
    
    with tab1:
        st.subheader("Pending Registrations")
        regs = get_all_registrations()
        pending_regs = [reg for reg in regs if reg["approved"] == 0]
        if pending_regs:
            for reg in pending_regs:
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                      <p><strong>Name:</strong> {reg["name"]}</p>
                      <p><strong>Email:</strong> {reg["email"]}</p>
                      <p><strong>National ID:</strong> {reg["national_id"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    col1_pending, col2_pending = st.columns(2)
                    if col1_pending.button("Approve Request", key=f"approve_{reg['id']}"):
                        code = str(random.randint(10000000, 99999999))
                        approve_registration(reg["id"], code)
                        st.success(f"Registration approved! Patient Code: {code}")
                    if col2_pending.button("Deny Request", key=f"deny_{reg['id']}"):
                        delete_patient(reg["id"])
                        st.success("Registration denied and removed.")
        else:
            st.info("No pending registrations.")
    
    with tab2:
        st.subheader("Approved Registrations")
        regs = get_all_registrations()
        approved_regs = [reg for reg in regs if reg["approved"] == 1]
        if approved_regs:
            for reg in approved_regs:
                st.markdown(f"""
                <div class="card">
                  <p><strong>Name:</strong> {reg["name"]}</p>
                  <p><strong>Email:</strong> {reg["email"]}</p>
                  <p><strong>National ID:</strong> {reg["national_id"]}</p>
                  <p><strong>Patient Code:</strong> {reg["patient_code"]}</p>
                  <p><strong>Approved At:</strong> {reg["approved_at"] if reg["approved_at"] else ""}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No approved registrations yet.")
    
    with tab3:
        st.subheader("Complete Patient Data Table")
        regs = get_all_registrations()
        if regs:
            display_data = pd.DataFrame(regs)[["name", "email", "national_id", "patient_code", "approved_at"]]
            display_data.index = display_data.index + 1
            st.dataframe(display_data)
        else:
            st.info("No patient data available yet.")
    
    with tab4:
        st.subheader("Search & Delete Patients")
        search_query = st.text_input("Search Patient (by Name, Email, or National ID):", key="search_patient")
        regs = get_all_registrations()
        if search_query:
            filtered_regs = [
                reg for reg in regs
                if search_query.lower() in reg["name"].lower() 
                   or search_query.lower() in reg["email"].lower() 
                   or search_query.lower() in reg["national_id"].lower()
            ]
        else:
            filtered_regs = regs
        if filtered_regs:
            search_data = pd.DataFrame(filtered_regs)[["name", "email", "national_id", "patient_code", "approved_at"]]
            search_data.index = search_data.index + 1
            st.dataframe(search_data)
            delete_options = {f"{reg['id']} - {reg['name']}": reg['id'] for reg in filtered_regs}
            selected = st.multiselect("Select patients to delete:", list(delete_options.keys()))
            if st.button("Delete Selected Patients"):
                for key in selected:
                    delete_patient(delete_options[key])
                st.success("Selected patients have been deleted.")
        else:
            st.info("No patients found matching your search.")
    
    with tab5:
        st.subheader("Questionnaire Responses")
        search_resp = st.text_input("Search Responses (by Name, Email, or National ID):", key="search_response")
        responses = get_all_responses()
        if search_resp:
            responses = [resp for resp in responses if search_resp.lower() in resp.get("Patient Name", "").lower()
                         or search_resp.lower() in resp.get("Patient Email", "").lower()
                         or search_resp.lower() in resp.get("National ID", "").lower()]
        if responses:
            for resp in responses:
                patient_name = resp.get("Patient Name", "Unknown")
                patient_code = resp.get("Patient Code", "")
                national_id = resp.get("National ID", "Unknown")
                # استفاده از رشته ساده برای عنوان expander
                title = f"Patient: {patient_name} | Code: {patient_code} | National ID: {national_id}"
                with st.expander(title, expanded=False):
                    data = [(f"Q{i}", resp.get("Q" + str(i), "No answer")) for i in range(1, 36)]
                    df_questions = pd.DataFrame(data, columns=["Question", "Answer"])
                    df_questions.index = range(1, len(df_questions) + 1)
                    html_table = df_questions.to_html(classes="styled-table", index=False)
                    st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("No questionnaire responses recorded.")

# -------------------------------------------------------------------
# 9. رندر داشبورد براساس انتخاب کاربر
if st.session_state.dashboard == "Patient Dashboard":
    render_patient_dashboard()
else:
    render_hospital_dashboard()


def __wm_func():
    # این تابع جهت watermarking کد است؛
    # تغییر ندهید: S3cr3t: SinaKhademi_2025_AgeingHealthApp_4570180991
    return "SinaKhademi_2025_AgeingHealthApp_4570180991"




