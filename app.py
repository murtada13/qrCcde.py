import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
import qrcode
from io import BytesIO
import base64
import webbrowser
import threading

app = Flask(__name__)  # تصحيح هنا
app.secret_key = 'your_secret_key'  # مفتاح سري لحماية الجلسات

# الاتصال بقاعدة البيانات
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # تأكد من أن اسم المستخدم وكلمة المرور مناسبين
        password='',  # تأكد من أن كلمة المرور صحيحة
        database='project_parcode'
    )

# الصفحة الافتراضية توجّه المستخدم إلى صفحة تسجيل الدخول
@app.route('/')
def home():
    return redirect(url_for('1'))

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  
        password = request.form.get('password')

        if not email or not password:
            flash('يرجى إدخال البريد الإلكتروني وكلمة المرور', 'danger')
            return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id_u, email, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and user[2] == password:
            session['logged_in'] = True
            session['id_u'] = user[0]  # تخزين id_u في الجلسة
            session['email'] = user[1]

            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('index'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# الصفحة الرئيسية
@app.route('/index')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email = session.get('email')
    user_id = session.get('id_u')  # استخدام id_u من الجلسة
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name_student, deap, barcode FROM student WHERE id_s = %s', (user_id,))  # جلب بيانات الطالب باستخدام id_u
    student_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if student_data:
        name, department, barcode = student_data
    else:
        name = department = barcode = "لا توجد بيانات متاحة"

    qr_base64 = None
    if barcode != "لا توجد بيانات متاحة":
        barcode_with_link = f"https://2ly.link/216Zh?code={barcode}"  # الرابط المعدل
        qr = qrcode.make(barcode_with_link)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return render_template('index.html', email=email, name=name, department=department, barcode=barcode, qr_code=qr_base64)

# صفحة الملف الشخصي
@app.route('/profile')
def profile():
    if 'logged_in' not in session:
        return redirect(url_for('profile'
        ''))

    email = session.get('email')
    user_id = session.get('id_u')  # استخدام id_u من الجلسة
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب بيانات الطالب مع رقم الهاتف والعنوان من جدول student باستخدام id_u
    cursor.execute('SELECT name_student, deap, barcode, phone, address, collage FROM student WHERE id_s = %s', (user_id,))
    student_data = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if student_data:
        name, department, barcode, phone, address, collage = student_data  # تم إضافة العنوان
    else:
        name = department = barcode = phone = address = collage = "غير متاح"

    qr_base64 = None
    if barcode != "غير متاح":
        barcode_with_link = f"https://2ly.link/216Zh?code={barcode}"  # الرابط المعدل
        qr = qrcode.make(barcode_with_link)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # إرسال البيانات إلى القالب
    return render_template('profile.html', email=email, name=name, department=department, barcode=barcode, phone=phone, address=address, qr_code=qr_base64, collage=collage)

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('login'))

# فتح المتصفح تلقائيًا
def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == '__main__':  # تصحيح هنا
    threading.Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)
