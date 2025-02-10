import os
import requests
import logging
import time
import random
from pathlib import Path
from seting import *

# 确保必要目录存在
Path(image_path).mkdir(parents=True, exist_ok=True)
Path(os.path.dirname(os.path.join(image_path, 'comic_downloader.log'))).mkdir(parents=True, exist_ok=True)

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(image_path, 'comic_downloader.log')),
        logging.StreamHandler()
    ]
)

def format_str(s, base="04"):
    s = str(s)
    l = len(s)
    if l >= int(base[1]):
        return s
    return base[0] * (int(base[1]) - l) + s

def get_md(index: int, title: str, image: str) -> str:
    """生成Markdown文本"""
    return (
        stencil
        .replace("$image$", image)
        .replace("$url$", f"{xkcd_url}/{index}")
        .replace("$title$", title)
        .replace("$index$", str(index))
    )

def write_md(index: int, title: str, image: str):
    """将漫画信息写入Markdown文件"""
    md_file_path = Path(image_path) / f"{format_str(index)}.md"
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(get_md(index, title, image))
    logging.info(f"已写入漫画信息到 {md_file_path}")

def get_latest_number() -> int:
    """获取最新的漫画编号"""
    existing_numbers = [
        int(file.stem) for file in Path(image_path).rglob('*.md')  # 使用 rglob 遍历所有子文件夹
    ]
    latest = max(existing_numbers, default=0)
    logging.info(f"最新的编号是: {latest}")
    return latest

def get_xkcd_comics(start_number: int, count: int = 20):
    """下载 XKCD 漫画"""
    comic_infos = []
    url_template = 'https://xkcd.com/{}/info.0.json'

    for i in range(start_number + 1, start_number + count + 1):
        response = requests.get(url_template.format(i))
        
        if response.status_code == 200:
            comic = response.json()
            title = comic['title']
            write_md(i, title, comic['img'])
            comic_infos.append((i, title, comic['img']))
        else:
            logging.warning(f"请求漫画编号 {i} 时出错: {response.status_code}")

        time.sleep(sleep_time)

    return comic_infos

def organize_comics():
    """整理下载的漫画文件到多级目录结构"""
    folder = Path(image_path)
    all_files = sorted(folder.glob('*.md'), key=lambda x: int(x.stem))  # 按编号排序

    for file in all_files:
        num = int(file.stem)
        
        # 计算三级目录结构
        # 第一层：每1000个一组 (0001-1000, 1001-2000...)
        group_1000_start = ((num - 1) // 1000) * 1000 + 1
        group_1000_end = group_1000_start + 999
        
        # 第二层：每100个一组 (0001-0100, 0101-0200...)
        group_100_start = group_1000_start + ((num - group_1000_start) // 100) * 100
        group_100_end = group_100_start + 99
        
        # 第三层：每10个一组 (0001-0010, 0011-0020...)
        group_10_start = group_100_start + ((num - group_100_start) // 10) * 10
        group_10_end = group_10_start + 9

        # 构建目录路径
        target_dir = (
            folder 
            / f"{group_1000_start:04}-{group_1000_end:04}" 
            / f"{group_100_start:04}-{group_100_end:04}"
            / f"{group_10_start:04}-{group_10_end:04}"
        )
        target_dir.mkdir(parents=True, exist_ok=True)  # 递归创建目录

        # 移动文件
        new_path = target_dir / file.name
        if not new_path.exists():
            file.rename(new_path)
            logging.info(f"已移动: {file.name} 到 {target_dir}")
        else:
            logging.warning(f"文件 {file.name} 已存在于 {target_dir}，跳过移动")

def pick_and_generate_readme(comic_infos):
    """生成 README.md"""
    if len(comic_infos) < 5:
        logging.warning("漫画信息不足，无法生成 README.md")
        return

    latest_comic = max(comic_infos, key=lambda x: x[0])
    random_comics = random.sample(comic_infos, 3)

    readme_content = (
        stencil_readme
        .replace("$new$", get_md(*latest_comic))
        .replace("$random1$", get_md(*random_comics[0]))
        .replace("$random2$", get_md(*random_comics[1]))
        .replace("$random3$", get_md(*random_comics[2]))
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    logging.info("已生成 README.md")

if __name__ == "__main__":
    latest_number = get_latest_number()
    comic_infos = get_xkcd_comics(latest_number, count=max_once)
    organize_comics()
    pick_and_generate_readme(comic_infos)