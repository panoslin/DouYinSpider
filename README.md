DouYinSpider
===============
此Github包含三个抖音爬虫： 
 
第一个为indepent目录下的模拟器版本，通过安卓模拟器，抓取抖音对应视频信息，此项目抓取的目标视频为抖音随机出现的 **竖屏广告** 
实际使用时可以根据自身 **测试学习** 需求修改FlowCatch.py逻辑  
  
第二个为douyin\_api\_feed目录下的API版本， 通过douyin的feed API (https://api.amemv.com/aweme/v1/feed/)获取视频信息。

二者比较， 第一个使用模拟器+Appium 可以很好的模拟真实浏览抖音的情况，并且不需要考虑加密参数的问题，但是占用较多的系统资源，效率低。第二个直接使用API请求json数据，能够极大的减少系统资源的占用，并且效率更高，除了Python以外不需要额外的依赖环境。  
  
第三个为github用户[loadchange](https://github.com/LoadChange/amemv-crawler)的代码，位于amemv-crawler目录下：
```
“ 可以下载指定抖音用户的全部视频(含收藏)，也可以下载指定主题(挑战)或音乐下的全部视频。”
```  
其优势为爬取速度快，系统资源占用少，但是不能够筛选特定的视频，如此项目的仅下载 **竖屏广告**   


### 以下分别对第1、2个爬虫展开讨论： 

#### 注意

这个项目是一个**练手项目**，源码仅作为和大家一起**学习Python**使用，你可以免费: 拷贝、分发和派生当前源码。你不可以用于*商业目的*及其他*恶意用途*。



  
  
###  1. 模拟器版本

#### 开发环境

>* Python3
>* Android environment
>* Appium
>* Mitmproxy




#### 环境安装
1. Android environment
    >   * 建议通过[Android Studio](https://developer.android.google.cn/studio/)安装JDK，配置[环境变量](https://blog.csdn.net/zeternityyt/article/details/79655150)
    >   * 安装JAVA [SDK](https://blog.csdn.net/u012382791/article/details/50891044)
    >   * 安卓模拟器: 常用的模拟器有
    >       * genymotion（收费）
    >       * 天天模拟器
    >       * 夜神模拟器
    >       * 领航模拟器
    >       * 这里使用[天天模拟器](http://www.kpzs.com/topic/ttmnqsgou/)作为测试
2. Appium
    >    * [Appium](https://github.com/appium/appium-desktop/releases)，为类似于Selenium的移动端测试工具，建议安装桌面版
    >       <img src="https://github.com/panoslin/DouYinSpider/blob/master/pic/AppiumDownload.png" width="600">
3. Python 依赖库：
    >```bash
    >pip install -r requirement.txt
    >```
#### 配置和运行

1. 首先运行天天模拟器，通过adb连接模拟器(天天默认端口*6555*)：在命令行输入
    >```bash
    >adb connect 127.0.0.1:6555
    >adb devices -l
    >```
    >第一步连接模拟器端口，如果端口连接不成功，可到ttmnq\deployed\TianTian.vbox中查看host端口（hostport）  
    >第二步显示是否连接成功，成功则会显示已连接设备信息  
    >返回结果应该如下图表示连接成功：
    ![adb](https://github.com/panoslin/DouYinSpider/blob/master/pic/adb.jpg)  
2. 通过模拟器内的“靠谱游戏”安装抖音App  
3. 安装Mitmproxy证书  
    > * 将C:\Users\UserName\\.mitmproxy 目录下面的mitmproxy-ca-cert.cer拖动到模拟器界面上安装证书  
    > * 双击运行安装mitmproxy-ca-cert.p12，选择证书存储位置为“受信任的根证书颁发机构”
4. 运行Appium服务器(默认端口*4723*)
5. 分别开启两个命令行窗口，激活虚拟环境，进入indepent目录，命令行输入
    >```bash
    >python AppiumControl.py
    >mitmdump -s .\FlowCatcher.py
    >```
    >此时模拟器便被Appium控制，自行打开抖音并且开始没日没夜的刷抖音。  
    >   <img src="https://github.com/panoslin/DouYinSpider/blob/master/pic/douyin.jpg" width="300">



###  2. API版本
#### 开发环境
>* Python3

#### 环境安装

1. Python 依赖库：  

>```bash
>pip install -r requirement.txt
>```


#### 配置和运行

1. douyin\_api\_feed目录下包含了一个示例运行文件 (example.py) 与示例配置文件 (sample_config.ini)，在命令行窗口直接运行```python example.py```，窗口首先会输出API返回的完整json数据，然后会连续输出6条通过**feed\_api/parser.py**整理过后的抖音视频数据。


#### 代码解析

通过**parser**整理完json数据之后，便需要考虑录入数据库与上传视频文件。  
  
你可以根据自身需求修改一下代码：

1. 入库  
**feed_api/database_operation.py**封装了入库的SQL语句，并且使用**feed_api/mysql_switch.py**作为装饰器将所有SQL语句作为一个事务一并提交    

2. 上传文件  
这里通过阿里云对象存储OSS作为例子：**feed\_api/integratedos.py**封装了两个方**merge_dir(old\_dst, new\_dst)**将old\_dst目录下的文件与子目录移动至new\_dst目录下**read_status(path=None, simulate=True)**通过oss的上传工具获得当前的上传状态，path为上传工具所在路径


