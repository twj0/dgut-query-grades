# dgut_grade_checker_v9_final.py (The Final Product with more details)
import requests
import re
import execjs
import os
from bs4 import BeautifulSoup

# --- Part 1: Login Module (No changes) ---
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9", "Cache-Control": "max-age=0", "Connection": "keep-alive",
    "Origin": "https://auth.dgut.edu.cn",
    "Referer": "https://auth.dgut.edu.cn/authserver/login?service=http%3A%2F%2Fauth.dgut.edu.cn%2FpersonalInfo%2FpersonCenter%2Findex.html%23%2Fauthorization",
    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\""
}
LOGIN_URL = "https://auth.dgut.edu.cn/authserver/login"

def encrypt_password_with_js(password: str, aes_key: str) -> str | None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(script_dir, "encrypt.js")
    if not os.path.exists(js_file_path):
        print(f"   [错误] encrypt.js 文件未找到！")
        return None
    with open(js_file_path, "r", encoding="utf-8") as f: js_code = f.read()
    try:
        ctx = execjs.compile(js_code)
        return ctx.call("encryptPassword", password, aes_key)
    except execjs.RuntimeError as e:
        print(f"   [错误] JavaScript 运行环境错误: {e}")
        return None

def login(username, password) -> requests.Session | None:
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        get_resp = session.get(LOGIN_URL)
        get_resp.raise_for_status()
        
        regex = r'.*id="pwdEncryptSalt".*?value="(.*?)".*id="execution".*?value="(.*?)"'
        params = re.search(regex, get_resp.text, re.S)
        if not params: return None
        pwd_encrypt_salt, execution = params.groups()
        
        jsessionid = session.cookies.get('JSESSIONID')
        route = session.cookies.get('route')
        if not jsessionid or not route: return None
        
        manual_cookie_header = f"route={route}; JSESSIONID={jsessionid}; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN"
        
        encrypted_password = encrypt_password_with_js(password, pwd_encrypt_salt)
        if not encrypted_password: return None
        
        login_data = {
            "username": username, "password": encrypted_password, "captcha": "",
            "_eventId": "submit", "cllt": "userNameLogin", "dllt": "generalLogin",
            "lt": "", "execution": execution,
        }
        
        post_headers = HEADERS.copy()
        post_headers['Cookie'] = manual_cookie_header
        
        post_resp = session.post(LOGIN_URL, headers=post_headers, data=login_data, allow_redirects=False)
        
        if post_resp.status_code == 302:
            session.get(post_resp.headers['Location'])
            return session
        return None
    except Exception:
        return None

# --- Part 2: Grade Fetching Module (Final Version with More Details) ---

def get_grades(session: requests.Session, year: str, semester: str):
    """
    ⭐最终版：此版本增加了平时成绩和考试成绩的输出。
    """
    print("\n--- 正在获取成绩信息 ---")
    grade_url = "https://jw.dgut.edu.cn/student/xscj.stuckcj_data.jsp"
    grade_headers = {
        "Referer": "https://jw.dgut.edu.cn/student/xscj.stuckcj.jsp?menucode=S40303",
        "User-Agent": HEADERS["User-Agent"]
    }
    semester_code = str(int(semester) - 1)
    grade_data = {
        "sjxz": "sjxz3", "ysyx": "yscj", "zx": "1", "fx": "0",
        "xn": year, "xn1": str(int(year) + 1), "xq": semester_code,
    }
    
    try:
        print(f"正在查询 {year}-{int(year)+1}学年 第{semester}学期 的成绩...")
        session.get("https://jw.dgut.edu.cn/caslogin")
        resp = session.post(grade_url, headers=grade_headers, data=grade_data)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, "lxml")
        tables = soup.find_all("table")
        if len(tables) < 2:
            print("   [错误] 未在返回页面中找到成绩表格。")
            return
            
        grade_table = tables[1]
        rows = grade_table.find_all("tr")
        
        if len(rows) <= 1:
            print("   [信息] 该学期可能没有成绩数据。")
            return

        print("\n" + "="*80)
        print(f" 东莞理工学院 {year}-{int(year)+1}学年 第{semester}学期 成绩单")
        print("="*80)
        
        # 遍历表格的每一行 (跳过表头)
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 13: continue 
            
            # --- ⭐ 使用正确的列索引提取所有需要的数据 ⭐ ---
            course_name = cells[1].text.strip().replace('\n', '') # 课程名称
            credit = cells[2].text.strip()       # 学分
            regular_score = cells[8].text.strip()  # 平时成绩
            exam_score = cells[10].text.strip()   # 期末/考试成绩
            final_score = cells[12].text.strip()  # 总评成绩
            
            # 如果没有成绩，显示'--'
            regular_score = regular_score if regular_score else '--'
            exam_score = exam_score if exam_score else '--'
            final_score = final_score if final_score else '--'

            # 格式化输出，让它看起来像一张真正的成绩单
            print(f"| {course_name:<28} | 学分: {credit:<4} | 平时: {regular_score:<5} | 考试: {exam_score:<5} | 最终成绩: {final_score:<5} |")

        print("="*80)

    except Exception as e:
        print(f"   [错误] 查询或解析成绩时发生错误: {e}")

# --- Part 3: The Main Program (No changes) ---

if __name__ == "__main__":
    MY_USERNAME = "2023428020130"
    MY_PASSWORD = "123456twj"

    print("--- 东莞理工学院成绩查询器 ---")
    if MY_USERNAME == "你的学号" or MY_PASSWORD == "你的密码":
        print("\n!!! 请先在脚本中填入你的真实学号和密码再运行 !!!\n")
    else:
        print("\n[步骤 1/2] 正在尝试登录...")
        session = login(MY_USERNAME, MY_PASSWORD)
        
        if session:
            print("\n[步骤 2/2] 登录成功！准备查询成绩。")
            while True:
                query_year = input("请输入要查询的学年 (例如: 2023): ").strip()
                query_semester = input("请输入要查询的学期 (1 或 2): ").strip()
                if query_year.isdigit() and query_semester in ("1", "2"):
                    get_grades(session, query_year, query_semester)
                else:
                    print("输入不合法，请重新输入。")
                cont = input("\n是否继续查询其他学期? (y/n): ").strip().lower()
                if cont != 'y':
                    break
            print("\n感谢使用！程序已退出。")
        else:
            print("\n登录失败，无法查询成绩。")