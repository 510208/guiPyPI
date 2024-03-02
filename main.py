import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import sys
import logging
from ttkthemes import ThemedTk
import asyncio
import tkinterweb
import markdown

# 載入畫面
splash = ThemedTk(theme="arc")
splash.overrideredirect(True)  # 隱藏標題列和邊框

# 將窗口置中
window_width = 200
window_height = 100
screen_width = splash.winfo_screenwidth()
screen_height = splash.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)

splash.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
# 設定視窗標題
splash_label = ttk.Label(splash, text="guiPip 正在啟動...")
splash_label.pack(padx=20, pady=20)
splash.update()

# 初始化 logging
# logging格式： 行號[時間][模組名稱][日誌等級] - 日誌訊息
logging.basicConfig(
                level=logging.INFO,
                format="%(lineno)d[%(asctime)s][%(module)s][%(levelname)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filemode="w",
                filename="guiPip.log"
            )
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pypi_api").setLevel(logging.DEBUG)

# 初始化 tkinter
root = ThemedTk(theme="arc")
root.withdraw()
root.state("zoomed")
root.title("PyPi GUI")
# 獲取 ttk 風格的預設背景顏色
style = ttk.Style()
default_bg = style.lookup("TFrame", "background")
# 將視窗的背景顏色設定為預設背景顏色
root.configure(bg=default_bg)

# 初始化 PyPiClient
from pypi_api import PyPiClient
client = PyPiClient()

def search_pkg():
    # 清空搜尋結果
    search_result_listbox.delete(*search_result_listbox.get_children())
    # 搜尋套件
    package_name = search_entry.get()
    package = asyncio.run(client.search_package(package_name))
    if package is None or "message" in package:
        messagebox.showerror("搜尋結果", "找不到套件")
        items = [
            "結果",
            "錯誤訊息"
        ]
        values = [
            "查詢套件失敗\n請檢查包名輸入是否正確，當前版本尚未引進模糊搜尋功能",
            package["message"]
        ]
        for i in range(len(items)):
            search_result_listbox.insert("", "end", values=(items[i], values[i]))
        return
    
    # 設定兩項的值
    items = [
                "套件作者",
                "作者電子郵件",
                "授權許可證",
                "概述",
                "最新版本號",
                "Python 版本要求"
            ]
    values = [
                package["info"]["author"],
                package["info"]["author_email"],
                package["info"]["license"],
                package["info"]["summary"],
                package["info"]["version"],
                package["info"]["requires_python"],
            ]
    for i in range(len(items)):
        search_result_listbox.insert("", "end", values=(items[i], values[i]))
    html = markdown.markdown(package["info"]["description"])
    descr_box.load_html(html)
    # 設定輸入框的值
    install_entry.delete(0, "end")
    install_entry.insert(0, package_name)
    remove_entry.delete(0, "end")
    remove_entry.insert(0, package_name)

def install_pkg():
    # 安裝套件
    package_name = install_entry.get()
    result = client.install_package(package_name)
    messagebox.showinfo("安裝結果", result)

def remove_pkg():
    # 移除套件
    package_name = remove_entry.get()
    result = client.remove_package(package_name)
    messagebox.showinfo("移除結果", result)

# 初始化 GUI
# 使用 Grid 方法
# 搜尋框
search_frame = ttk.Frame(root)
search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

search_label = ttk.Label(search_frame, text="搜尋套件：")
search_label.grid(row=0, column=0)

search_entry = ttk.Entry(search_frame, width=75)
search_entry.grid(row=0, column=1)
# 按下Enter鍵時，執行search_pkg函數
search_entry.bind("<Return>", lambda event: search_pkg())
search_frame.grid_columnconfigure(1, weight=1)
# root.grid_rowconfigure(0, weight=1)

search_button = ttk.Button(search_frame, text="搜尋", command=search_pkg)
search_button.grid(row=0, column=2)

# 搜尋結果
search_result_frame = ttk.Frame(root)
search_result_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

search_result_label = ttk.Label(search_result_frame, text="套件資訊：")
search_result_label.grid(row=0, column=0)

search_result_listbox = ttk.Treeview(search_result_frame, columns=["item", "value"], show="headings", height=6)
search_result_listbox.grid(row=1, column=0, sticky="nsew", pady=5)
search_result_listbox.heading("item", text="項目")
search_result_listbox.heading("value", text="內容")
# 建立輸出概述的框，佔據column=1的整行空間
descr_box = tkinterweb.HtmlFrame(search_result_frame, horizontal_scrollbar=True, vertical_scrollbar=True, height=1, width=1, messages_enabled = False)
descr_box.grid(row=2, column=0, sticky="ew")


# 安裝框
install_frame = ttk.Frame(root)
install_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

install_label = ttk.Label(install_frame, text="安裝套件：")
install_label.grid(row=0, column=0)

install_entry = ttk.Entry(install_frame, width=75)
install_entry.grid(row=0, column=1)
# 按下Enter鍵時，執行install_pkg函數
install_entry.bind("<Return>", lambda event: install_pkg())

install_button = ttk.Button(install_frame, text="安裝")
install_button.grid(row=0, column=2)

install_frame.grid_columnconfigure(1, weight=1)

# 移除框
remove_frame = ttk.Frame(root)
remove_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

remove_label = ttk.Label(remove_frame, text="移除套件：")
remove_label.grid(row=0, column=0)

remove_entry = ttk.Entry(remove_frame, width=75)
remove_entry.grid(row=0, column=1)
# 按下Enter鍵時，執行remove_pkg函數
remove_entry.bind("<Return>", lambda event: remove_pkg())

remove_button = ttk.Button(remove_frame, text="移除")
remove_button.grid(row=0, column=2)

remove_frame.grid_columnconfigure(1, weight=1)

# 取得本地套件
def get_local_packages():
    # 清空搜尋結果
    local_listbox.delete(*local_listbox.get_children())
    # 取得本地套件
    packages = asyncio.run(client.get_local_packages())
    # print(packages)
    # 將每個包的名稱和版本號添加到local_listbox中
    if packages is not None:
        for i in range(len(packages["package"])):
            local_listbox.insert("", "end", values=(packages["package"][i], packages["version"][i]))
    else:
        messagebox.showerror("錯誤", "無法取得本地套件或本地無任何可搜索到的套件")

# 本地套件
# 向下延伸兩格
local_frame = ttk.Frame(root)
local_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

local_label = ttk.Label(local_frame, text="本地套件：")
local_label.grid(row=0, column=0)

local_listbox = ttk.Treeview(local_frame, columns=["package", "version"], show="headings", height=6)
local_listbox.grid(row=1, column=0, pady=5)
local_listbox.heading("package", text="套件名稱")
local_listbox.heading("version", text="版本號")

def on_selection_change(event):
    # 獲取當前選擇的選項
    selection = local_listbox.curselection()
    if selection:
        # 獲取選擇的選項的內容
        selected_option = local_listbox.get(selection[0])
        messagebox.showinfo(selected_option)
        # 將選擇的選項的內容設置為remove_entry的內容
        remove_entry.delete(0, "end")
        remove_entry.insert(0, selected_option[0]["package"])

# 綁定on_selection_change函數到<<ListboxSelect>>事件
local_listbox.bind('<<ListboxSelect>>', on_selection_change)

local_button = ttk.Button(local_frame, text="取得本地套件", command=get_local_packages)
# 按鈕靠右
local_button.grid(row=2, column=0, pady=5, sticky="e")

splash.destroy()
root.deiconify()

root.mainloop()