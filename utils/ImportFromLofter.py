from lxml import etree
import datetime
import urllib.request
import urllib.parse
import http.cookiejar
import json


class ImportFromLofter:
    def __init__(self, file_path, name, password):
        with open(file_path, 'rb') as f:
            file_content = f.read()
        self.root = etree.fromstring(file_content, parser=etree.XMLParser(recover=True))
        self.base_url = 'http://localhost:5000/'
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        login_request = urllib.request.Request(self.base_url + 'api/login',
                                               data=urllib.parse.urlencode({'name': name, 'password': password}).encode(
                                                   'utf-8'), method='POST')
        with self.opener.open(login_request) as f:
            print(f.read().decode('utf-8'))

    def extract_user_ids(self):
        user_ids = set()
        for post_item in self.root.iter('PostItem'):
            comment_list = post_item.find('commentList')
            if comment_list:
                for comment in comment_list.iter('comment'):
                    user_ids.add(comment.find('publisherUserId').text)
                    user_ids.add(comment.find('replyToUserId').text)
        return user_ids

    def run_import(self, user_ids_dict):
        for post_item in self.root.findall('PostItem'):
            publish_time = datetime.datetime.fromtimestamp(int(post_item.find('publishTime').text) // 1000)

            post_type = post_item.find('type').text
            if post_type == 'Text':
                raw_content = post_item.find('content').text
            elif post_type == 'Photo':
                raw_content = post_item.find('caption').text
            content = ''.join(etree.fromstring(raw_content, parser=etree.XMLParser(recover=True)).itertext())
            post_article_request = urllib.request.Request(self.base_url + 'api/postArticle',
                                                          data=urllib.parse.urlencode(
                                                              {'article': content, 'time': publish_time}).encode(
                                                              'utf-8'), method='POST')
            with self.opener.open(post_article_request) as f:
                article_id = json.loads(f.read().decode('utf-8'))['articleId']
            comments = []
            comment_list = post_item.find('commentList')
            if comment_list:
                for comment in comment_list.iter('comment'):
                    lofter_author_user_id = comment.find('publisherUserId').text
                    lofter_reply_to_user_id = comment.find('replyToUserId').text
                    publish_time = datetime.datetime.fromtimestamp(int(comment.find('publishTime').text) // 1000)
                    content = comment.find('content').text
                    comments.append((user_ids_dict[lofter_author_user_id], user_ids_dict[lofter_reply_to_user_id],
                                     publish_time, content))
            comments.sort(key=lambda x: x[2])
            parent_comment_id = '0'
            for comment in comments:
                if comment[1] == '':
                    parent_comment_id = '0'
                post_comment_request = urllib.request.Request(self.base_url + 'api/postComment',
                                                              data=urllib.parse.urlencode(
                                                                  {'articleId': article_id, 'comment': comment[3],
                                                                   'parentCommentId': parent_comment_id,
                                                                   'time': comment[2], 'userId': comment[0]}).encode(
                                                                  'utf-8'), method='POST')
                with self.opener.open(post_comment_request) as f:
                    parent_comment_id = json.loads(f.read().decode('utf-8'))['commentId']


if __name__ == '__main__':
    lofter = ImportFromLofter('/Users/zhantong/Downloads/xmlexport.do', '北极熊', '123456')
    # print(lofter.extract_user_ids())
    lofter.run_import({
        '3Wx9vl0wdoE=': '',
        '/3hM5X5JBMQ=': '1',
        's1taZbwEndE=': '2'
    })
