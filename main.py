# main.py
import os
from cas_login import login
from grade_fetcher import fetch_grades

def main():
    """
    主函数，执行登录和查询成绩的完整流程。
    """
    # 从环境变量或用户输入获取用户名和密码，更安全
    username = os.getenv("DGUT_USERNAME") or input("请输入你的学号: ")
    password = os.getenv("DGUT_PASSWORD") or input("请输入你的密码: ")

    # 1. 登录
    logged_in_session = login(username, password)
    
    if not logged_in_session:
        return # 登录失败，程序退出

    # 2. 获取用户想查询的学期
    year = input("请输入要查询的学年 (例如 2023-2024): ")
    term = input("请输入要查询的学期 (1 或 2): ")

    # 3. 查询成绩
    grades = fetch_grades(logged_in_session, year, term)

    # 4. 显示成绩
    if grades and 'list' in grades:
        print(f"\n--- {year}学年第{term}学期 成绩单 ---")
        for course in grades['list']:
            # 这些字段名(courseName, grade, credit)需要根据实际返回的JSON结构来确定
            print(
                f"课程: {course.get('courseName', 'N/A')}, "
                f"成绩: {course.get('grade', 'N/A')}, "
                f"学分: {course.get('credit', 'N/A')}"
            )
        print("---------------------------------")
    else:
        print("未能获取到成绩数据。")

if __name__ == "__main__":
    main()