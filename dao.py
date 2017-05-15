import pymysql


# 使用 cursor() 方法创建一个游标对象 cursor
class dao:
    def connect(self):
        try:
            db = pymysql.connect(host="localhost", user="root", password="123", db="weibo", charset='utf8')
            return db
        except Exception as e:
            print(e)

    def create_if_not_exist(self):
        db = self.connect()
        cursor = db.cursor()
        try:
            cursor.execute(
                "create table if not exists follow_weibos(id int not null auto_increment,weibo_id varchar(50),"
                "nickname varchar(100),weibo_content varchar(200),weibo_time varchar(50),PRIMARY KEY (`id`))")
            print("Database check ok!")
        except Exception as e:
            print("create", e)
        db.close()

    def insert(self, weibo_id, weibo_content, nickname,weibo_time):
        db = self.connect()
        cursor = db.cursor()
        try:
            cursor.execute("insert into follow_weibos(weibo_id,weibo_content,nickname,weibo_time) values(%s,%s,%s,%s)",
                           (weibo_id, weibo_content, nickname,weibo_time))
            db.commit()
            print("Insert ok!")
        except Exception as e:
            print("insert", e)
        db.close()

    def search(self, nickname):
        db = self.connect()
        cursor = db.cursor()
        try:
            cursor.execute("select * from follow_weibos where nickname=%s", (nickname))
            results = cursor.fetchall()
            for row in results:
                print(row)
            print("Search ok!")
        except Exception as e:
            print("search", e)
        db.close()
