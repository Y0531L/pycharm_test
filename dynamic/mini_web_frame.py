import re
import pymysql

url_func_dict = dict()
data_ip = '192.168.167.92'
def route(my_data):
    def func_out(func):
        url_func_dict[my_data] = func
        def func_in():
            pass
        return func_in
    return func_out

@route(r'/indexdy.html')
def index(ret):
    with open('./templates/indexdy.html', 'rb') as f:
        content = f.read()
    db = pymysql.connect(host=data_ip, port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    cs = db.cursor()
    # sql语句
    sql = "select * from info;"
    cs.execute(sql)
    my_data = cs.fetchall()
    # html代码
    temp = """
    <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule=%s>
        </td>
        </tr>"""
    html = ''
    for i in my_data:
        html += temp% (i[0],i[1],i[2],i[3], i[4], i[5], i[6], i[7], i[1])
    content = content.decode('utf-8')
    content = re.sub(r"{%content%", html, content)
    content = content.encode('utf-8')
    cs.close()
    db.close()

    return content

def application(envir, set_response):
    set_response('200 OK',  [('Content-Type', 'text/html; charset=utf-8'), ("Server", "YL_web")] )
    file_name = envir['url']
    try:
        for key,value in url_func_dict.items():
            ret = re.match(key, file_name)
            if ret:
                rsp = value(ret)
                return rsp
        else:
            str = '%s is not found' % file_name
            return str.encode('utf-8')
    except Exception as e:
        print(e)
        return ('异常').encode('utf-8')
    pass