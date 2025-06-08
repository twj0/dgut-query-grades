# config.py

# 统一认证平台的登录页面
LOGIN_PAGE_URL = "https://auth.dgut.edu.cn/"

# ！！！将这里替换成你用F12找到的那个POST请求的 Request URL
LOGIN_POST_URL = "https://auth.dgut.edu.cn/login?service=..." # 这只是一个例子，请务必替换

# ！！！教务系统的成绩接口也可能变了，需要登录后抓取确认
GRADE_API_URL = "https://jwxt.dgut.edu.cn/student/for-std/grade/sheet/info" 

# 请求头，Referer很重要，它告诉服务器你是从哪个页面提交的请求
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': LOGIN_PAGE_URL 
}