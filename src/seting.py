import os

max_once = 16
sleep_time = 0.25

xkcd_url = "https://xkcd.com/"
image_path = os.path.abspath('image')
readme_path = os.path.abspath('README.md')

stencil = '''### $title$
No.$index$
![图片不见了~~~]($image$)

[原址]($url$) [下载]($image$)

'''

stencil_readme = r'''# XKCD 漫画


> 一部关于浪漫、讽刺、数学和语言的网络漫画

> A webcomic of romance,sarcasm, math, and language


## 最新漫画
$new$

## 随机漫画
$random1$

$random2$

$random3$

[往期漫画](image/)

谢谢您的观看, 如果喜欢这些漫画的话, 
您可以为我的仓库点个星, 也可以去原址支持原作

XKCD原址: [xkcd.com](https://xkcd.com)

'''
