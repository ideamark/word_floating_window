# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as messagebox
import xml.etree.ElementTree as ET
import pandas as pd
import os
import sys
import time
import random
import docx
import sqlite3


class Dictionary:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def search(self, word):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT word, translation FROM stardict WHERE word = '{word}'")
        result = cursor.fetchone()
        cursor.close()
        return result[1]

    def __del__(self):
        self.conn.close()


# 窗口居中显示
def display_in_center(window, window_size=(200,100), window_offset=(0,0)):
    window_width = window_size[0]
    window_height = window_size[1]
    screen_width = window.winfo_screenwidth() + window_offset[0]
    screen_height = window.winfo_screenheight() + window_offset[1]
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    return window_width, window_height

def show_help():
    help_window = tk.Toplevel()
    help_window.title("帮助")
    help_text = '''
单词浮窗 v0.0.1 

这是一款可以置顶循环播放单词的背单词工具
只需导入单词表文件，点击开始即可播放
单词表文件制作方法：每行一个单词，无需释义
支持多种文件类型：docx, doc, xlsx, xls, txt, csv, 有道xml

作者：Mark Yang
邮箱：ideamark@qq.com
'''
    help_label = tk.Label(help_window, text=help_text)
    help_label.pack(padx=10, pady=10)
    display_in_center(help_window, (400, 200))


def read_docx_lines(file_path):
    doc = docx.Document(file_path)
    lines = []
    for paragraph in doc.paragraphs:
        line = paragraph.text.strip()
        if line:  # 去除空行
            lines.append(line)
    return lines


def read_youdao_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    words = []
    for item in root.findall('item'):
        words.append(item.find('word').text.strip())
        # trans = item.find('trans').text.strip()
    return words


def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)
        file_name = file_path.split("/")[-1]
        file_path_label.config(text=file_name)


def get_word_list(file_path):
    ext = os.path.splitext(file_path)[1]
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
            return df.iloc[:, 0].tolist()
        elif ext == '.xls' or ext == '.xlsx':
            df = pd.read_excel(file_path)
            return df.iloc[:, 0].tolist()
        elif ext == '.doc' or ext == '.docx':
            return read_docx_lines(file_path)
        elif ext == '.xml':
            return read_youdao_xml(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()
                return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", "读取文件出错")
        root.destroy()


def rotate_words(root=None, dictionary=None, file_path='', delay_time=2, is_random=False, auto_play=False):
    root.title("")  # 设置窗口标题为空字符串
    window_width, window_height = display_in_center(root, (400, 75), (0, 60))

    word_label = tk.Label(root, font=('Arial', 28))
    definition_label = tk.Label(root, font=('Arial', 16))
    word_label.pack()
    definition_label.pack()

    word_list = get_word_list(file_path)
    current_index = 0
    if is_random:
        random.shuffle(word_list)

    def show_word(index):
        word = word_list[index]
        word_label.config(text=word)
        definition_label.config(text=dictionary.search(word))
        word_label_height = word_label.winfo_reqheight()
        definition_label_height = definition_label.winfo_reqheight()
        if word_label_height + definition_label_height > window_height:
            root.geometry(f'{window_width}x{word_label_height + definition_label_height + 10}')
        else:
            root.geometry(f'{window_width}x{window_height}')
        root.update()

    def on_left_key(event):
        nonlocal current_index
        current_index = (current_index - 1) % len(word_list)
        show_word(current_index)

    def on_right_key(event):
        nonlocal current_index
        current_index = (current_index + 1) % len(word_list)
        show_word(current_index)

    root.bind('<Left>', on_left_key)
    root.bind('<Right>', on_right_key)

    if auto_play:
        while root.winfo_exists():
            current_index = (current_index + 1) % len(word_list)
            show_word(current_index)
            time.sleep(delay_time)
    else:
        show_word(current_index)


def start_rotate_words(dictionary):
    file_path = file_path_var.get()
    delay_time = int(delay_time_entry.get())
    is_random = is_random_var.get()
    auto_play = auto_play_var.get()
    if not file_path:
        messagebox.showerror("Error", "请先导入单词表文件")
        return
    rotate_words_window = tk.Toplevel()
    rotate_words_window.wm_attributes("-topmost", True)
    rotate_words_window.wm_attributes("-alpha", 0.8)  # 设置窗口透明度为80%
    rotate_words(rotate_words_window, dictionary, file_path, delay_time, is_random, auto_play)


if __name__ == '__main__':

    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    db_path = os.path.join(base_path, 'stardict.db')
    dictionary = Dictionary(db_path)

    root = tk.Tk()
    root.title("单词浮窗")
    root.wm_attributes("-alpha", 0.95)
    display_in_center(root, (200, 320))

    file_path_var = tk.StringVar()
    file_path_var.set("")

    file_path_frame = tk.Frame(root)
    file_path_frame.pack()

    browse_button = tk.Button(file_path_frame, text="导入单词表", command=browse_file)
    browse_button.pack(pady=(20, 0))  # 设置上边距为20

    file_path_label = tk.Label(file_path_frame, text="", width=30)
    file_path_label.pack(side=tk.LEFT, padx=(10, 0))  # 设置左边距为10

    is_random_var = tk.BooleanVar()
    is_random_checkbox = tk.Checkbutton(root, text="随机顺序", variable=is_random_var)
    is_random_checkbox.pack(pady=(10, 0))  # 设置上边距为10

    auto_play_var = tk.BooleanVar()
    auto_play_checkbox = tk.Checkbutton(root, text="自动播放", variable=auto_play_var)
    auto_play_checkbox.pack(pady=(10, 0))  # 设置上边距为10

    delay_time_label = tk.Label(root, text="播放间隔/秒")
    delay_time_label.pack(pady=(10, 0))  # 设置上边距为10

    delay_time_entry = tk.Entry(root, width=3)
    delay_time_entry.pack(padx=10)  # 设置水平内边距为10
    delay_time_entry.insert(tk.END, "2")
    delay_time_entry.config(state=tk.DISABLED)

    start_button = tk.Button(root, text="开始", command=lambda: start_rotate_words(dictionary))
    start_button.pack(pady=(20, 0))  # 设置上边距为20

    help_button = tk.Button(root, text="帮助", command=show_help)
    help_button.pack(pady=(20, 0))  # 设置上边距为20

    def update_delay_time_entry_state():
        if auto_play_var.get():
            delay_time_entry.config(state=tk.NORMAL)
        else:
            delay_time_entry.config(state=tk.DISABLED)

    auto_play_var.trace('w', lambda *args: update_delay_time_entry_state())  # 监听auto_play_var变量的变化

    root.mainloop()
