import threading
from insta import *
import instaloader as instaloader


def check_like_comment(username, link):
    #print("")
    L = instaloader.Instaloader(sleep=False)  # nalazenje stvari sa instagrama

    #bot = InstaBot('like_jony123', 'zxcvbnmlp')
    list_likes = [likee.username for likee in instaloader.Post.from_shortcode(L.context, link.split('/')[4]).get_likes()]
    #list_likes= bot.get_likes(link)
    list_comments = [[comment.text, comment.owner.username] for comment in
                     instaloader.Post.from_shortcode(L.context, link.split('/')[4]).get_comments()]
    result_list = []

    try:
        if username not in list_likes:
            result_list.append('Нет лайка.')
    except:
        pass

    if username not in [p[1] for p in list_comments]:
        result_list.append('Нет комментария.')
    else:
        for i in list_comments:
            if i[1] == username:
                if len(i[0].replace(' ', '')) < 10 or len(i[0].split(' ')) < 4:
                    result_list.append(
                        'Недостаточно символов или слов в комментарии (как минимум 4 слов, не менее 10 символов).')
                else:
                    try:
                        result_list.remove(
                        'Недостаточно символов или слов в комментарии (как минимум 4 слов, не менее 10 символов).')
                    except:
                        pass


    return result_list


def get_username_by_post(link):
    try:
        link = instaloader.Post.from_shortcode(instaloader.Instaloader(sleep=False).context,
                                           link.split('/')[4])
        return link.owner_username
    except:
        return False




