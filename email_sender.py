import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "re_your_api_key_here")

def send_security_audit_email(receiver_email, owner_name, target_domain, pdf_path):
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">🛡️ Security Vulnerability Advisory</h2>
            <p>Hi <b>{owner_name if owner_name else 'Founder / Team'}</b>,</p>
            <p>While conducting an external automated security posture analysis of <b>{target_domain}</b>, our diagnostic engine identified critical missing HTTP security headers and browser-defense configurations exposing your application to client-side threats (XSS & Clickjacking).</p>
            <p>We have attached your customized <b>Executive Cybersecurity Risk Assessment Report</b> to this email containing detailed remediation steps and server configuration snippets.</p>
            <div style="background-color: #f8fafc; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #1e293b;"><b>Action Required:</b> Immediate hardening of Nginx/Cloudflare security headers recommended to protect user data and session integrity.</p>
            </div>
            <p>If you would like our security engineering team to assist with infrastructure hardening, feel free to reply directly.</p>
            <p style="margin-top: 30px; font-size: 12px; color: #64748b;">Best regards,<br><b>Security Engineering Team</b><br>B2B Security Solutions</p>
        </div>
        """

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        params = {
            "from": "Security Audit <audit@secguard.tech>",
            "to": [receiver_email],
            "subject": f"Security Vulnerability Advisory for {target_domain}",
            "html": html_content,
            "attachments": [
                {
                    "filename": os.path.basename(pdf_path),
                    "content": list(pdf_data)
                }
            ]
        }

        email = resend.Emails.send(params)
        print(f"[+] Professional email sent successfully to {receiver_email} via API. ID: {email.get('id')}")
        return True
    except Exception as e:
        print(f"[-] Failed to dispatch email via API: {str(e)}")
        return False