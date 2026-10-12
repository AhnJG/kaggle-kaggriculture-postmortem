"""Capture screenshots for Step 3 conditional alternative of COMMUNITY0929.
Captures full-screen section views for the 3 community notebooks using headless Chrome CDP.
"""
import base64
import json
from pathlib import Path
import socket
import struct
import subprocess
import time
import urllib.request
from urllib.parse import urlparse

OUT = Path(__file__).resolve().parent

def ws_connect(host, port, path):
    s = socket.create_connection((host, port), timeout=30)
    key = base64.b64encode(b'community_antigravity_0929').decode()
    req = (f"GET {path} HTTP/1.1\r\n"
           f"Host: {host}:{port}\r\n"
           "Upgrade: websocket\r\n"
           "Connection: Upgrade\r\n"
           f"Sec-WebSocket-Key: {key}\r\n"
           "Sec-WebSocket-Version: 13\r\n\r\n")
    s.sendall(req.encode())
    resp = s.recv(4096)
    assert b"101 " in resp, resp
    return s

def ws_send(s, msg):
    payload = msg.encode('utf-8')
    l = len(payload)
    mask_key = b'\x12\x34\x56\x78'
    if l <= 125:
        header = bytes([0x81, 0x80 | l])
    elif l <= 65535:
        header = bytes([0x81, 0x80 | 126]) + struct.pack("!H", l)
    else:
        header = bytes([0x81, 0x80 | 127]) + struct.pack("!Q", l)
    masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    s.sendall(header + mask_key + masked)

def ws_recv(s):
    def recv_exact(n):
        buf = b""
        while len(buf) < n:
            chunk = s.recv(n - len(buf))
            if not chunk:
                raise EOFError("Connection closed")
            buf += chunk
        return buf

    b1, b2 = recv_exact(2)
    masked = bool(b2 & 0x80)
    plen = b2 & 0x7F
    if plen == 126:
        plen = struct.unpack("!H", recv_exact(2))[0]
    elif plen == 127:
        plen = struct.unpack("!Q", recv_exact(8))[0]
    if masked:
        mask = recv_exact(4)
        data = recv_exact(plen)
        return bytes(b ^ mask[i % 4] for i, b in enumerate(data)).decode('utf-8', errors='replace')
    else:
        data = recv_exact(plen)
        return data.decode('utf-8', errors='replace')

class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self.id = 0

    def call(self, method, params=None):
        self.id += 1
        cid = self.id
        msg = {"id": cid, "method": method}
        if params:
            msg["params"] = params
        ws_send(self.ws, json.dumps(msg))
        while True:
            raw = ws_recv(self.ws)
            resp = json.loads(raw)
            if resp.get("id") == cid:
                return resp.get("result", {})

def capture_section(cdp, slug, filename, toc_search_text, extra_scroll=0):
    screen_dir = OUT / 'kernels' / slug / 'screens'
    screen_dir.mkdir(parents=True, exist_ok=True)
    target_path = screen_dir / filename

    js_action = f"""
    (() => {{
        // Remove cookie / privacy banner if present
        document.querySelectorAll('div').forEach(d => {{
            if (d.innerText && d.innerText.includes('Kaggle uses cookies') && d.offsetHeight < 100) {{
                d.style.display = 'none';
            }}
        }});

        let links = Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('#'));
        let target = links.find(a => a.innerText && a.innerText.toLowerCase().includes({json.dumps(toc_search_text.lower())}));
        if (target) {{
            target.click();
            return {{status: 'clicked_toc', text: target.innerText}};
        }}
        // Fallback: search headings directly
        let headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5'));
        let h = headings.find(el => el.innerText && el.innerText.toLowerCase().includes({json.dumps(toc_search_text.lower())}));
        if (h) {{
            h.scrollIntoView({{block: 'start'}});
            return {{status: 'scrolled_heading', text: h.innerText}};
        }}
        return {{status: 'not_found'}};
    }})()
    """
    res = cdp.call("Runtime.evaluate", {"expression": js_action, "returnByValue": True})
    time.sleep(1.5)

    if extra_scroll != 0:
        js_extra = f"""
        (() => {{
            let scroller = document.querySelector('.legacy-less-light-theme') || document.documentElement;
            scroller.scrollTop += {extra_scroll};
        }})()
        """
        cdp.call("Runtime.evaluate", {"expression": js_extra})
        time.sleep(1.0)

    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    img_data = base64.b64decode(shot['data'])
    target_path.write_bytes(img_data)
    print(f"Saved {slug}/screens/{filename} ({len(img_data):,} bytes) -> {res.get('result', {}).get('value')}")
    return target_path

