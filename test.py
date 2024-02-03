import requests
from pprint import pprint
from datetime import datetime
import csv

header = ['ru_name', 'reply_time', 'reply_content']
YOUTUBE_API_KEY = "AIzaSyCtBckVbVCmGNjuk4u5ZuHvO49LTEGooQ0"


def main():

    f = open('comments.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(header)

    # youtube_channel_id = "UCMTklC9mjGdMZtGQjL7pppQ"
    # https://www.youtube.com/watch?v=ILysnoMdH9Y
    # https://www.youtube.com/watch?v=kDsJ4DITmzo
    youtube_channel_id = "kDsJ4DITmzo"

    youtube_spider = YoutubeSpider(YOUTUBE_API_KEY)
    uploads_id = youtube_spider.get_channel_uploads_id(youtube_channel_id)
    # print(uploads_id)

    video_ids = youtube_spider.get_playlist(uploads_id, max_results=5)
    # print(video_ids)

    # for video_id in video_ids:
    #     print("----------------------")
    #     video_info = youtube_spider.get_video(video_id)
    #     print(video_info)

    #     next_page_token = ''
    #     while 1:
    #         comments, next_page_token = youtube_spider.get_comments(video_id, page_token=next_page_token)
    #         print(comments)
    #         # 如果沒有下一頁留言，則跳離
    #         if not next_page_token:
    #             break

    print("Start to get comments")

    video_id = "xSDMTIe90AY"
    next_page_token = ''
    while 1:
        comments, next_page_token = youtube_spider.get_comments(video_id, page_token=next_page_token)
        # print(comments)
        # save to file
        with open("comments.csv", "a") as f:
            for comment in comments:
                data=[comment['ru_name'], comment['reply_time'], comment['reply_content'], comment['rm_positive']]
                writer.writerow(data)

        # 如果沒有下一頁留言，則跳離
        if not next_page_token:
            break

    # close the file
    f.close()
    print("Finish getting comments")


class YoutubeSpider():
    def __init__(self, api_key):
        self.base_url = "https://www.googleapis.com/youtube/v3/"
        self.api_key = api_key

    def get_html_to_json(self, path):
        """組合 URL 後 GET 網頁並轉換成 JSON"""
        api_url = f"{self.base_url}{path}&key={self.api_key}"
        r = requests.get(api_url)
        if r.status_code == requests.codes.ok:
            data = r.json()
        else:
            data = None
        return data

    def get_channel_uploads_id(self, channel_id, part='contentDetails'):
        """取得頻道上傳影片清單的ID"""
        # UC7ia-A8gma8qcdC6GDcjwsQ
        path = f'channels?part={part}&id={channel_id}'
        data = self.get_html_to_json(path)
        try:
            uploads_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        except KeyError:
            uploads_id = None
        return uploads_id

    def get_playlist(self, playlist_id, part='contentDetails', max_results=10):
        """取得影片清單ID中的影片"""
        # UU7ia-A8gma8qcdC6GDcjwsQ
        path = f'playlistItems?part={part}&playlistId={playlist_id}&maxResults={max_results}'
        data = self.get_html_to_json(path)
        if not data:
            return []

        video_ids = []
        for data_item in data['items']:
            video_ids.append(data_item['contentDetails']['videoId'])
        return video_ids

    def get_video(self, video_id, part='snippet,statistics'):
        """取得影片資訊"""
        # jyordOSr4cI
        # part = 'contentDetails,id,liveStreamingDetails,localizations,player,recordingDetails,snippet,statistics,status,topicDetails'
        path = f'videos?part={part}&id={video_id}'
        data = self.get_html_to_json(path)
        if not data:
            return {}
        # 以下整理並提取需要的資料
        data_item = data['items'][0]

        try:
            # 2019-09-29T04:17:05Z
            time_ = datetime.strptime(data_item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # 日期格式錯誤
            time_ = None

        url_ = f"https://www.youtube.com/watch?v={data_item['id']}"

        info = {
            'id': data_item['id'],
            'channelTitle': data_item['snippet']['channelTitle'],
            'publishedAt': time_,
            'video_url': url_,
            'title': data_item['snippet']['title'],
            'description': data_item['snippet']['description'],
            'likeCount': data_item['statistics']['likeCount'],
            # 'dislikeCount': data_item['statistics']['dislikeCount'],
            'commentCount': data_item['statistics']['commentCount'],
            'viewCount': data_item['statistics']['viewCount']
        }
        return info

    def get_comments(self, video_id, page_token='', part='snippet', max_results=100):
        """取得影片留言"""
        # jyordOSr4cI
        path = f'commentThreads?part={part}&videoId={video_id}&maxResults={max_results}&pageToken={page_token}'
        data = self.get_html_to_json(path)
        if not data:
            return [], ''
        # 下一頁的數值
        next_page_token = data.get('nextPageToken', '')

        # 以下整理並提取需要的資料
        comments = []
        for data_item in data['items']:
            data_item = data_item['snippet']
            top_comment = data_item['topLevelComment']
            # print(data_item)
            # print(top_comment)
            try:
                # 2020-08-03T16:00:56Z
                time_ = datetime.strptime(top_comment['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # 日期格式錯誤
                time_ = None

            if 'authorChannelId' in top_comment['snippet']:
                ru_id = top_comment['snippet']['authorChannelId']['value']
            else:
                ru_id = ''

            ru_name = top_comment['snippet'].get('authorDisplayName', '')
            if not ru_name:
                ru_name = ''

            comments.append({
                'reply_id': top_comment['id'],
                'ru_id': ru_id,
                'ru_name': ru_name,
                'reply_time': time_,
                'reply_content': top_comment['snippet']['textOriginal'],
                'rm_positive': int(top_comment['snippet']['likeCount']),
                'rn_comment': int(data_item['totalReplyCount'])
            })
        return comments, next_page_token


if __name__ == "__main__":
    main()