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
            `ownerId` INT(10),
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


if __name__ == '__main__':
    wetwo = WeTwo()
    wetwo.init_db()
