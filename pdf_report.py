import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_executive_pdf(data, output_pdf):
    target = data.get('target', 'target')
    
    doc = SimpleDocTemplate(
        output_pdf, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Corporate Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold'
    )
    
    alert_style = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#991b1b')
    )

    # Header / Title Block
    story.append(Paragraph("<b>EXECUTIVE CYBERSECURITY RISK ASSESSMENT</b>", title_style))
    story.append(Paragraph(f"Prepared for: <b>{target}</b> &nbsp;|&nbsp; Date: {data.get('scan_time', '').split()[0]} &nbsp;|&nbsp; Status: <b>Action Required</b>", subtitle_style))
    
    # Executive Summary Box
    summary_text = f"""
    <b>Executive Overview:</b> This automated security briefing evaluates the external attack surface and browser security posture of <b>{target}</b>. While your core encryption (SSL/TLS) and transport layers are functional, our diagnostic identified critical missing HTTP security headers. Without these defenses, your web application is exposed to browser-based client-side exploits, including Cross-Site Scripting (XSS) and Clickjacking, which can compromise user trust and data integrity.
    """
    summary_table = Table([[Paragraph(summary_text, body_style)]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # Section 1: Risk Analysis & Business Impact
    story.append(Paragraph("1. Identified Vulnerabilities & Business Risk Analysis", section_heading))
    
    headers = data.get('security_headers', {})
    
    # Wrap headers text inside Paragraphs to force proper wrapping and prevent clipping/overlapping
    header_table_data = [[
        Paragraph("<b>Security Control / Header</b>", table_header_style), 
        Paragraph("<b>Current Status</b>", table_header_style), 
        Paragraph("<b>Business Risk & Impact</b>", table_header_style)
    ]]
    
    risk_descriptions = {
        "Content-Security-Policy": "High Risk: Missing CSP allows attackers to inject malicious scripts (XSS), leading to session hijacking and data theft.",
        "X-Frame-Options": "Medium Risk: Absence permits Clickjacking, allowing malicious sites to embed your app in invisible frames and trick users.",
        "X-Content-Type-Options": "Medium Risk: Lack of MIME-sniffing defense can cause browsers to execute malicious uploaded files.",
        "X-XSS-Protection": "Low Risk: Legacy XSS filter disabled, though modern browsers rely primarily on CSP."
    }

    for h, status in headers.items():
        if "Missing" in status:
            status_html = "<font color='#dc2626'><b>VULNERABLE</b></font>"
            desc = risk_descriptions.get(h, "Exposes application to browser-based client exploits.")
        else:
            status_html = "<font color='#16a34a'><b>SECURE</b></font>"
            desc = "Properly configured and enforced."
            
        header_table_data.append([
            Paragraph(f"<b>{h}</b>", table_cell_style),
            Paragraph(status_html, table_cell_style),
            Paragraph(desc, table_cell_style)
        ])

    # Expanded column widths to provide ample room and prevent overlap (Total = 540)
    t_headers = Table(header_table_data, colWidths=[150, 90, 300])
    t_headers.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_headers)
    story.append(Spacer(1, 8))

    # Section 2: Professional Recommendations & Solutions
    story.append(Paragraph("2. Remediation Strategy & Engineering Solutions", section_heading))
    
    solutions_text = """
    To achieve an enterprise-grade security posture and protect your users, your development team should implement the following HTTP response headers immediately on your web server (Nginx/Apache/Cloudflare):
    <br/><br/>
    <b>1. Implement Content-Security-Policy (CSP):</b><br/>
    <font face="Courier" size="7.5">Content-Security-Policy: default-src 'self' https:; script-src 'self' 'unsafe-inline'</font><br/>
    <i>Restricts the resources (such as JavaScript, CSS, Images) that the browser is allowed to load for your page.</i>
    <br/><br/>
    <b>2. Enforce X-Frame-Options:</b><br/>
    <font face="Courier" size="7.5">X-Frame-Options: DENY (or SAMEORIGIN)</font><br/>
    <i>Protects your web pages against clickjacking by preventing other sites from framing your content.</i>
    <br/><br/>
    <b>3. Set X-Content-Type-Options:</b><br/>
    <font face="Courier" size="7.5">X-Content-Type-Options: nosniff</font><br/>
    <i>Forces browsers to strictly adhere to declared content types, blocking MIME-sniffing attacks.</i>
    """
    
    sol_table = Table([[Paragraph(solutions_text, body_style)]], colWidths=[540])
    sol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bbf7d0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sol_table)
    story.append(Spacer(1, 8))

    # Section 3: Infrastructure & SSL Audit
    story.append(Paragraph("3. Infrastructure & SSL/TLS Health", section_heading))
    ssl_info = data.get('ssl_info', {})
    issuer = ssl_info.get('issuer', {})
    ports = data.get('open_ports', [])
    
    infra_text = f"""
    <b>Open Ports Discovered:</b> {', '.join(map(str, ports)) if ports else 'None'} (Standard HTTP/HTTPS web ports active).<br/>
    <b>Encryption Protocol:</b> {ssl_info.get('version', 'N/A')} (Modern secure transport layer).<br/>
    <b>Certificate Authority:</b> {issuer.get('organizationName', 'N/A')} — Valid until {ssl_info.get('expiry', 'N/A')}.
    """
    story.append(Paragraph(infra_text, body_style))
    story.append(Spacer(1, 10))

    # Call to Action / Pitch Footer
    cta_text = """
    <b>Want to secure your application completely?</b><br/>
    This report was generated automatically by our automated B2B security auditing pipeline. If you would like a comprehensive manual penetration test or automated header hardening for your startup, get in touch with our security engineering team.
    """
    cta_table = Table([[Paragraph(cta_text, alert_style)]], colWidths=[540])
    cta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fecaca')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cta_table)

    doc.build(story)
    print(f"[+] Fixed Professional Pitch PDF generated successfully: {output_pdf}")