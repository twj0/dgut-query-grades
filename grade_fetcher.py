# grade_fetcher.py
import requests
from typing import Optional, Dict, Any
from config import GRADE_API_URL

def fetch_grades(session: requests.Session, academic_year: str, semester: str) -> Optional[Dict[str, Any]]:
    """
    使用已登录的 session 获取指定学期的成绩。

    Args:
        session (requests.Session): 已登录的 Session 对象。
        academic_year (str): 学年，例如 "2023-2024"。
        semester (str): 学期，例如 "1" 或 "2"。

    Returns:
        Optional[Dict[str, Any]]: 包含成绩信息的字典，如果失败则返回 None。
    """
    # 构建查询成绩的参数
    # 这些参数名(academicYear, semester)需要根据实际接口确定
    params = {
        'academicYear': academic_year,
        'semester': semester,
    }
    
    try:
        response = session.get(GRADE_API_URL, params=params)
        response.raise_for_status()
        
        # 假设接口返回的是 JSON 格式的数据
        grade_data = response.json()
        
        if grade_data.get("success"): # 假设返回的JSON里有 success 字段
            return grade_data.get("data") # 假设成绩在 data 字段里
        else:
            print(f"获取成绩失败: {grade_data.get('message')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"获取成绩时网络请求错误: {e}")
        return None
    except ValueError: # JSON aaaaaa
        print("解析成绩数据失败，返回的可能不是有效的 JSON 格式。")
        # print(response.text) # 打印原始返回内容以供调试
        return None