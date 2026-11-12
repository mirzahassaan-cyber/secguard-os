import socket
import ssl
import urllib.request
from datetime import datetime

class SecurityScanner:
    def __init__(self, target_domain):
        self.target = target_domain.replace("http://", "").replace("https://", "").strip("/")
        self.results = {
            "target": self.target,
            "scan_time": str(datetime.now()),
            "open_ports": [],
            "security_headers": {},
            "ssl_info": {}
        }

    def check_ports(self):
        ports_to_check = [80, 443, 21, 22, 25, 3306, 8080]
        for port in ports_to_check:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                result = s.connect_ex((self.target, port))
                if result == 0:
                    self.results["open_ports"].append(port)
                s.close()
            except Exception:
                pass

    def check_headers(self):
        url = f"https://{self.target}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                headers = dict(response.headers)
                security_headers = [
                    'Strict-Transport-Security',
                    'Content-Security-Policy',
                    'X-Frame-Options',
                    'X-Content-Type-Options',
                    'X-XSS-Protection'
                ]
                for header in security_headers:
                    if header in headers:
                        self.results["security_headers"][header] = "Present"
                    else:
                        self.results["security_headers"][header] = "Missing (Vulnerability)"
        except Exception as e:
            self.results["security_headers"]["error"] = str(e)

    def check_ssl(self):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.target, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.target) as ssock:
                    cert = ssock.getpeercert()
                    self.results["ssl_info"] = {
                        "issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "expiry": cert.get('notAfter'),
                        "version": ssock.version()
                    }
        except Exception as e:
            self.results["ssl_info"]["error"] = str(e)

    def run_scan(self):
        self.check_ports()
        self.check_headers()
        self.check_ssl()
        return self.results