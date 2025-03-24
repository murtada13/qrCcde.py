import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
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
    return redirect(url_for('login'))

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
        cursor.execute('SELECT id, email, password FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user and user[2] == password:
            session['logged_in'] = True
            session['user_id'] = user[0]
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, deap, barcode FROM student WHERE id = %s', (session['user_id'],))
    student_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if student_data:
        name, department, barcode = student_data
    else:
        name = department = barcode = "لا توجد بيانات متاحة"

    qr_base64 = None
    if barcode != "لا توجد بيانات متاحة":
        qr = qrcode.make(barcode)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return render_template('index.html', email=email, name=name, department=department, barcode=barcode, qr_code=qr_base64)

# صفحة الملف الشخصي
@app.route('/profile')
def profile():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    email = session.get('email')
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جلب بيانات الطالب مع رقم الهاتف والعنوان من جدول student
    cursor.execute('SELECT name, deap, barcode, phone, address FROM student WHERE id = %s', (user_id,))
    student_data = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if student_data:
        name, department, barcode, phone, address = student_data  # تم إضافة العنوان
    else:
        name = department = barcode = phone = address = "غير متاح"

    qr_base64 = None
    if barcode != "غير متاح":
        qr = qrcode.make(barcode)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # إرسال البيانات إلى القالب
    return render_template('profile.html', email=email, name=name, department=department, barcode=barcode, phone=phone, address=address, qr_code=qr_base64)

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
