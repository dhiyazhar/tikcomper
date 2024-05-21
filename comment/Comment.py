import requests
import logging
import csv
from requests import Response
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [ %(levelname)s ]\t:: %(message)s', datefmt="%Y-%m-%dT%H:%M:%S")

class Comment:
    def __init__(self) -> None:
        self.__result: dict = {}
        self.__result["caption"]: str = None
        self.__result["date_now"]: str = None
        self.__result["video_url"]: str = None
        self.__result["comments"]: list = []

    def __format_date(self, milisecond: int) -> str:
        try:
            return datetime.fromtimestamp(milisecond).strftime("%Y-%m-%dT%H:%M:%S")
        except:
            return datetime.fromtimestamp(milisecond / 1000).strftime("%Y-%m-%dT%H:%M:%S")

    def __get_replies(self, commentid: str) -> list:
        [data, i] = [[], 0]

        while(True):
            res: Response = requests.get(f'https://www.tiktok.com/api/comment/list/reply/?aid=1988&comment_id={commentid}&count=9999999&cursor={i * 50}').json()
            
            if(not res['comments']): break

            data += res['comments']
            i += 1

        return self.__filter_comments(data)

    def __filter_comments(self, comments: list) -> list:
        new_comments: list = []

        for comment in comments:
            if comment['share_info']['desc']:
                logging.info(comment['share_info']['desc'])

            new_comment = {
                "username": comment['user']['unique_id'],
                "nickname": comment['user']['nickname'],
                "comment": comment['text'],
                'create_time': self.__format_date(comment['create_time']),
                "avatar": comment['user']['avatar_thumb']['url_list'][0],
                "total_reply": comment.get('reply_comment_total', 0),
                "is_reply": False  
            }

            new_comments.append(new_comment)

            if comment.get('reply_comment_total', 0) > 0:
                replies = self.__get_replies(comment['cid'])
                for reply in replies:
                    reply['is_reply'] = True 
                    new_comments.append(reply)

        return new_comments

    def execute(self, videoid: str, size: int) -> None:
        logging.info(f'Starting Scrapping for video with id {videoid}[{size} - {size + 50}]...')

        res: Response = requests.get(f'https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={videoid}&count=9999999&cursor={size}').json()

        if(res['status_code'] > 0): return logging.error('invalid id video')

        try:
            self.__result['caption'] = res['comments'][0]['share_info']['title']
            self.__result['date_now'] = self.__format_date(res['extra']['now'])
            self.__result['video_url'] = res['comments'][0]['share_info']['url']
            self.__result['comments'] = self.__filter_comments(res['comments'])

        except:
            return logging.error('comments are over')

        return self.__result

    def to_csv(self, output_file: str, videoid: str, all_comments: list):
        csv_file_path = f'{output_file}.csv'
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['username', 'nickname', 'comment', 'create_time', 'avatar', 'total_reply', 'is_reply']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            comment_count = 0
            for comment in all_comments:
                writer.writerow({
                    'username': comment['username'],
                    'nickname': comment['nickname'],
                    'comment': comment['comment'],
                    'create_time': comment['create_time'],
                    'avatar': comment['avatar'],
                    'total_reply': comment['total_reply'],
                    'is_reply': comment.get('is_reply', False)
                })
                comment_count += 1

        logging.info(f'Output CSV data : {csv_file_path} with {comment_count} comments')

# testing
if __name__ == '__main__':
    comment: Comment = Comment()
    comment.execute('717013')