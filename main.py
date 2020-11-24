from threading import Thread
import telebot, sqlite3, datetime, threading, sys
from telebot.types import *
from config import token, admins
from bd_function import *
from insta_function import *

sys.setrecursionlimit(10 ** 6)
bot = telebot.TeleBot(token, threaded=True)

GROUP_ID = []

conn = sqlite3.connect("db/data.db")

start_command = '/start'

"""
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return
"""

def get_list_posts():
    conn = sqlite3.connect("db/data.db")
    c = conn.cursor()
    result = c.execute("SELECT link FROM posts").fetchall()
    result = [i[0] for i in result]
    c.close()
    conn.close()
    return result

@bot.message_handler(func=lambda message: '/link' in message.text and message.chat.id in GROUP_ID)
def repeat_all_messages(message):
    conn = sqlite3.connect("db/data.db")
    c = conn.cursor()
    result = c.execute(
        "SELECT * FROM (SELECT id ,link, referal FROM posts ORDER BY id DESC LIMIT 10) AS T ORDER BY id ASC").fetchall()
    result.reverse()
    text = "Список активных ссылок:"
    count = 1
    if result:
        for r in result:
            if r[2]:
                text += '\n' + str(count) + ')' + " !" + str(r[2]) + " " + str(r[1])
            else:
                text += '\n' + str(count) + ')' + str(r[1])
            count += 1
    c.close()
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: '/start' in message.text and message.chat.id in GROUP_ID)
def repeat_all_messages(message):
    if message.from_user.id not in admins:
        conn = sqlite3.connect("db/data.db")
        c = conn.cursor()
        result = c.execute(
            "SELECT * FROM (SELECT id ,link, referal FROM posts ORDER BY id DESC LIMIT 10) AS T ORDER BY id ASC").fetchall()
        result.reverse()
        check = c.execute("SELECT post FROM liked_posts WHERE user_id = ?", (message.from_user.id,))
        check = [c[0] for c in check]
        if not check:
            text = "Поставьте лайк и напишите комментарий:"
            count = 1
            if result:
                store_liked_post(message.from_user.id, [r[1] for r in result])
                for r in result:
                    if r[2]:
                        text += '\n' + str(count) + ')' + " !" + str(r[2]) + " " + str(r[1])
                    else:
                        text += '\n' + str(count) + ')' + str(r[1])
                    count += 1
            c.close()
            bot.send_message(message.chat.id, text, disable_web_page_preview=True)
        else:
            text = 'Список активных ссылок:\n'
            count = 1
            for p in check:
                text += str(count) + ' - ' + str(p) + '\n'
                count += 1
            bot.send_message(message.chat.id, text, disable_web_page_preview=True)
    else:
        conn = sqlite3.connect("db/data.db")
        c = conn.cursor()
        result = c.execute(
            "SELECT * FROM (SELECT id ,link, referal FROM posts ORDER BY id DESC LIMIT 10) AS T ORDER BY id ASC").fetchall()
        result.reverse()
        text = "Список активных ссылок:"
        count = 1
        if result:
            for r in result:
                if r[2]:
                    text += '\n' + str(count) + ')' + " !" + str(r[2]) + " " + str(r[1])
                else:
                    text += '\n' + str(count) + ')' + str(r[1])
                count += 1
        c.close()
        bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.chat.id in GROUP_ID)
