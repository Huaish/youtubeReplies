from curses import window
import tkinter
from tkinter import Entry, messagebox
import requests
from pprint import pprint
from datetime import datetime
import csv
from urllib.parse import urlparse
from urllib.parse import parse_qs
from tkinter import filedialog


def main():

    window = tkinter.Tk()
    window.title("Youtube Comments Downloader")
    window.geometry("500x500")

    urlTextBox = tkinter.Text(window,height = 5,width = 500)
    urlTextBox.pack()

    def button_event():
        file = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        try:
            parsed_url = urlparse(urlTextBox.get(1.0, "end-1c"))
            video_id = parse_qs(parsed_url.query)['v'][0]
        except:
            messagebox.showerror("Error", "Invalid URL")
            return

        get_comments(video_id, file)

    getButton = tkinter.Button(window,text = "Get comments", command = button_event)
    getButton.pack()

    window.geometry("500x500+1+1")
    window.bind_all("<Key>", _onKeyRelease, "+")


    window.mainloop()

def get_comments(video_id, file="comments.csv"):
    tkinter.messagebox.showinfo("Info", "Start to get comments")
    headerName = ['姓名', '回覆時間', '回覆內容', '按讚數量']
    YOUTUBE_API_KEY = "AIzaSyCtBckVbVCmGNjuk4u5ZuHvO49LTEGooQ0"

    f = open(file, "w+")
    dataStr =  ",".join(headerName)
    f.write(dataStr)
    f.write("\n")

    youtube_spider = YoutubeSpider(YOUTUBE_API_KEY)
    next_page_token = ''
    while 1:
        comments, next_page_token = youtube_spider.get_comments(video_id, page_token=next_page_token)
        for comment in comments:
            data=[comment['ru_name'], comment['reply_time'].strftime("%m/%d/%Y %H:%M:%S"), comment['reply_content'], str(comment['rm_positive'])]
            dataStr =  ",".join(data)
            f.write(dataStr)
            f.write("\n")
        if not next_page_token:
            break

    f.close()
    tkinter.messagebox.showinfo("Info", "Finish getting comments")

def _onKeyRelease(event):
    ctrl  = (event.state & 0x4) != 0
    if event.keycode==88 and  ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode==86 and  ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

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