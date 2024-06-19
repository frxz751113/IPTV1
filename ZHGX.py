import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
###urls城市根据自己所处地理位置修改
urls = [
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJoZWJlaSI%3D",  # c河北
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcG9ydD0iODg4OCI%3D",#8888
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcG9ydD0iODA5MCI%3D",#8090
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcG9ydD0iODgi",#88
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcG9ydD0iODgi",#809
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgY2l0eT0iVGFpJ2FuIg%3D%3D",#泰安
    
]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/ZHGXTV/Public/json/live_interface.txt"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    try:
        # 创建一个Chrome WebDriver实例
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
        driver = webdriver.Chrome(options=chrome_options)
        # 使用WebDriver访问网页
        driver.get(url)  # 将网址替换为你要访问的网页地址
        time.sleep(10)
        # 获取网页内容
        page_content = driver.page_source
    
        # 关闭WebDriver
        driver.quit()
    
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
        urls_all = re.findall(pattern, page_content)
        # urls = list(set(urls_all))  # 去重得到唯一的URL列表
        urls = set(urls_all)  # 去重得到唯一的URL列表
        x_urls = []
        for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
            url = url.strip()
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}"
            x_url = f"{base_url}{modified_ip}{port}"
            x_urls.append(x_url)
        urls = set(x_urls)  # 去重得到唯一的URL列表
    
        valid_urls = []
        #   多线程获取可用url
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for url in urls:
                url = url.strip()
                modified_urls = modify_urls(url)
                for modified_url in modified_urls:
                    futures.append(executor.submit(is_url_accessible, modified_url))
    
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_urls.append(result)
    
        for url in valid_urls:
            print(url)
        # 遍历网址列表，获取JSON文件并解析
        for url in valid_urls:
            try:
                # 发送GET请求获取JSON文件，设置超时时间为0.5秒
                json_url = f"{url}"
                response = requests.get(json_url, timeout=1)
                json_data = response.content.decode('utf-8')
                try:
                    # 按行分割数据
                    lines = json_data.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            name, channel_url = line.split(',')
                            urls = channel_url.split('/', 3)
                            url_data = json_url.split('/', 3)
                            if len(urls) >= 4:
                                urld = (f"{urls[0]}//{url_data[2]}/{urls[3]}")
                            else:
                                urld = (f"{urls[0]}//{url_data[2]}")
                            print(f"{name},{urld}")
                            if name and urld:
                                # 删除特定文字
                                name = name.replace("cctv", "CCTV")
                                name = name.replace("中央", "CCTV")
                                name = name.replace("央视", "CCTV")
                                name = name.replace("高清", "")
                                name = name.replace("超高", "")
                                name = name.replace("HD", "")
                                name = name.replace("标清", "")
                                name = name.replace("频道", "")
                                name = name.replace("-", "")
                                name = name.replace(" ", "")
                                name = name.replace("PLUS", "+")
                                name = name.replace("＋", "+")
                                name = name.replace("(", "")
                                name = name.replace(")", "")
                                name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                                name = name.replace("CCTV1综合", "CCTV1")
                                name = name.replace("CCTV2财经", "CCTV2")
                                name = name.replace("CCTV3综艺", "CCTV3")
                                name = name.replace("CCTV4国际", "CCTV4")
                                name = name.replace("CCTV4中文国际", "CCTV4")
                                name = name.replace("CCTV4欧洲", "CCTV4")
                                name = name.replace("CCTV5体育", "CCTV5")
                                name = name.replace("CCTV6电影", "CCTV6")
                                name = name.replace("CCTV7军事", "CCTV7")
                                name = name.replace("CCTV7军农", "CCTV7")
                                name = name.replace("CCTV7农业", "CCTV7")
                                name = name.replace("CCTV7国防军事", "CCTV7")
                                name = name.replace("CCTV8电视剧", "CCTV8")
                                name = name.replace("CCTV9记录", "CCTV9")
                                name = name.replace("CCTV9纪录", "CCTV9")
                                name = name.replace("CCTV10科教", "CCTV10")
                                name = name.replace("CCTV11戏曲", "CCTV11")
                                name = name.replace("CCTV12社会与法", "CCTV12")
                                name = name.replace("CCTV13新闻", "CCTV13")
                                name = name.replace("CCTV新闻", "CCTV13")
                                name = name.replace("CCTV14少儿", "CCTV14")
                                name = name.replace("CCTV15音乐", "CCTV15")
                                name = name.replace("CCTV16奥林匹克", "CCTV16")
                                name = name.replace("CCTV17农业农村", "CCTV17")
                                name = name.replace("CCTV17农业", "CCTV17")
                                name = name.replace("CCTV5+体育赛视", "CCTV5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV5+")
                                name = name.replace("CCTV5+体育", "CCTV5+")
                                results.append(f"{name},{urld}")
                except:
                    continue
            except:
                continue
    except:
        continue

