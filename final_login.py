# final_login_v7.py (The Manual Override)
import requests
import re
import execjs
import os

# The same full header set from v6
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Origin": "https://auth.dgut.edu.cn",
    "Referer": "https://auth.dgut.edu.cn/authserver/login?service=http%3A%2F%2Fauth.dgut.edu.cn%2FpersonalInfo%2FpersonCenter%2Findex.html%23%2Fauthorization",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
LOGIN_URL = "https://auth.dgut.edu.cn/authserver/login"

def encrypt_password_with_js(password: str, aes_key: str) -> str | None:
    # This function remains the same
    print("2. 正在加载并执行 encrypt.js 文件...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(script_dir, "encrypt.js")
    if not os.path.exists(js_file_path):
        print(f"   [错误] encrypt.js 文件未找到！路径: {js_file_path}")
        return None
    with open(js_file_path, "r", encoding="utf-8") as f: js_code = f.read()
    try:
        ctx = execjs.compile(js_code)
        encrypted_password = ctx.call("encryptPassword", password, aes_key)
        print("   [成功] JS加密执行完毕！")
        return encrypted_password
    except execjs.RuntimeError as e:
        print(f"   [错误] JavaScript 运行环境错误: {e}")
        return None

def login(username, password):
    session = requests.Session()
    session.headers.update(HEADERS)

    # Step 1: Get dynamic params and initial cookies
    print("1. 正在访问登录页面以获取动态参数和初始Cookie...")
    try:
        resp = session.get(LOGIN_URL)
        resp.raise_for_status()
        
        # Extract dynamic form data
        regex = r'.*id="pwdEncryptSalt".*?value="(.*?)".*id="execution".*?value="(.*?)"'
        params = re.search(regex, resp.text, re.S)
        if not params:
            print("   [错误] 无法在页面中找到加密参数。")
            return None
        pwd_encrypt_salt, execution = params.groups()
        print("   [成功] 获取到所有动态参数！")

        # --- ⭐ The Final Change: Manual Cookie Construction ⭐ ---
        # Get the dynamic cookies the server just gave us
        jsessionid = session.cookies.get('JSESSIONID')
        route = session.cookies.get('route')
        
        if not jsessionid or not route:
            print("   [错误] 未能从服务器获取到初始的 JSESSIONID 或 route cookie。")
            return None

        # Manually build the cookie string exactly as seen in the cURL command
        manual_cookie_header = f"route={route}; JSESSIONID={jsessionid}; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN"
        print("   [成功] 已手动构建Cookie头！")
        # --- ⭐ Change End ⭐ ---

    except requests.RequestException as e:
        print(f"   [错误] 访问登录页面时发生网络错误: {e}")
        return None

    # Step 2: Encrypt password
    encrypted_password = encrypt_password_with_js(password, pwd_encrypt_salt)
    if not encrypted_password: return None

    # Step 3: Assemble payload
    # We no longer need all the hidden inputs, just the core ones
    login_data = {
        "username": username,
        "password": encrypted_password,
        "captcha": "",
        "_eventId": "submit", # Hardcode this, it's always submit
        "cllt": "userNameLogin", # Hardcode this
        "dllt": "generalLogin", # Hardcode this
        "lt": "", # It was empty in your cURL
        "execution": execution,
    }
    
    # Step 4: Send the final POST request with the manually crafted cookie
    try:
        print("3. 正在发送最终登录请求 (携带手动构建的cookie)...")
        
        # Add the manually built cookie to a temporary header for this one request
        post_headers = HEADERS.copy()
        post_headers['Cookie'] = manual_cookie_header

        resp = requests.post(LOGIN_URL, headers=post_headers, data=login_data, allow_redirects=False)
        
        if resp.status_code == 302:
            print("   [成功] 收到302重定向！登录成功！！！")
            return resp # Return the response so we can complete the session
        else:
            print(f"   [失败] 服务器返回状态码: {resp.status_code} (预期为302)")
            return None

    except requests.RequestException as e:
        print(f"   [错误] 登录请求失败: {e}")
        return None

if __name__ == "__main__":
    # --- ONE LAST CHECK ---
    # Please, please triple-check your password for any typos.
    # Copy and paste it directly from your password manager if you can.
    MY_USERNAME = "2023428020130"
    MY_PASSWORD = "123456twj"

    print("--- 开始模拟登录东莞理工学院统一认证平台 (v7 - The Final Gambit) ---")
    if MY_USERNAME == "你的学号" or MY_PASSWORD == "你的密码":
        print("\n!!! 请先在脚本中填入你的真实学号和密码再运行 !!!\n")
    else:
        final_response = login(MY_USERNAME, MY_PASSWORD)
        if final_response:
            print("\n✅ 恭喜！我们终于突破了防线！")
        else:
            print("\n❌ 登录流程失败。我们已用尽所有常规手段。")
            print("   最后可能的原因：1.密码错误；2.服务器使用了无法绕过的TLS指纹识别。")