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
              `created` DATETIME DEFAULT CURRENT_TIMESTAMP,
              `text` TEXT,
              `authorId` INT(10)
            )
            '''
            sql_create_users_table = '''
            CREATE TABLE `users` (
              `uid` INT(10) AUTO_INCREMENT PRIMARY KEY,
              `name` VARCHAR(32) NOT NULL UNIQUE,
              `password` VARCHAR(32) NOT NULL,
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

    def is_password_correct(self, user_name=None, user_id=None, password=None):
        if (user_name is None and user_id is None) or password is None:
            return False
        with self.db_con.cursor() as cursor:
            sql = 'SELECT EXISTS (SELECT * FROM `users` WHERE (`uid`=%s OR `name`=%s) AND `password`=%s) AS result'
            cursor.execute(sql, (user_id, user_name, password))
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

    def post_article(self, article, user_id, time=None):
        with self.db_con.cursor() as cursor:
            if time:
                sql = 'INSERT INTO `contents` (`text`,`authorId`,`created`) VALUES (%s,%s,%s)'
                cursor.execute(sql, (article, user_id, time))
            else:
                sql = 'INSERT INTO `contents` (`text`,`authorId`) VALUES (%s,%s)'
                cursor.execute(sql, (article, str(user_id)))
            sql_get_article_id = 'SELECT LAST_INSERT_ID() AS article_id'
            cursor.execute(sql_get_article_id)
            article_id = cursor.fetchone()['article_id']
        self.db_con.commit()
        return article_id

    def get_article(self, article_id):
        with self.db_con.cursor() as cursor:
            sql = '''
                SELECT 
                    `cid` AS article_id,
                    `created` AS post_time,
                    `text` AS article,
                    `authorId` AS user_id 
                FROM 
                    `contents` 
                WHERE 
                    `cid`=%s
                '''
            cursor.execute(sql, article_id)
            result = cursor.fetchone()
            return result

    def get_articles(self, user_id=None, offset=0, limit=20):
        with self.db_con.cursor() as cursor:
            sql = '''
                SELECT 
                    contents.cid AS article_id,
                    contents.created AS post_time,
                    contents.text AS article,
                    contents.authorId AS user_id,
                    users.name AS user_name 
                FROM 
                    `contents` AS contents, 
                    `users` AS users 
                WHERE 
                    contents.authorId=users.uid''' + ('AND `contents.authorId`=%s' if user_id is not None else '') + ''' 
                ORDER BY contents.created DESC 
                LIMIT %s 
                OFFSET %s
                '''
            cursor.execute(sql, ((user_id, offset, limit) if user_id is not None else (limit, offset)))
            result = cursor.fetchall()
            return result

    def post_comment(self, article_id, user_id, comment, parent_comment_id=0, time=None):
        with self.db_con.cursor() as cursor:
            if time:
                sql = 'INSERT INTO `comments` (`cid`,`authorId`,`text`,`parent`,`created`) VALUES (%s,%s,%s,%s,%s)'
                cursor.execute(sql, (article_id, user_id, comment, parent_comment_id, time))
            else:
                sql = 'INSERT INTO `comments` (`cid`,`authorId`,`text`,`parent`) VALUES (%s,%s,%s,%s)'
                cursor.execute(sql, (article_id, user_id, comment, parent_comment_id))
            sql_get_comment_id = 'SELECT LAST_INSERT_ID() AS comment_id'
            cursor.execute(sql_get_comment_id)
            comment_id = cursor.fetchone()['comment_id']
        self.db_con.commit()
        return comment_id

    def get_comments(self, article_id, parent_comment_id=0):
        with self.db_con.cursor() as cursor:
            sql = '''
                SELECT 
                    comments.coid AS comment_id,
                    comments.cid AS article_id,
                    comments.created AS post_time,
                    comments.authorId AS user_id,
                    users.name AS user_name, 
                    comments.text AS comment,
                    comments.parent AS parent_comment_id,
                    comments2.authorId AS parent_user_id,
                    users2.name AS parent_user_name
                FROM (
                    `comments` AS comments,
                    `users` AS users
                    )
                LEFT JOIN
                    `comments` AS comments2
                ON
                    comments.parent=comments2.coid
                LEFT JOIN
                    `users` AS users2
                ON
                    comments2.authorId=users2.uid
                WHERE 
                    comments.authorId=users.uid AND 
                    comments.cid=%s AND 
                    comments.parent=%s
                '''
            cursor.execute(sql, (article_id, parent_comment_id))
            result = cursor.fetchall()
            for item in result:
                item['children'] = self.get_comments(article_id, item['comment_id'])
            return result


if __name__ == '__main__':
    wetwo = WeTwo()
    # wetwo.post_comment(3,1,'test comment 2',1)
    # print(wetwo.get_comments(3))
