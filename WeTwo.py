import pymysql.cursors


class WeTwo:
    def __init__(self):
        self.db_con = pymysql.connect(host='localhost', user='root', password='123456', db='wetwo', charset='utf8mb4',
                                      cursorclass=pymysql.cursors.DictCursor)

    def init_db(self):
        with self.db_con.cursor() as cursor:
            sql_create_contents_table = '''
            CREATE TABLE `contents` (
              `cid` INT(10) AUTO_INCREMENT PRIMARY KEY,
              `create` DATETIME DEFAULT CURRENT_TIMESTAMP,
              `text` TEXT,
              `authorId` INT(10)
            )
            '''
            sql_create_users_table = '''
            CREATE TABLE `users` (
              `uid` INT(10) AUTO_INCREMENT PRIMARY KEY,
              `name` VARCHAR(32) UNIQUE,
              `password` VARCHAR(32),
              `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
              `logged` DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
            sql_create_comments_table = '''
            CREATE TABLE `comments` (
            `coid` INT(10) AUTO_INCREMENT PRIMARY KEY,
            `cid` INT(10),
            `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `authorId` INT(10),
            `ip` VARCHAR(64),
            `agent` VARCHAR(200),
            `text` TEXT,
            `parent` INT(10)
            )
            '''
            cursor.execute(sql_create_contents_table)
            cursor.execute(sql_create_users_table)
            cursor.execute(sql_create_comments_table)
        self.db_con.commit()

    def register(self, name, password):
        def check_exists(name):
            with self.db_con.cursor() as cursor:
                sql = 'SELECT EXISTS (SELECT * FROM `users` WHERE `name`=%s) AS result'
                cursor.execute(sql, name)
                result = cursor.fetchone()
                return result['result'] == 1

        if check_exists(name):
            return -1
        with self.db_con.cursor() as cursor:
            sql = 'INSERT INTO `users` (`name`,`password`) VALUES (%s,%s)'
            cursor.execute(sql, (name, password))
        self.db_con.commit()
        return 0

    def is_user_id_exists(self, user_id):
        if not user_id:
            return False
        with self.db_con.cursor() as cursor:
            sql = 'SELECT EXISTS (SELECT * FROM `users` WHERE `uid`=%s) AS result'
            cursor.execute(sql, user_id)
            result = cursor.fetchone()
            return result['result'] == 1

    def is_password_correct(self, user_id, password):
        with self.db_con.cursor() as cursor:
            sql = 'SELECT EXISTS (SELECT * FROM `users` WHERE `uid`=%s AND `password`=%s) AS result'
            cursor.execute(sql, (user_id, password))
            result = cursor.fetchone()
            return result['result'] == 1

    def get_user_id(self, name):
        with self.db_con.cursor() as cursor:
            sql = 'SELECT `uid` AS user_id FROM `users` WHERE `name`=%s'
            cursor.execute(sql, name)
            result = cursor.fetchone()
            if not result:
                return None
            return result['user_id']

    def post_article(self, article, user_id):
        with self.db_con.cursor() as cursor:
            sql = 'INSERT INTO `contents` (`text`,`authorId`) VALUES (%s,%s)'
            cursor.execute(sql, (article, str(user_id)))
            sql_get_article_id = 'SELECT LAST_INSERT_ID() AS article_id'
            cursor.execute(sql_get_article_id)
            article_id = cursor.fetchone()['article_id']
        self.db_con.commit()
        return article_id

    def get_article(self, article_id):
        with self.db_con.cursor() as cursor:
            sql = 'SELECT `cid` AS article_id,`create` AS post_time,`text` AS article,`authorId` AS user_id FROM `contents` WHERE `cid`=%s'
            cursor.execute(sql, article_id)
            result = cursor.fetchone()
            return result

    def post_comment(self, article_id, user_id, comment, parent_comment_id=0):
        with self.db_con.cursor() as cursor:
            sql = 'INSERT INTO `comments` (`cid`,`authorId`,`text`,`parent`) VALUES (%s,%s,%s,%s)'
            cursor.execute(sql, (article_id, user_id, comment, parent_comment_id))
        self.db_con.commit()

    def get_comments(self, article_id, parent_comment_id=0):
        with self.db_con.cursor() as cursor:
            sql = 'SELECT `coid` AS comment_id,`cid` AS article_id,`created` AS post_time,`authorId` AS user_id, `text` AS comment,`parent` AS parent_comment_id FROM `comments` WHERE `cid`=%s AND `parent`=%s'
            cursor.execute(sql, (article_id, parent_comment_id))
            result = cursor.fetchall()
            for item in result:
                item['children'] = self.get_comments(article_id, item['comment_id'])
            return result


if __name__ == '__main__':
    wetwo = WeTwo()
    # wetwo.post_comment(3,1,'test comment 2',1)
    # print(wetwo.get_comments(3))
