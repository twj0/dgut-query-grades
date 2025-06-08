import requests
from bs4 import BeautifulSoup

# 统一认证的登录页面URL
LOGIN_PAGE_URL = "https://auth.dgut.edu.cn/authserver/login?service=http%3A%2F%2Fauth.dgut.edu.cn%2FpersonalInfo%2FpersonCenter%2Findex.html%23%2Fauthorization"

# 请求头，模拟浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_execution_token() -> str | None:
    """
    访问登录页面，获取动态的 execution 令牌。
    """
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        
        print(f"正在访问登录页面: {LOGIN_PAGE_URL}")
        response = session.get(LOGIN_PAGE_URL)
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 查找包含 execution 值的 <input> 标签
        # 通常它会像这样：<input type="hidden" name="execution" value="xxxxxx">
        execution_input = soup.find('input', {'name': 'execution'})
        
        if execution_input and execution_input.get('value'):
            token = execution_input.get('value')
            print(f"成功获取 execution 令牌!")
            return token
        else:
            print("错误：在页面源码中未找到 'execution' 令牌。")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None

if __name__ == "__main__":
    execution_token = get_execution_token()
    if execution_token:
        print("\n获取到的 execution 令牌是：")
        print(execution_token)