import json
import logging
from re import findall, compile

from grab import Grab
from grab.spider import Spider, Task
from redis import StrictRedis

from core.config import *
from core.tasks import save_result

logging.basicConfig(level=logging.DEBUG)

r_shopping_balance = compile(r'shopping_balance":{"value":([\d.]*?),')
r_username_and_pass = compile(r'name="([\w\S]{32})"')

platform = 'fiverr.com'


def parse(regex, body, _from=0, size=None):
    val = findall(regex, body)
    length = len(val)
    if length > 0:
        if length == 1:
            return val[0]
        else:
            return val[_from:size]
    else:
        return -1


def create_session(username, password, session_file, task_id, update=False):
    if update and os.path.isfile(session_file):
        os.remove(session_file)

    if not os.path.isfile(session_file):
        open(session_file, 'a')  # create a session file
        g = Grab()
        g.setup(cookiefile=session_file)
        g.go(FIVER_LOGIN_URL)
        username_field, password_field = findall(r_username_and_pass, g.response.body)
        g.doc.set_input(username_field, username)
        g.doc.set_input(password_field, password)
        if g.cookies.cookiejar:
            g.doc.submit()
            if username in g.response.body:
                return True
            else:
                save_result(task_id, STATUS_ERROR, error_message='Can\'t create session')
                return False
        else:
            save_result(task_id, STATUS_ERROR, error_message='Cookie not found %s' % g.cookies.cookiejar)
            return False
    else:
        return True


class FiverrSpider(Spider):
    def task_generator(self):
        rs = StrictRedis(host='localhost', port=6379, db=REDIS_TASK_DB_ID)
        for key in rs.keys(pattern='task_%s*' % platform):
            task_data = json.loads(rs.get(key))
            task_id = key.split('_')[-1]
            try:
                username = task_data['username']
                password = task_data['password']
            except Exception as e:
                save_result(task_id, platform, STATUS_ERROR, error_message=e.message)
            cookie_path = '%s/%s/%s.txt' % (COOKIE_FOLDER, platform, username)
            if create_session(username, password, cookie_path, task_id):
                g = Grab()
                g.setup(url='https://www.fiverr.com/users/%s/todos' % username, cookiefile=cookie_path)
                yield Task('page', grab=g, task_id=task_id, username=username, password=password,
                           cookie_path=cookie_path, initial=True)

    def task_page(self, grab, task):
        if grab.response.code == 200:
            balance = parse(r_shopping_balance, grab.response.body)
            if balance != -1:
                save_result(task.task_id, platform, STATUS_COMPLETED, data={'balance': balance})
            else:
                # we are here because the session is outdated or the page layout has been changed
                if task.initial:
                    # let's check the assumption about the change session
                    if create_session(task.username, task.password, task.cookie_path, task.task_id, update=True):
                        yield task.clone(initial=False)
                else:
                    save_result(task.task_id, platform, STATUS_ERROR, error_message='The page layout has been changed')
        else:
            save_result(task.task_id, platform, STATUS_ERROR, error_message='Not found %s' % grab.response.url)


def run():
    spider = FiverrSpider()
    spider.run()


if __name__ == '__main__':
    run()
