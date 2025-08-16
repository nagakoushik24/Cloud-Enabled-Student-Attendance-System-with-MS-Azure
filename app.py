from flask import Flask, render_template, request, redirect, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'snk'

def get_conn():

    connection_string = ("Driver={ODBC Driver 17 for SQL Server};Server=tcp:attendance1.database.windows.net,1433;Database=att_dat;Uid=attendance;Pwd=Koushik@2408;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    return pyodbc.connect(connection_string)


db = get_conn()
cur= db.cursor()

@app.route('/')
def index():
    return render_template('index.html')    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if role == 'teacher':
            cur.execute("SELECT * FROM teachers WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()
            if user:
                session['loggedin'] = True
                session['username'] = user[0]
                session['role'] = 'teacher'
                return redirect('/teacher/dashboard')
            else:
                error = 'Invalid login credentials.'
                return render_template('login.html', error=error)
        elif role == 'admin':
            cur.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
            user = cur.fetchone()
            if user:
                session['loggedin'] = True
                session['username'] = user[0]
                session['role'] = 'admin'
                return redirect('/admin/admin_dashboard')
            else:
                error='Invalid login credentials'
                return render_template('login.html',error=error)
        cur.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        db= get_conn()
        cursor = db.cursor()
        query = "SELECT username FROM teachers WHERE username = ?"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Username already exists. Please choose a different one."
            return render_template('teacher_registration.html', error=error_message)
        insert_query = "INSERT INTO teachers (teacher_name, username, password, email, phone) VALUES  ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (name, username, password, email, phone))
        db.commit()
        return render_template('teacher_registration.html', message="Teacher successfully registered.")
    return render_template('teacher_registration.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == "POST":
        student_id = request.form['student_id']
        name = request.form['name']
        class_sec = request.form['class_sec']
        email = request.form['email']
        phone = request.form['phone']
        db= get_conn()
        cursor = db.cursor()
        query = "SELECT student_id FROM students WHERE student_id = ?"
        cursor.execute(query, (student_id,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Invalid student_id"
            return render_template('student_registration.html', error=error_message)
        insert_query = "INSERT INTO students (student_id, student_name, class_sec, email, phone) VALUES ( ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (student_id, name, class_sec, email, phone))
        db.commit()
        return render_template('student_registration.html', message="Student successfully registered.")
    return render_template('student_registration.html')

@app.route('/get_student',methods=['POST','GET'])
def get_student():
    if request.method=='POST':
        student_id=request.form['student_id']
        db= get_conn()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cur.fetchone()
        if student:
            message="Fetched student details"
            return render_template('update_student.html', student=student, msg=message)
        else:
            error = "Invalid Student ID"
            return render_template('update_student.html', err=error)
    return render_template('update_student.html') 

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        new_name = request.form['new_name']
        new_email = request.form['new_email']
        new_phone = request.form['new_phone']
        db= get_conn()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cur.fetchone()
        if student:
            cur.execute("UPDATE students SET student_name = ?, email = ?, phone = ? WHERE student_id = ?",(new_name, new_email, new_phone, student_id))
            db.commit()
            message = "Student ID " +str(student_id)+" details have been successfully updated."
            return render_template('update_student.html', student=student, message=message)
        else:
            error = "Invalid Student ID"
            return render_template('update_student.html', error=error)
    return render_template('update_student.html')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'loggedin' in session and session['role'] == 'teacher':
        db = get_conn()
        cur = db.cursor()
        cur.execute("SELECT * FROM classes WHERE teacher_username = ?", (session['username'],))
        # Convert rows to dictionaries
        classes = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
        cur.close()
        return render_template('teacher_dashboard.html', classes=classes)
    else:
        return redirect('/')
    
@app.route('/teacher/teacher_profile')
def teacher_profile():
    db= get_conn()
    cur = db.cursor()
    cur.execute("SELECT teacher_name, email, phone FROM teachers WHERE username = ?", (session['username'],))
    profile_data = cur.fetchone()
    cur.close()
    return render_template('teacher_profile.html', profile_data=profile_data)

@app.route('/teacher/update_profile', methods=['POST'])
def update_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    db= get_conn()
    cur = db.cursor()
    cur.execute("UPDATE teachers SET teacher_name = ?, email = ?, phone = ? WHERE username = ?",(name, email, phone, session['username']))
    db.commit()
    cur.close()
    return redirect('/teacher/teacher_profile')

@app.route('/teacher/add_class', methods=['GET', 'POST'])
def add_class():
    if 'loggedin' in session and session['role'] == 'teacher':
        db= get_conn()
        cur = db.cursor()
        if request.method == 'POST':
            class_name = request.form['class_name']
            class_section = request.form['class_section']
            attendance_date = request.form['attendance_date']
            teacher_username = request.form['teacher_username']
            cur.execute("INSERT INTO classes (class_sec, class_name, class_date, teacher_username) VALUES (?, ?, ?, ?)",
            (class_section, class_name, attendance_date, teacher_username))

            db.commit()
            cur.close()
            return redirect('/teacher/dashboard')
        cur.execute('SELECT DISTINCT class_sec from classes')
        class_sections = cur.fetchall()
        cur.close()
        return render_template('add_class.html', class_sections=class_sections)
    else:
        return redirect('/')


@app.route('/teacher/mark_attendance', methods=['GET'])
def mark_attendance():
    if 'loggedin' in session and session['role'] == 'teacher':
        # Retrieve any necessary data for the attendance marking page here if needed
        return render_template('mark_attendance.html')
    else:
        return redirect('/teacher/login')  # Redirect to login if not logged in

@app.route("/teacher/mark_attendance/validate", methods=['POST'])
def validate_class_details():
    if 'loggedin' in session and session['role'] == 'teacher':
        data = request.get_json()
        print("Received data:", data)  # Debugging line
        
        # Validate input data
        if not data or 'date' not in data or 'class_name' not in data or 'class_sec' not in data:
            response_data = {"success": False, "message": "Missing input data"}
            return Response(json.dumps(response_data), status=400, mimetype='application/json')
        
        class_date = data['date']
        class_name = data['class_name']
        class_sec = data['class_sec']
        
        # Connect to the database using pyodbc
        db = get_conn()
        cursor = db.cursor()
        
        cursor.execute(
            "SELECT class_id FROM classes WHERE class_name = ? AND class_sec = ? AND class_date = ?",
            (class_name, class_sec, class_date)
        )
        class_info = cursor.fetchone()
        
        if class_info:
            class_id = class_info[0]
            cursor.execute("SELECT student_id, student_name FROM students WHERE class_sec = ?", (class_sec,))
            students = [{"id": student[0], "name": student[1]} for student in cursor.fetchall()]
            cursor.close()
            response_data = {"success": True, "students": students}
            return Response(json.dumps(response_data), status=200, mimetype='application/json')
        else:
            cursor.close()
            response_data = {"success": False, "message": "Class not found or invalid date."}
            return Response(json.dumps(response_data), status=404, mimetype='application/json')
    else:
        return redirect('/teacher/login')


@app.route("/teacher/mark_attendance/<class_id>", methods=['GET'])
def display_attendance_form(class_id):
    if 'loggedin' in session and session['role'] == 'teacher':
        # Connect to the database using pyodbc
        db = get_conn()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM classes WHERE class_id = ?", (class_id,))
        classes = cursor.fetchone()
        
        if classes is None:
            # Handle case where the class ID does not exist
            return "Class not found", 404
        
        cursor.execute("SELECT * FROM students WHERE class_sec = ?", (classes[3],))
        students = cursor.fetchall()
        cursor.close()
        
        return render_template('mark_attendance.html', students=students, 
                               class_date=classes[4], 
                               class_name=classes[1], 
                               class_sec=classes[3], 
                               class_id=classes[0])
    else:
        return redirect('/teacher/login')  # Redirect to the login page if not logged in

@app.route("/teacher/mark_attendance/update", methods=['POST'])
def update_attendance():
    if 'loggedin' in session and session['role'] == 'teacher':
        # Getting values from the form and stripping whitespace
        class_date = request.form.get('class_date').strip()
        class_sec = request.form.get('class_sec').strip()
        class_name = request.form.get('class_name').strip()

        # Debugging logs
        print("Class Name:", class_name)
        print("Class Section:", class_sec)
        print("Class Date:", class_date)

        try:
            # Fetch class_id based on class_name, class_sec, and class_date
            query = "SELECT class_id FROM classes WHERE class_name = ? AND class_sec = ? AND class_date = ?"
            print("Executing query:", query)
            print("With parameters:", (class_name, class_sec, class_date))

            db = get_conn()
            cursor = db.cursor()
            cursor.execute(query, (class_name, class_sec, class_date))
            class_info = cursor.fetchone()

            if class_info:
                class_id = class_info[0]
                print("Found class ID:", class_id)

                # Loop through the students to update or insert attendance
                for student in request.form:
                    if student.startswith('attendance_'):
                        student_id = student.split('_')[1]  # Extract student ID from the input name
                        status = request.form[student]  # Get the status (present/absent)

                        print(f"Updating attendance: Class ID: {class_id}, Student ID: {student_id}, Status: {status}")

                        # Check if an attendance record already exists for this student and class
                        cursor.execute(
                            "SELECT * FROM attendance WHERE class_id = ? AND student_id = ?",
                            (class_id, student_id)
                        )
                        existing_record = cursor.fetchone()

                        if existing_record:
                            # If a record exists, update the status
                            cursor.execute(
                                "UPDATE attendance SET status = ? WHERE class_id = ? AND student_id = ?",
                                (status, class_id, student_id)
                            )
                        else:
                            # If no record exists, insert a new one
                            cursor.execute(
                                "INSERT INTO attendance (class_id, student_id, status) VALUES (?, ?, ?)",
                                (class_id, student_id, status)
                            )

                db.commit()  # Commit changes to the database
                cursor.close()
                return make_response(json.dumps({"success": True, "message": "Attendance updated successfully!"}), 200)
            else:
                cursor.close()
                print("Class not found or invalid date.")
                return make_response(json.dumps({"success": False, "message": "Class not found or invalid date."}), 400)
        
        except Exception as e:
            print("Error occurred:", e)  # Log the error
            return make_response(json.dumps({"success": False, "message": "An error occurred while submitting attendance."}), 500)

    else:
        return redirect('/teacher/login')



@app.route('/admin/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect('/')



@app.route("/admin/get_attendance_report", methods=['GET', 'POST'])
def get_attendance_report():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            class_sec = request.form.get('class_sec')
            class_date = request.form.get('class_date')
            class_name = request.form.get('class_name')
            
            db= get_conn()
            cur = db.cursor()
            cur.execute("SELECT student_id, student_name FROM students WHERE class_sec = ?", (class_sec,))
            students = cur.fetchall()
            
            cur.execute("SELECT student_id, status FROM attendance WHERE class_id IN (SELECT class_id FROM classes WHERE class_sec = ? AND class_date = ? AND class_name = ?)", (class_sec, class_date, class_name))
            attendance = cur.fetchall()
            
            cur.close()
            
            return render_template('attendance_report.html', class_sec=class_sec, class_date=class_date, class_name=class_name, students=students, attendance=attendance)
        else:
            db= get_conn()
            cur = db.cursor()
            cur.execute("SELECT DISTINCT class_sec FROM classes")
            secs = cur.fetchall()
            cur.execute("SELECT DISTINCT class_name FROM classes")
            class_names = cur.fetchall()
            cur.close()
            
            return render_template('attendance_report.html', class_secs=secs, class_names=class_names)
    else:
        return redirect('/admin/login')


    
@app.route('/admin/admin_profile')
def admin_profile():
    db= get_conn()
    cur = db.cursor()
    cur.execute("SELECT admin_name, email, phone FROM admins WHERE username = ?", (session['username'],))
    profile_data = cur.fetchone()
    cur.close()
    return render_template('admin_profile.html', profile_data=profile_data)

@app.route('/admin/update_admin_profile', methods=['POST'])
def update_admin_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    db= get_conn()
    cur = db.cursor()
    cur.execute("UPDATE admins SET admin_name = ?, email = ?, phone = ? WHERE username = ?",(name, email, phone, session['username']))
    db.commit()
    cur.close()
    return redirect('/admin/admin_profile')
    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=8000)
