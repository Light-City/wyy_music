import json
import re
import urllib.request
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os

driver = webdriver.Chrome()
# timeout:超出时间，等待的最长时间(同时要考虑隐形等待时间)
# 显示等待
wait = WebDriverWait(driver, 5)

class Musci_info(object):
    def __init__(self, id):
        self.id = id

    def get_music_info(self):
        url = "https://music.163.com/#/artist?id={0}".format(self.id)
        driver.get(url)
        driver.switch_to.frame('contentFrame')
        # 获取歌手的姓名，并建立对应文件夹
        artist_name = driver.find_element_by_id('artist-name').text
        print(artist_name)
        path = os.getcwd() + "\\data\\{0}".format(artist_name)
        if not os.path.exists(path):
            os.makedirs(path)

        tr_list = driver.find_element_by_id("hotsong-list").find_elements_by_tag_name("tr")
        music_info = []
        for i in range(len(tr_list)):
            content = tr_list[i].find_element_by_class_name('txt')
            href = content.find_element_by_tag_name('a').get_attribute('href')
            title = content.find_element_by_tag_name('b').get_attribute('title')
            music_info.append((title, href))
        return music_info, path
    def save_csv(self, music_info, path, head=None):
        data = pd.DataFrame(music_info,columns=head)
        # index=False去掉DataFrame默认的index列
        data.to_csv("{0}\\singer{1}.csv".format(path,str(self.id)), encoding="utf-8", index=False)
class Download_Music(object):
    def __init__(self, music_name, music_id, path):
        self.music_name = music_name
        self.music_id = music_id
        self.path = path
    def get_lyric(self):
        url = 'http://music.163.com/api/song/lyric?' + 'id=' + str(self.music_id) + '&lv=1&kv=1&tv=-1'
        r = requests.get(url)
        raw_json = r.text
        ch_json = json.loads(raw_json)
        raw_lyric = ch_json['lrc']['lyric']
        del_str = re.compile(r'\[.*\]')
        ch_lyric = re.sub(del_str, '', raw_lyric)
        return ch_lyric
    def download_mp3(self):
        url = 'http://music.163.com/song/media/outer/url?id=' + str(self.music_id) + '.mp3'
        try:
            print("正在下载：{0}".format(self.music_name))
            urllib.request.urlretrieve(url, '{0}/{1}.mp3'.format(self.path, self.music_name))
            print("Finish...")
        except:
            print("Failed...")

    def save_txt(self):
        lyric = self.get_lyric()
        print("正在写入歌曲：{0}".format(self.music_name))
        print(lyric)
        with open("{0}/{1}.txt".format(self.path, self.music_name), 'w', encoding='utf-8') as f:
            f.write(lyric)


def main(id):
    singer_id = id # 歌手id，自定义修改--根据自己爬取的歌手选择
    mu_info = Musci_info(singer_id) # 类初始化
    music_info, path = mu_info.get_music_info() # 调用方法，获取音乐信息及路径
    print(music_info)
    print(path)
    mu_info.save_csv(music_info, path, head=['music', 'link']) # 存储音乐的歌名及链接至csv文件
    '''
    调用pandas的read_csv()方法时，默认使用C engine作为parser engine，而当文件名中含有中文的时候,就会报错，
    这里一定要设置engine为python，即engine='python'
    '''
    mu_info = pd.read_csv('{0}/singer{1}.csv'.format(path, str(singer_id)), engine='python', encoding='utf-8')

    '''
    通过iterrows遍历音乐信息的music文件
    iterrows返回的是一个元组(index,mu)
    '''
    for index, mu in mu_info.iterrows():
        music = mu['music'] # 取对应的歌曲
        # 通过正则取出歌曲对应的链接中的id
        #
        '''
        提取歌曲id
        方法一：
        re.search 匹配包含
        link = re.search(regex, mu['link']).group()
        匹配后为id=1294910785，前面都为id=刚好3位,index从0开始，
        也就是说[3:]即为所需要的id数据。
        # .*是贪婪模式  尽可能多的匹配数据
        regex = re.compile(r'id=.*') # .*贪婪模式匹配
        link = re.search(regex, mu['link']).group()[3:]
        或者采用以下分组解决
        方法二:
        regex = re.compile(r'(id)(=)(.*)')
        link = re.search(regex, mu['link']).group() # id=1294910785
        link = re.search(regex, mu['link']).group(0) # id=1294910785
        link = re.search(regex, mu['link']).group(1) # id
        link = re.search(regex, mu['link']).group(2) # =
        link = re.search(regex, mu['link']).group(3) # 1294910785
        也就是说直接使用
        regex = re.compile(r'(id)(=)(.*)') 
        link = re.search(regex, mu['link']).group(3)
        便可以实现获取id的效果了
        '''
        regex = re.compile(r'(id)(=)(.*)')
        print('--------------------')
        link = re.search(regex, mu['link']).group(3)
        print('--------------------')
        print(link)
        music = Download_Music(music, link, path)
        music.save_txt()
        music.download_mp3()


if __name__ == '__main__':
    main(5781)

