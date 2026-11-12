import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from models import db, User, Report
from scanner import SecurityScanner
from pdf_report import generate_executive_pdf
from email_sender import send_security_audit_email

app = Flask(__name__)
app.secret_key = "super_secret_secguard_key"

# Local SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

UPLOAD_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("[+] Default admin user created (admin / admin123)")

# Landing Page Route
@app.route('/')
def landing():
    return render_template('landing.html')

# Portal Router (Dashboard redirect based on role)
@app.route('/portal')
def portal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        reports = Report.query.order_by(Report.created_at.desc()).all()
        clients = User.query.filter_by(role='client').all()
        return render_template('admin_dashboard.html', reports=reports, clients=clients, user=user)
    else:
        reports = Report.query.filter_by(target_domain=user.assigned_domain).all()
        return render_template('client_dashboard.html', reports=reports, user=user)

# Authentication Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('portal'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

# Admin Route: Create Client Account
@app.route('/admin/create-client', methods=['POST'])
def create_client():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    username = request.form.get('username')
    password = request.form.get('password')
    domain = request.form.get('domain')
    
    if username and password and domain:
        existing = User.query.filter_by(username=username).first()
        if not existing:
            client = User(username=username, role='client', assigned_domain=domain)
            client.set_password(password)
            db.session.add(client)
            db.session.commit()
            print(f"[+] Client created: {username} for domain {domain}")
            
    return redirect(url_for('portal'))

# Admin Route: Manual Scans Queue
@app.route('/scan', methods=['POST'])
def scan_leads():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    domains = request.form.getlist('domain[]')
    names = request.form.getlist('name[]')
    emails = request.form.getlist('email[]')
    
    for d, n, e in zip(domains, names, emails):
        if not d.strip():
            continue
        process_single_lead(d.strip(), n.strip() if n else "Founder", e.strip() if e else "")

    return redirect(url_for('portal'))

# Admin Route: Bulk CSV Upload
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    if 'csv_file' not in request.files:
        return redirect(url_for('portal'))
    
    file = request.files['csv_file']
    if file.filename == '':
        return redirect(url_for('portal'))
    
    if file:
        stream = io.TextIOWrapper(file.stream, encoding="UTF-8")
        reader = csv.DictReader(stream)
        for row in reader:
            domain = row.get('domain', '').strip()
            name = row.get('name', 'Founder').strip()
            email = row.get('email', '').strip()
            if domain:
                process_single_lead(domain, name, email)
                
    return redirect(url_for('portal'))

# Helper function to execute scan, generate PDF, save to DB, and send email via Resend API
def process_single_lead(domain, owner_name, owner_email):
    print(f"[+] Processing scan for: {domain} | Owner: {owner_name}")
    try:
        scanner = SecurityScanner(domain)
        scan_data = scanner.run_scan()
        
        pdf_filename = f"Security_Audit_{domain.replace('/', '_')}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        generate_executive_pdf(scan_data, pdf_path)
        
        existing_rep = Report.query.filter_by(filename=pdf_filename).first()
        if not existing_rep:
            report_entry = Report(filename=pdf_filename, target_domain=domain)
            db.session.add(report_entry)
            db.session.commit()
        
        if owner_email and "@" in owner_email:
            send_security_audit_email(owner_email, owner_name, domain, pdf_path)
    except Exception as e:
        print(f"[-] Error processing {domain}: {e}")

# Secure Report Download Route
@app.route('/download/<filename>')
def download_report(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Admin Route: Delete Report
@app.route('/delete/<filename>', methods=['POST'])
def delete_report(filename):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        Report.query.filter_by(filename=filename).delete()
        db.session.commit()
    except Exception as e:
        print(f"[-] Delete error: {e}")
    return redirect(url_for('portal'))

if __name__ == '__main__':
    print("[+] Starting SecGuard OS SaaS on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)