import argparse
import logging
import tkinter as tk
from tkinter import messagebox

from modules.auth import authenticate
from modules.remote_listing import fetch_remote_listing as fetch_remote_listing_data


logger = logging.getLogger(__name__)


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件下载工具")
        self.root.geometry("560x440")
        self.root.minsize(540, 400)
        self.current_token = None

        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # 登录信息区域
        tk.Label(main_frame, text="账号:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.username_entry = tk.Entry(main_frame, width=50)
        self.username_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 4))

        tk.Label(main_frame, text="密码:").grid(row=1, column=0, sticky="w", pady=4)
        self.password_entry = tk.Entry(main_frame, width=50, show="*")
        self.password_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

        tk.Button(main_frame, text="获取 JWT Token", command=self.fetch_jwt_token).grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(4, 8),
        )

        tk.Label(main_frame, text="JWT Token:").grid(row=3, column=0, sticky="nw")
        self.token_text = tk.Text(main_frame, width=50, height=4, wrap="word", state="disabled")
        self.token_text.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(0, 8))

        # 远程文件列表功能
        tk.Label(main_frame, text="远程路径:").grid(row=4, column=0, sticky="w", pady=4)
        tk.Label(
            main_frame,
            text="https://list.beginner.center/local/rilinic/",
            anchor="w",
            justify="left",
        ).grid(row=4, column=1, sticky="w", pady=4)
        tk.Button(main_frame, text="获取文件列表", command=self.fetch_remote_listing).grid(
            row=4,
            column=2,
            sticky="w",
            padx=(8, 0),
            pady=4,
        )

        tk.Label(main_frame, text="路径密码(可选):").grid(row=5, column=0, sticky="w", pady=4)
        self.remote_password_entry = tk.Entry(main_frame, width=50, show="*")
        self.remote_password_entry.grid(row=5, column=1, columnspan=2, sticky="ew", pady=4)

        self.force_root_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            main_frame,
            text="强制根目录 (force_root)",
            variable=self.force_root_var,
        ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.remote_text = tk.Text(main_frame, width=50, height=8, wrap="word", state="disabled")
        self.remote_text.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(0, 8))

        # 下载相关功能暂未启用

    def fetch_jwt_token(self):
        """调用认证模块获取 token"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("错误", "请输入账号和密码！")
            return

        logger.debug("Attempting login for user '%s'", username)
        token, error = authenticate(username, password)
        if error:
            logger.warning("Login failed for user '%s': %s", username, error)
            messagebox.showerror("错误", error)
            self._update_token_box("未获取到 token")
            self.current_token = None
            return

        self.current_token = token
        self._update_token_box(token)
        logger.debug("登录成功，token 已获取 (长度 %s)", len(token) if token else 0)
        messagebox.showinfo("成功", "已获取 JWT Token")

    def _update_token_box(self, text):
        """在只读文本框中展示 token 或提示信息"""
        self.token_text.config(state="normal")
        self.token_text.delete("1.0", tk.END)
        self.token_text.insert(tk.END, text)
        self.token_text.config(state="disabled")

    def _update_listing_box(self, text):
        """在只读文本框中展示目录列表"""
        self.remote_text.config(state="normal")
        self.remote_text.delete("1.0", tk.END)
        self.remote_text.insert(tk.END, text or "")
        self.remote_text.config(state="disabled")

    def fetch_remote_listing(self):
        """调用远程列表模块请求数据"""
        if not self.current_token:
            logger.debug("Token missing when requesting listing")
            messagebox.showwarning("提示", "请先获取 JWT Token")
            return

        path = "/local/rilinic/"
        password = self.remote_password_entry.get().strip()

        logger.debug(
            "Fetching remote listing: path=%s, password_provided=%s, force_root=%s",
            path,
            bool(password),
            bool(self.force_root_var.get()),
        )

        listing_text, error, token_invalid = fetch_remote_listing_data(
            token=self.current_token,
            path=path,
            password=password,
            force_root=bool(self.force_root_var.get()),
        )

        if token_invalid:
            logger.warning("Token invalidated while fetching listing")
            self.current_token = None
            self._update_token_box("当前 token 已失效，请重新登录")
            messagebox.showwarning("提示", "Token 已失效，请重新获取 JWT Token 后再试")
            self._update_listing_box(listing_text)
            return

        if error:
            logger.error("获取目录失败: %s", error)
            messagebox.showerror("错误", error)
            self._update_listing_box(listing_text)
            return

        self._update_listing_box(listing_text)
        logger.debug("远程文件列表获取成功")
        messagebox.showinfo("成功", "已获取文件列表")

def configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    else:
        root_logger.setLevel(level)
    logger.debug("Logging configured. Debug mode: %s", debug)


def main(debug: bool = False):
    configure_logging(debug)
    logger.debug("Starting DownloaderApp")
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文件下载工具 GUI")
    parser.add_argument("--debug", action="store_true", help="启用调试日志输出")
    args = parser.parse_args()
    main(debug=args.debug)