DouYinSpider
===============
本项目包含两个抖音爬虫：  
第一个为github用户[loadchange](https://github.com/LoadChange/amemv-crawler)的代码，位于amemv-crawler目录下：
```
“ 可以下载指定抖音用户的全部视频(含收藏)，也可以下载指定主题(挑战)或音乐下的全部视频。”
```
但是不能够获取抖音视频的详细信息如小心心数量、评论数目、视频时长、玩家具体信息等  

indepent目录下的本人的代码，通过安卓模拟器，抓取抖音对应视频及视频数据，此项目抓取的目标视频为抖音随机出现的 **竖屏广告** 
实际使用时可以根据自身 **测试学习** 需求修改FlowCatch.py逻辑
## 开发环境
>
>* Python3
>* Android environment
>* Fiddler/Charles
>* Appium
>* Mitmproxy


## 注意

大家好，这个项目是一个**练手项目**，源码仅作为和大家一起**学习Python**使用，你可以免费: 拷贝、分发和派生当前源码。你不可以用于*商业目的*及其他*恶意用途*。

## 环境安装
1. Android environment
    >   * 建议通过[Android Studio](https://developer.android.google.cn/studio/)安装安卓开发环境
    >   * 安卓模拟器: 常用的模拟器有
    >       * genymotion（收费）
    >       * 天天模拟器
    >       * 夜神模拟器
    >       * 领航模拟器
    >       * 这里使用[天天模拟器](http://www.kpzs.com/topic/ttmnqsgou/)作为测试
2. Fiddler/Charles（收费）
    >    * 两个均为抓包工具，这里使用[Fiddler](https://www.telerik.com/download/fiddler)
3. Appium
    >    * [Appium](https://github.com/appium/appium-desktop/releases)，为类似于Selenium的移动端测试工具，建议安装桌面版
    >       <img src="https://github.com/panoslin/DouYinSpider/blob/master/pic/AppiumDownload.png" width="600">
4. Python 依赖库：
    >```bash
    >pip install -r requirement.txt
    >```
## 配置和运行

1. 首先运行天天模拟器，通过adb连接模拟器(天天默认端口*6555*)：在命令行输入
    >```bash
    >adb connect 127.0.0.1:6555
    >adb devices -l
    >adb install douyin.apk
    >```
    >第一步连接模拟器端口，如果端口连接不成功，可到ttmnq\deployed\TianTian.vbox中查看host端口（hostport）  
    >第二步显示是否连接成功，成功则会显示已连接设备信息  
    >第三步安装抖音App  
    >返回结果应该如下图表示连接成功：
    ![adb](https://github.com/panoslin/DouYinSpider/blob/master/pic/adb.jpg)
2. 运行Appium服务器(默认端口*4723*)
3. 进入indepent目录，命令行输入
    >```bash
    >python commander.py
    >python AppiumControl.py
    >```
此时模拟器便被Appium控制，自行打开抖音并且开始没日没夜的刷抖音。 