def main():
    user_data = "/tmp/chrome_profile_comm0929"
    subprocess.run(["rm", "-rf", user_data], check=True)
    cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1600,1200"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/json/list") as resp:
            tabs = json.loads(resp.read().decode())
        page_tab = [t for t in tabs if t.get('type') == 'page'][0]
        u = urlparse(page_tab['webSocketDebuggerUrl'])
        ws = ws_connect(u.hostname, u.port, u.path)
        cdp = CDPClient(ws)
        print("CDP connected to Chrome.")

        # 1. 2600-farms
        # Sections: 1, 4, 5, 7, 8, 9, 10, Takeaways
        slug1 = "kaggriculture-what-2600-farms-do-differently"
        url1 = f"https://www.kaggle.com/code/georgymamarin/{slug1}"
        print(f"\nNavigating to {url1}...")
        cdp.call("Page.navigate", {"url": url1})
        for _ in range(30):
            time.sleep(1)
            check = cdp.call("Runtime.evaluate", {"expression": "document.body.innerText.includes('1. What is in the dataset today')"})
            if check.get('result', {}).get('value', False):
                break

        capture_section(cdp, slug1, "01_section_1.png", "1. What is in the dataset today", extra_scroll=200)
        capture_section(cdp, slug1, "02_section_4.png", "4. Strategy fingerprints", extra_scroll=300)
        capture_section(cdp, slug1, "03_section_5.png", "5. What actually separates a big bank", extra_scroll=300)
        capture_section(cdp, slug1, "04_section_7.png", "7. How fast the bar is moving", extra_scroll=300)
        capture_section(cdp, slug1, "05_section_8.png", "8. Who beats whom", extra_scroll=300)
        capture_section(cdp, slug1, "06_section_9.png", "9. How much of this is luck", extra_scroll=300)
        capture_section(cdp, slug1, "07_section_10.png", "10. The openings they share", extra_scroll=300)
        capture_section(cdp, slug1, "08_takeaways.png", "Takeaways", extra_scroll=100)

        # 2. know-your-noise
        # Conclusion and effect size (effective sample, variance inflation, etc.) tables & charts
        slug2 = "kaggriculture-know-your-noise"
        url2 = f"https://www.kaggle.com/code/destbreso/{slug2}"
        print(f"\nNavigating to {url2}...")
        cdp.call("Page.navigate", {"url": url2})
        for _ in range(30):
            time.sleep(1)
            check = cdp.call("Runtime.evaluate", {"expression": "document.body.innerText.includes('How much money is noise?')"})
            if check.get('result', {}).get('value', False):
                break

        capture_section(cdp, slug2, "01_number_that_ends_the_argument.png", "The number that ends the argument", extra_scroll=350)
        capture_section(cdp, slug2, "02_reinvestment_wrong_variance.png", "The reinvestment argument is wrong", extra_scroll=350)
        capture_section(cdp, slug2, "03_three_explanations_refuted.png", "Three explanations, and the corpus", extra_scroll=350)
        capture_section(cdp, slug2, "04_effective_opponents_species_sampling.png", "How many opponents do you actually have", extra_scroll=400)
        capture_section(cdp, slug2, "05_what_to_take_away.png", "What to take away", extra_scroll=150)

        # 3. same-opening
        # Turn 48 related table & charts
        slug3 = "everyone-is-playing-the-same-opening"
        url3 = f"https://www.kaggle.com/code/destbreso/{slug3}"
        print(f"\nNavigating to {url3}...")
        cdp.call("Page.navigate", {"url": url3})
        for _ in range(30):
            time.sleep(1)
            check = cdp.call("Runtime.evaluate", {"expression": "document.body.innerText.includes('The thing we are trying to show')"})
            if check.get('result', {}).get('value', False):
                break

        capture_section(cdp, slug3, "01_field_stopped_ecology_48h.png", "5. The field stopped being an ecology in about 48 hours", extra_scroll=400)
        capture_section(cdp, slug3, "02_opening_horizon_measurement.png", "6. Only the opening horizon is a measurement at all", extra_scroll=400)
        capture_section(cdp, slug3, "03_arms_race_opening_shares.png", "8. There is no arms race", extra_scroll=400)

        print("\nAll requested screenshots captured successfully.")
    finally:
        proc.terminate()

if __name__ == '__main__':
    main()