results = set(results)   # 去重得到唯一的URL列表
results = sorted(results)
with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)


                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('卫视频道1,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('省市频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '湖北' in channel_name or '武汉' in channel_name  or '黑龙江' in channel_name or '湖南' in channel_name or '南宁' in channel_name or '河北' in channel_name or '广东' in channel_name or '广西' in channel_name or '石家庄' in channel_name:
          if 'CCTV' not in channel_name and '卫视' not in channel_name and '购物' not in channel_name:  
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    



    channel_counters = {}
    file.write('港澳频道1,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '龙祥' in channel_name or '翡翠' in channel_name or '酒店' in channel_name or 'AXN' in channel_name or '东森' in channel_name or '莲花' in channel_name or '天映' in channel_name or '好莱坞' in channel_name or '星河' in channel_name or '私人' in channel_name or '哔哩' in channel_name or '凤凰' in channel_name:
          #if 'CCTV' not in channel_name and '卫视' not in channel_name and 'TV' not in channel_name and '儿' not in channel_name and '文' not in channel_name and 'CHC' not in channel_name and '新' not in channel_name and '山东' not in channel_name and '河北' not in channel_name and '哈哈' not in channel_name and '临沂' not in channel_name and '公共' not in channel_name and 'CETV' not in channel_name and '交通' not in channel_name and '冬' not in channel_name and '梨园' not in channel_name and '民生' not in channel_name and '综合' not in channel_name and '法制' not in channel_name and '齐鲁' not in channel_name and '自办' not in channel_name and '都市' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1


    channel_counters = {}
    file.write('少儿频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卡通' in channel_name or '少儿' in channel_name or '哈哈' in channel_name or '动漫' in channel_name:
          if 'CCTV' not in channel_name and '卫视' not in channel_name and '湖' not in channel_name and '广' not in channel_name and '河' not in channel_name and '黑' not in channel_name and '保' not in channel_name and '宁' not in channel_name and '家庭' not in channel_name and '影迷' not in channel_name and '动作' not in channel_name and '武汉' not in channel_name and 'CETV' not in channel_name and '交通' not in channel_name and '冬' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

    channel_counters = {}
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        #if '卡通' in channel_name or '少儿' in channel_name or '哈哈' in channel_name or '动漫' in channel_name:
        if 'CCTV' not in channel_name and '卫视' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1









      
# 合并自定义频道文件内容
file_contents = []
file_paths = ["GAT.txt", "hn.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的文件
with open("酒店源.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
for line in fileinput.input("酒店源.txt", inplace=True):  #打开文件，并对其进行关键词原地替换 
    line = line.replace("AA", "")
    line = line.replace("\n电影,", "\n影迷电影,")
    print(line, end="")  #设置end=""，避免输出多余的换行符  

#########原始顺序去重，以避免同一个频道出现在不同的类中
with open('酒店源.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('酒店源.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
#####################


os.remove("iptv.txt")
print("任务运行完毕")
