#1\def __init__ 初始化
#2\验证码识别api
#3\模拟登录api
#4\爬取所有课程信息api
#5\主函数调用所有api
from pytesser3 import Image, image_to_string
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import pymysql

conn = pymysql.connect(host='127.0.0.1',
                       user='localhost',
                       passwd='123456',
                       db='swjtu',
                       charset='utf8'
                       )
cursor = conn.cursor()

username = input('please input your username:')
passwd = input('please input your passwd:')
img_url = 'http://jiaowu.swjtu.edu.cn/servlet/GetRandomNumberToJPEG'
headers = {
    'Host': 'jiaowu.swjtu.edu.cn',
    'Origin': 'http://jiaowu.swjtu.edu.cn',
    'Referer': "http://jiaowu.swjtu.edu.cn/service/login.jsp?user_type=student",
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
}
post_url = 'http://jiaowu.swjtu.edu.cn/servlet/UserLoginSQLAction'
course_url = 'http://jiaowu.swjtu.edu.cn/student/course/MyCourseThisTerm.jsp'

class Crawler(object):
    #类初始化
    def __init__(self):
        self.conn = conn
        self.username = username
        self.passwd = passwd
        self.img_url = img_url
        self.headers = headers
        self.post_url = post_url
        self.course_url = course_url

    # 获得验证码图片，此处需要把图片显示到书循环的页面让用户一起输入，然后返回
    def getCheckCode(self, session):
        img = session.get(self.img_url, headers=self.headers)
        imgs = Image.open(BytesIO(img.content))
        imgs.show()
        Checkcode = input('请输入验证码：')
        return Checkcode, session

    #模拟登录
    def login(self, checkCode, session):
        data = {
            'url': '../servlet/UserLoginCheckInfoAction',
            'OperatingSystem': "",
            'Browser': "",
            'user_id': self.username,
            'password': self.passwd,
            'ranstring': checkCode,
            'user_type': 'student',
            'btn1': "",
        }
        session.post(self.post_url, headers=self.headers, data=data)
        index = session.get('http://jiaowu.swjtu.edu.cn/usersys/index.jsp')
        return session

    # 解析爬取本学期所有课程
    def course(self, session):
        c_html = session.get(course_url, headers=headers)
        soup = BeautifulSoup(c_html.text, 'lxml')
        table = soup.find(bordercolorlight="#666666")
        rows = table.select('tr')
        length = len(rows)
        for row in rows[1:length - 1]:
            class_name = row.select('td:nth-of-type(4) > a > u > font')[0].text
            credit = float(row.select('td:nth-of-type(6)')[0].text)
            properties = row.select('td:nth-of-type(7)')[0].text
            teacher_name = row.select('td:nth-of-type(8)')[0].text
            college_given = row.select('td:nth-of-type(9)')[0].text
            classroom = row.select('td:nth-of-type(10)')[0].text
            data = {
                'class_name': class_name,
                'credit': credit,
                'properties': properties,
                'teacher_name': teacher_name,
                'college_given': college_given,
                'classroom': classroom,
            }
            sql = 'INSERT INTO course(class_name, credit, properties, teacher_name, college_given, classroom) ' \
                  'VALUES ("%s", "%d", "%s", "%s", "%s", "%s")' % \
                  (class_name, credit, properties, teacher_name, college_given, classroom)
            cursor.execute(sql)
            conn.commit()
            print(data)
        conn.close()

    #调用主函数
    def main(self):
        session = requests.session()
        checkCode, session = self.getCheckCode(session)
        session = self.login(checkCode, session)
        self.course(session)

if __name__ == '__main__':
    course_crawler = Crawler()
    course_crawler.main()


