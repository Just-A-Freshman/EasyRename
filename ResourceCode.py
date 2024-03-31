# -*- coding: utf-8 -*-
import os
import tkinter as tk
from re import findall, search
from tkinter import ttk
from tkinter import filedialog, messagebox, Radiobutton, StringVar


def get_files(directory):
    with os.scandir(directory) as entries:
        return [entry.name for entry in entries if entry.is_file()]


def show_default(param):
    try:
        prefix = int((entry_start_num.get())) - 1
    except (ValueError, TypeError):
        entry_start_num.delete(0, 'end')
        entry_start_num.insert(0, "1")
        prefix = param
    return prefix


def all_number_rename(directory, name_suffix, pre_concat, tail_concat):
    prefix = show_default(0) + 1
    files = temp_rename(directory)
    for old_name in files:
        new_name = f"{pre_concat}{prefix}{tail_concat}{name_suffix}"
        try:
            os.rename(old_name, new_name)  # 最终命名
        except OSError:
            messagebox.showerror(f'命名时出现错误,\n请尝试重新命名!')
            return
        prefix += 1

    messagebox.showinfo("提示", "重命名成功！")


def prefix_suffix_rename(directory, name_suffix, pre_concat, tail_concat):
    # 初始化变量
    prev_get_time = 0
    time_interval = input_interval()
    prefix = show_default(0)
    suffix = 1
    folder_files = temp_rename(directory)

    for old_name in folder_files:
        get_time = os.path.getmtime(old_name)
        # 确定名字
        if (get_time - prev_get_time) > time_interval:
            suffix = 1
            prefix += 1
        else:
            suffix += 1

        new_name = f"{pre_concat}{prefix}-{suffix}{tail_concat}{name_suffix}"
        try:
            os.rename(old_name, new_name)
        except (PermissionError, OSError):
            messagebox.showerror(f'命名时出现错误,\n请尝试重新命名')
            return
        prev_get_time = get_time

    messagebox.showinfo("提示", "重命名成功！")


def temp_rename(director):
    random_bytes = os.urandom(4)
    random_num = int.from_bytes(random_bytes, signed=False, byteorder='big')
    temp_files = get_files(director)
    for index, temp in enumerate(temp_files, random_num):
        os.rename(temp, f'#temp{index}')
    temp_files = get_files(director)
    temp_files.sort(key=lambda x: os.path.getmtime(x))
    return temp_files


def input_interval():
    try:
        time_interval = float(entry_time_interval.get())
    except ValueError:
        entry_time_interval.delete(0, 'end')
        entry_time_interval.insert(0, '5')
        time_interval = 5
    return time_interval


def choose_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_dir.delete(0, 'end')
        entry_dir.insert(0, folder_selected)


def get_files_and_suffix(exp):
    directory = entry_dir.get()
    try:
        if not get_files(directory):
            messagebox.showinfo("提示", "没有找到文件，请检查路径！")
            return
    except FileNotFoundError:
        messagebox.showerror("错误", "文件夹错误，请选择文件夹！")
        return
    os.chdir(directory)  # 改变文件路径，后续就不需要频繁的拼接路径了
    suffix = combobox.get()
    if not suffix or not suffix.startswith('.'):
        messagebox.showerror("错误", "请输入有效的文件后缀，且以点开头！")
        return
    mode = selected_option.get()
    head, tail = '', ''
    if mode == '3':
        if check_expression(exp):
            return
        mode = search(r'{([12])}', exp).group(1)
        concat_list = findall(r'(.*?)\{[12]}(.*)', exp)[0]
        head, tail = concat_list
    if mode == '1':
        prefix_suffix_rename(entry_dir.get(), suffix, head, tail)
    else:
        all_number_rename(entry_dir.get(), suffix, head, tail)


