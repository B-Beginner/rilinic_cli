import tkinter as tk
from tkinter import filedialog, messagebox
from modules.downloader import download_file

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件下载工具")
        self.root.geometry("500x200")

        # URL 输入框
        tk.Label(root, text="文件 URL:").pack(pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # 保存路径选择按钮
        tk.Label(root, text="保存路径:").pack(pady=5)
        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack(pady=5)
        tk.Button(root, text="选择路径", command=self.choose_path).pack(pady=5)

        # 下载按钮
        tk.Button(root, text="下载", command=self.start_download).pack(pady=10)

    def choose_path(self):
        """选择保存路径"""
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def start_download(self):
        """开始下载"""
        url = self.url_entry.get()
        save_path = self.path_entry.get()

        if not url or not save_path:
            messagebox.showerror("错误", "请填写 URL 和保存路径！")
            return

        try:
            download_file(url, save_path)
            messagebox.showinfo("成功", "文件下载完成！")
        except Exception as e:
            messagebox.showerror("错误", f"下载失败: {e}")


def main():
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()