def repeat_all_messages(message):
    print("inst")
    posts_main = get_list_posts()
    if message.text not in posts_main:
        if 'https://www.instagram.com/p/' in message.text:
            if message.from_user.id not in admins:
                conn = sqlite3.connect("db/data.db")
                c = conn.cursor()
                users = c.execute("SELECT user_id FROM users").fetchall()
                users = [int(i[0]) for i in users]
                liked_users = c.execute("SELECT DISTINCT user_id FROM liked_posts").fetchall()
                try:
                    liked_users = [int(r[0]) for r in liked_users]
                except:
                    liked_users = []
                c.close()

                def store_post(message, username, post_link, referal=0):
                    print("store")
                    conn = sqlite3.connect("db/data.db")
                    c = conn.cursor()
                    list_link = c.execute("SELECT post FROM liked_posts WHERE user_id = ?", (message.from_user.id,))
                    list_link = [c[0] for c in list_link]
                    check = False  # !!!!!!!
                    for link in list_link:
                        """
                        twrv = ThreadWithReturnValue(target=check_like_comment, args=(username, link))
                        twrv.start()
                        print(twrv.join())
                        """
                        result_feedback = check_like_comment(username, link)
                        print(result_feedback)
                        if result_feedback:
                            text = "Внимание! Вы не выполнили условия, поэтому я удалил вашу ссылку!\n\n ("
                            for i in result_feedback:
                                text += str(i) + ' '
                            done_count = \
                            c.execute("SELECT count(post) FROM liked_posts WHERE user_id = ?", (message.from_user.id,)).fetchone()[0]
                            done_count = 10 - int(done_count)
                            text += 'Выполнено условий ' + str(done_count) + ' из 10.Проблемная ссылка: ' + str(
                                link) + ')\nСначала выполните условия, а потом кидайте ссылку.'
                            bot.delete_message(message.chat.id, message.message_id)
                            bot.send_message(message.chat.id, text, parse_mode='HTML')
                            check = True
                            break
                        else:
                            delete_liked_post(message.from_user.id, link)

                    if not check:
                        list_of_posts = get_list_posts()
                        print(list_of_posts)
                        if post_link in list_of_posts:
                            bot.send_message(message.chat.id,
                                             'Внимание! Данная ссылка уже есть в моей базе! Пожалуйста, не добавляйте ссылки повторно! Ссылку можно будет добавить повторно, когда она уйдет из списка "активных" ссылок.')
                        else:
                            delete_first_record()
                            if referal == 1:
                                create_post(post_link, None)
                            else:
                                create_post(post_link, None)
                            change_last_visit(message.from_user.id)
                            change_last_visit_username(username)
                            link_result = c.execute("SELECT link FROM posts").fetchall()
                            link_result = [l[0] for l in link_result]
                            link_result.reverse()
                            text = 'Ваша ссылка принята!\n\nСписок активных ссылок:'
                            count = 1
                            for l in link_result:
                                text += '\n' + str(count) + ' - ' + str(l)
                                count += 1
                            bot.send_message(message.chat.id, text)

                last_visit = get_last_visit(message.from_user.id)
                if last_visit:
                    if message.from_user.id in liked_users :
                        if message.text != 'https://www.instagram.com/p/':
                            if 'Прошёл с' in message.text or "Прошел с" in message.text:
                                username = message.text.replace("\n", " ").split(" ")[2][1:]
                                print(username)
                                post_link = message.text.replace("\n", " ").split(" ")[-1]
                                print(post_link)
                                last_visit_username = get_last_visit_username(username)
                                if last_visit_username:
                                    if (datetime.datetime.now() - datetime.datetime.strptime(last_visit_username,
                                                                                             '%Y-%m-%d %H:%M:%S.%f')).total_seconds() // 3600 >= 24:
                                        threading.Thread(target=store_post, args=(message, username, post_link, 1)).start()
                                    else:
                                        l_v = datetime.datetime.strptime(last_visit,
                                                                         '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(
                                            days=1)
                                        l_v = l_v.strftime('%Y-%m-%d %H:%M:%S')
                                        bot.send_message(message.chat.id,
                                                         f'Внимание! Внимание! С момента вашей последней ссылки еще не прошло 24 часа. Напоминаю, что вы можете отправлять ссылку не чаще, чем один раз в 24 часа! Время вашей разблокировки: {l_v}')
                                else:
                                    threading.Thread(target=store_post, args=(message, username, post_link, 1)).start()
                            else:
                                username = get_username_by_post(message.text)
                                if username:
                                    post_link = message.text
                                    last_visit_username = get_last_visit_username(username)
                                    if last_visit_username:
                                        if (datetime.datetime.now() - datetime.datetime.strptime(last_visit_username,
                                                                                                 '%Y-%m-%d %H:%M:%S.%f')).total_seconds() // 3600 >= 24:
                                            threading.Thread(target=store_post, args=(message, username, post_link)).start()
                                        else:
                                            l_v = datetime.datetime.strptime(last_visit,
                                                                             '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(
                                                days=1)
                                            l_v = l_v.strftime('%Y-%m-%d %H:%M:%S')
                                            bot.send_message(message.chat.id,
                                                             f'Внимание! Внимание! С момента вашей последней ссылки еще не прошло 24 часа. Напоминаю, что вы можете отправлять ссылку не чаще, чем один раз в 24 часа! Время вашей разблокировки: {l_v}')
                                    else:
                                        threading.Thread(target=store_post, args=(message, username, post_link)).start()
                                else:
                                    bot.send_message(message.chat.id, "Ссылка не действительна")
                        else:
                            bot.send_message(message.chat.id, 'Неверный формат')
                    elif message.from_user.id not in liked_users:
                        bot.send_message(message.chat.id, f"Нажмите {start_command}, чтобы получить список ссылок")

                else:
                    if message.from_user.id in liked_users:
                        if message.text != 'https://www.instagram.com/p/':
                            if 'Прошёл с' in message.text or "Прошел с" in message.text:
                                print("Переход")

                                username = message.text.replace("\n", " ").split(" ")[2][1:]
                                print(username)
                                post_link = message.text.replace("\n", " ").split(" ")[-1]
                                print(post_link)
                                last_visit_username = get_last_visit_username(username)
                                if last_visit_username:
                                    if (datetime.datetime.now() - datetime.datetime.strptime(last_visit_username,
                                                                                             '%Y-%m-%d %H:%M:%S.%f')).total_seconds() // 3600 >= 24:
                                        threading.Thread(target=store_post, args=(message, username, post_link, 1)).start()
                                    else:
                                        l_v = datetime.datetime.strptime(last_visit,
                                                                         '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(
                                            days=1)
                                        l_v = l_v.strftime('%Y-%m-%d %H:%M:%S')
                                        bot.send_message(message.chat.id,
                                                         f'Внимание! Внимание! С момента вашей последней ссылки еще не прошло 24 часа. Напоминаю, что вы можете отправлять ссылку не чаще, чем один раз в 24 часа! Время вашей разблокировки: {l_v}')
                                else:
                                    threading.Thread(target=store_post, args=(message, username, post_link, 1)).start()
                            else:
                                username = get_username_by_post(message.text)
                                if username:
                                    post_link = message.text
                                    last_visit_username = get_last_visit_username(username)
                                    if last_visit_username:
                                        if (datetime.datetime.now() - datetime.datetime.strptime(last_visit_username,
                                                                                                 '%Y-%m-%d %H:%M:%S.%f')).total_seconds() // 3600 >= 24:
                                            threading.Thread(target=store_post, args=(message, username, post_link)).start()
                                        else:
                                            l_v = datetime.datetime.strptime(last_visit,
                                                                             '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(
                                                days=1)
                                            l_v = l_v.strftime('%Y-%m-%d %H:%M:%S')
                                            bot.send_message(message.chat.id,
                                                             f'Внимание! Внимание! С момента вашей последней ссылки еще не прошло 24 часа. Напоминаю, что вы можете отправлять ссылку не чаще, чем один раз в 24 часа! Время вашей разблокировки: {l_v}')
                                    else:
                                        threading.Thread(target=store_post, args=(message, username, post_link)).start()
                                else:
                                    bot.send_message(message.chat.id, "Ссылка не действительна")
                        else:
                            bot.send_message(message.chat.id, 'Неверный формат')
                    elif message.from_user.id not in liked_users :
                        bot.send_message(message.chat.id, f"Нажмите {start_command}, чтобы получить список ссылок")
            else:
                def store_post(message, post_link, referal=0):
                    conn = sqlite3.connect("db/data.db")
                    c = conn.cursor()
                    list_of_posts = get_list_posts()
                    print(list_of_posts)
                    if post_link in list_of_posts:
                        bot.send_message(message.chat.id,
                                         'Внимание! Данная ссылка уже есть в моей базе! Пожалуйста, не добавляйте ссылки повторно! Ссылку можно будет добавить повторно, когда она уйдет из списка "активных" ссылок.')
                    else:
                        delete_first_record()
                        if referal == 1:
                            create_post(post_link, None)
                        else:
                            create_post(post_link, None)
                        link_result = c.execute("SELECT link FROM posts").fetchall()
                        link_result = [l[0] for l in link_result]
                        link_result.reverse()
                        text = 'Ваша ссылка принята!\n\nСписок активных ссылок:'
                        count = 1
                        for l in link_result:
                            text += '\n' + str(count) + ' - ' + str(l)
                            count += 1
                        bot.send_message(message.chat.id, text)

                if message.text != 'https://www.instagram.com/p/':
                    if 'Прошёл с' in message.text or "Прошел с" in message.text:
                        username = message.text.replace("\n", " ").split(" ")[2][1:]
                        post_link = message.text.replace("\n", " ").split(" ")[-1]
                        store_post(message, post_link, 1)
                    else:
                        username = get_username_by_post(message.text)
                        post_link = message.text
                        store_post(message, post_link)
                else:
                    bot.send_message(message.chat.id, 'Неверный формат')
    else:
        bot.send_message(message.chat.id,
                         'Внимание! Данная ссылка уже есть в моей базе! Пожалуйста, не добавляйте ссылки повторно! Ссылку можно будет добавить повторно, когда она уйдет из списка "активных" ссылок.')


if __name__ == '__main__':
    # bot.polling(none_stop=True)
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)