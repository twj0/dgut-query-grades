# cas_login.py
import requests
from typing import Optional
from config import LOGIN_POST_URL, HEADERS

def login(username: str, password: str) -> Optional[requests.Session]:
    """
    登录学校新的统一身份认证系统。
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # ！！！关键：将这里替换成你从F12的Form Data中看到的所有字段
    login_data = {
        'username': username,
        'password': password,
        'lt': 'LT-248095-AgQG1g3gSFLd4tHSPc3e5eA4d2Xb1a-auth', # 例子：这些值通常是动态的
        'execution': 'e1s1',                                    # 例子
        '_eventId': 'submit',                                   # 例子
        'croypto': '',                                          # 例子
        # ... 把你在F12里看到的所有字段都加进来
    }
    
    try:
        print(f"正在向 {LOGIN_POST_URL} 发送登录请求...")
        response = session.post(LOGIN_POST_URL, data=login_data, allow_redirects=True) # 允许重定向很重要
        response.raise_for_status()

        # 判断是否登录成功，这一步需要调试
        # 登录成功后，通常会跳转到某个页面，或者返回的页面内容包含“欢迎”或你的名字
        # 你可以打印 response.text 和 response.url 来观察登录后的结果
        if "我的事务" in response.text or "欢迎" in response.text: # 根据实际成功页面的关键词调整
            print("登录成功！")
            return session
        else:
            print("登录失败！请检查Form Data是否完整，或登录成功关键词是否正确。")
            # print("Response URL:", response.url)
            # print("Response Text:", response.text[:500]) # 打印部分返回内容帮助调试
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None