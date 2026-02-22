import re
import ssl
import socket
import requests
import whois
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class FeatureExtractor:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        try:
            self.response = requests.get(url, timeout=10)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            self.response = None
            self.soup = None

    def having_IP_Address(self):
        match = re.search(r'\d+\.\d+\.\d+\.\d+', self.url)
        return 1 if match else -1

    def URL_Length(self):
        if len(self.url) < 54:
            return -1
        elif len(self.url) < 75:
            return 0
        return 1

    def Shortining_Service(self):
        shorteners = ['bit.ly','tinyurl','goo.gl','t.co',
                      'ow.ly','is.gd','buff.ly','adf.ly']
        for s in shorteners:
            if s in self.url:
                return 1
        return -1

    def having_At_Symbol(self):
        return 1 if '@' in self.url else -1

    def double_slash_redirecting(self):
        # Check for // after http://
        pos = self.url.find('//')
        if self.url.rfind('//') > pos:
            return 1
        return -1

    def Prefix_Suffix(self):
        return 1 if '-' in self.domain else -1

    def having_Sub_Domain(self):
        dots = self.domain.count('.')
        if dots == 1:
            return -1
        elif dots == 2:
            return 0
        return 1

    def SSLfinal_State(self):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain):
                    return 1  # valid SSL
        except:
            return -1  # no SSL

    def Domain_registeration_length(self):
        try:
            w = whois.whois(self.domain)
            exp = w.expiration_date
            if isinstance(exp, list):
                exp = exp[0]
            days = (exp - datetime.now()).days
            return 1 if days > 365 else -1
        except:
            return -1

    def Favicon(self):
        try:
            for link in self.soup.find_all('link', rel='icon'):
                href = link.get('href', '')
                if self.domain not in href and href.startswith('http'):
                    return -1  # favicon from different domain
            return 1
        except:
            return -1

    def port(self):
        try:
            parsed = urlparse(self.url)
            if parsed.port and parsed.port not in [80, 443]:
                return -1  # unusual port
            return 1
        except:
            return -1

    def HTTPS_token(self):
        return -1 if 'https' in self.domain.lower() else 1

    def Request_URL(self):
        try:
            total, external = 0, 0
            for tag in self.soup.find_all(['img','script','link']):
                src = tag.get('src') or tag.get('href') or ''
                if src.startswith('http'):
                    total += 1
                    if self.domain not in src:
                        external += 1
            if total == 0:
                return -1
            ratio = external / total
            if ratio < 0.22:
                return 1
            elif ratio < 0.61:
                return 0
            return -1
        except:
            return -1

    def URL_of_Anchor(self):
        try:
            total, external = 0, 0
            for tag in self.soup.find_all('a'):
                href = tag.get('href', '')
                if href.startswith('http'):
                    total += 1
                    if self.domain not in href:
                        external += 1
            if total == 0:
                return -1
            ratio = external / total
            if ratio < 0.31:
                return 1
            elif ratio < 0.67:
                return 0
            return -1
        except:
            return -1

    def Links_in_tags(self):
        try:
            total, external = 0, 0
            for tag in self.soup.find_all(['meta','script','link']):
                src = tag.get('src') or tag.get('href') or ''
                if src:
                    total += 1
                    if self.domain not in src:
                        external += 1
            if total == 0:
                return -1
            ratio = external / total
            return -1 if ratio > 0.61 else 1
        except:
            return -1

    def SFH(self):
        try:
            for form in self.soup.find_all('form'):
                action = form.get('action', '')
                if action == '' or action == 'about:blank':
                    return -1
                if self.domain not in action and action.startswith('http'):
                    return -1
            return 1
        except:
            return -1

    def Submitting_to_email(self):
        try:
            for form in self.soup.find_all('form'):
                action = form.get('action', '')
                if 'mailto:' in action:
                    return 1
            return -1
        except:
            return -1

    def Abnormal_URL(self):
        try:
            w = whois.whois(self.domain)
            return 1 if self.domain in str(w) else -1
        except:
            return -1

    def Redirect(self):
        try:
            if self.response:
                return 1 if len(self.response.history) > 2 else 0
            return -1
        except:
            return -1

    def on_mouseover(self):
        try:
            if self.response and 'onmouseover' in self.response.text:
                return 1
            return -1
        except:
            return -1

    def RightClick(self):
        try:
            if self.response and 'preventdefault' in self.response.text.lower():
                return -1
            return 1
        except:
            return -1

    def popUpWidnow(self):
        try:
            if self.response and 'alert(' in self.response.text:
                return 1
            return -1
        except:
            return -1

    def Iframe(self):
        try:
            if self.soup and self.soup.find_all('iframe'):
                return -1
            return 1
        except:
            return -1

    def age_of_domain(self):
        try:
            w = whois.whois(self.domain)
            created = w.creation_date
            if isinstance(created, list):
                created = created[0]
            age = (datetime.now() - created).days
            return 1 if age > 180 else -1
        except:
            return -1

    def DNSRecord(self):
        try:
            socket.gethostbyname(self.domain)
            return 1   # DNS exists
        except:
            return -1  # no DNS

    def web_traffic(self):
        # Without paid API, we estimate using Alexa
        try:
            response = requests.get(
                f"https://data.alexa.com/data?cli=10&url={self.domain}",
                timeout=5
            )
            rank = re.search(r'<REACH RANK="(\d+)"', response.text)
            if rank:
                return 1 if int(rank.group(1)) < 100000 else -1
            return -1
        except:
            return -1

    def Page_Rank(self):
        # Simplified - check if site appears in search
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(
                f"https://www.google.com/search?q={self.domain}",
                headers=headers, timeout=5
            )
            return 1 if self.domain in r.text else -1
        except:
            return -1

    def Google_Index(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(
                f"https://www.google.com/search?q=site:{self.domain}",
                headers=headers, timeout=5
            )
            return -1 if 'did not match' in r.text else 1
        except:
            return -1

    def Links_pointing_to_page(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(
                f"https://www.google.com/search?q=link:{self.domain}",
                headers=headers, timeout=5
            )
            links = re.findall(r'<cite>', r.text)
            if len(links) == 0:
                return -1
            elif len(links) <= 2:
                return 0
            return 1
        except:
            return -1

    def Statistical_report(self):
        # Check against PhishTank
        try:
            r = requests.get(
                f"https://checkurl.phishtank.com/checkurl/",
                data={'url': self.url, 'format': 'json'},
                timeout=5
            )
            result = r.json()
            return 1 if result.get('results', {}).get('in_database') else -1
        except:
            return -1

    def extract_all_features(self):
        features = {
            'having_IP_Address': self.having_IP_Address(),
            'URL_Length': self.URL_Length(),
            'Shortining_Service': self.Shortining_Service(),
            'having_At_Symbol': self.having_At_Symbol(),
            'double_slash_redirecting': self.double_slash_redirecting(),
            'Prefix_Suffix': self.Prefix_Suffix(),
            'having_Sub_Domain': self.having_Sub_Domain(),
            'SSLfinal_State': self.SSLfinal_State(),
            'Domain_registeration_length': self.Domain_registeration_length(),
            'Favicon': self.Favicon(),
            'port': self.port(),
            'HTTPS_token': self.HTTPS_token(),
            'Request_URL': self.Request_URL(),
            'URL_of_Anchor': self.URL_of_Anchor(),
            'Links_in_tags': self.Links_in_tags(),
            'SFH': self.SFH(),
            'Submitting_to_email': self.Submitting_to_email(),
            'Abnormal_URL': self.Abnormal_URL(),
            'Redirect': self.Redirect(),
            'on_mouseover': self.on_mouseover(),
            'RightClick': self.RightClick(),
            'popUpWidnow': self.popUpWidnow(),
            'Iframe': self.Iframe(),
            'age_of_domain': self.age_of_domain(),
            'DNSRecord': self.DNSRecord(),
            'web_traffic': self.web_traffic(),
            'Page_Rank': self.Page_Rank(),
            'Google_Index': self.Google_Index(),
            'Links_pointing_to_page': self.Links_pointing_to_page(),
            'Statistical_report': self.Statistical_report(),
        }
        return features