def show_sub_window(old_expression):
    def destroy_sub_window(exp_entry):
        global expression
        expression = exp_entry.get()
        sub_window.destroy()
    sub_window = tk.Toplevel(root)
    sub_window.geometry('390x230+500+300')
    sub_window.resizable(False, False)
    sub_window.title("更多命名方式")
    info = tk.Label(sub_window, font=('宋体', 16), text="提示:{1}代表【前缀-后缀】命名\t\n     {2}代表【纯数字命名】\t\n"
                    "eg: IMG{2} -> IMG1, IMG2, IMG3...\n   【{1}】 -> 【1-1】, 【1-2】...\n\n请输入你指定的命名格式:")
    expression_entry = tk.Entry(sub_window, width=40)
    expression_entry.insert(0, old_expression)
    expression_entry.place(relx=0.1, rely=0.6, relheight=0.15)
    info.place(relx=0, rely=0)
    close_button = tk.Button(sub_window, text="确定", font=('宋体', 16), bg="wheat",
                             command=lambda: destroy_sub_window(expression_entry))
    close_button.place(relx=0.4, rely=0.82, relheight=0.18, relwidth=0.2)


def check_expression(exp):
    if not search(r'{[12]}', exp):
        messagebox.showwarning('来自[更多命名方式]的警告', '您的命名格式不合法,\n未含有: {1} 或 {2}!')
        return True
    elif search(r'[:|<>"?*/\\]', exp):
        messagebox.showwarning('来自[更多命名方式]的警告',
                               '系统命名限制:\n文件名不能包含下列任何字符:\n\\ / : * ? " < > |')
        return True
    else:
        return False


expression = ''
root = tk.Tk()
root.title("批量重命名工具")
root.geometry('390x230+500+300')
root.resizable(False, False)

entry_dir = tk.Entry(root, width=35)
entry_dir.place(relx=0.05, rely=0, relheight=0.13)

button_dir = tk.Button(root, text="选择文件夹", command=choose_directory, bg="wheat")
button_dir.place(relx=0.65, rely=0, relheight=0.13)

label_suffix = tk.Label(root, text="选择文件名后缀(可手动输入)", font=('宋体', 12, 'bold'))
label_suffix.place(relx=0.26, rely=0.17, relheight=0.13)

combobox = ttk.Combobox(root, values=['.jpg', '.png', '.jpeg', '.txt', '.json', '.xlsx', '.pdf', '.wps', '.docx'])
combobox.place(relx=0.05, rely=0.17, relwidth=0.2, relheight=0.13)

label_interval = tk.Label(root, text='<      s前缀相同', font=('宋体', 12, 'bold'))
label_interval.place(relx=0.6, rely=0.48, relheight=0.15)

entry_time_interval = tk.Entry(root, width=5)
entry_time_interval.place(relx=0.66, rely=0.48, relheight=0.15)

# 初始化两个复选框
selected_option = StringVar()
mode1 = Radiobutton(root, text='【前缀-后缀】命名', font=('宋体', 16), bg='gainsboro',
                    variable=selected_option, borderwidth=2, relief='groove', value=1)
mode2 = Radiobutton(root, text='【纯数字】命名   ', font=('宋体', 16), bg='gainsboro',
                    variable=selected_option, borderwidth=2, relief='groove', value=2)
mode3 = Radiobutton(root, text=' 更多命名方式    ', relief='groove', bg='gainsboro',
                    variable=selected_option, font=('宋体', 16), value=3, command=lambda: show_sub_window(expression))
mode1.select()  # 默认情况下勾选第一个模式

mode1.place(relx=0.05, rely=0.48, relheight=0.16, relwidth=0.54)
mode2.place(relx=0.05, rely=0.65, relheight=0.16, relwidth=0.54)
mode3.place(relx=0.05, rely=0.82, relheight=0.16, relwidth=0.54)

label_start_num = tk.Label(root, text='命名起始数字：', font=('宋体', 16, 'bold'))
label_start_num.place(relx=0.05, rely=0.3, relheight=0.16)

entry_start_num = tk.Entry(root, width=10)
entry_start_num.place(relx=0.43, rely=0.32, relheight=0.13, relwidth=0.16)

button_rename = tk.Button(root, text="执行重命名", bg='cyan',  # 触发按钮，首先往get_files_and_suffix传递
                          font=('宋体', 20, 'bold'), command=lambda: get_files_and_suffix(expression))
button_rename.place(relx=0.6, rely=0.65, relheight=0.35, relwidth=0.4)
root.mainloop()
