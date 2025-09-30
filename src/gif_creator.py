#!/usr/bin/env python3
"""
アニメーションGIF作成ツール

複数の画像ファイルを選択し、それらからアニメーションGIFを作成するプログラムです。
Tkinterを使用してファイル選択UIを提供し、PillowライブラリでGIFアニメーションを生成します。

使用方法:
    python gif_creator.py

機能:
    - 複数画像ファイルの選択（JPG、PNG、BMP、GIF対応）
    - 画像の順序変更
    - フレーム間隔の設定
    - アニメーションGIFの生成
    - プログレスバーでの進捗表示
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageTk
import threading


class GifCreator:
    """アニメーションGIF作成クラス"""
    
    def __init__(self):
        """初期化"""
        self.root = tk.Tk()
        self.root.title("アニメーションGIF作成ツール")
        self.root.geometry("800x600")
        
        # 画像ファイルリスト
        self.image_files: List[str] = []
        
        # サポートする画像形式
        self.supported_formats = [
            ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
            ("すべてのファイル", "*.*")
        ]
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択セクション
        file_frame = ttk.LabelFrame(main_frame, text="画像ファイル選択", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="画像ファイルを選択", 
                  command=self.select_files).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(file_frame, text="クリア", 
                  command=self.clear_files).grid(row=0, column=1)
        
        # ファイルリスト
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # リストボックスとスクロールバー
        self.file_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 順序変更ボタン
        order_frame = ttk.Frame(file_frame)
        order_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(order_frame, text="↑ 上へ", 
                  command=self.move_up).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(order_frame, text="↓ 下へ", 
                  command=self.move_down).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(order_frame, text="削除", 
                  command=self.remove_selected).grid(row=0, column=2)
        
        # 設定セクション
        settings_frame = ttk.LabelFrame(main_frame, text="GIF設定", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # フレーム間隔設定
        ttk.Label(settings_frame, text="フレーム間隔 (ミリ秒):").grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="500")
        duration_spinbox = ttk.Spinbox(settings_frame, from_=100, to=5000, 
                                      increment=100, textvariable=self.duration_var, width=10)
        duration_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # ループ設定
        self.loop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="無限ループ", 
                       variable=self.loop_var).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # 出力ファイル設定
        output_frame = ttk.LabelFrame(main_frame, text="出力設定", padding="10")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(output_frame, text="出力ファイル:").grid(row=0, column=0, sticky=tk.W)
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        ttk.Button(output_frame, text="参照", 
                  command=self.select_output_file).grid(row=0, column=2)
        
        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ステータスラベル
        self.status_var = tk.StringVar(value="画像ファイルを選択してください")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # 作成ボタン
        self.create_button = ttk.Button(main_frame, text="GIFを作成", 
                                       command=self.create_gif, state=tk.DISABLED)
        self.create_button.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(1, weight=1)
    
    def select_files(self) -> None:
        """画像ファイルを選択"""
        files = filedialog.askopenfilenames(
            title="画像ファイルを選択",
            filetypes=self.supported_formats
        )
        
        if files:
            # 新しいファイルを追加
            for file_path in files:
                if file_path not in self.image_files:
                    self.image_files.append(file_path)
            
            self.update_file_list()
            self.update_create_button_state()
    
    def clear_files(self) -> None:
        """ファイルリストをクリア"""
        self.image_files.clear()
        self.update_file_list()
        self.update_create_button_state()
    
    def update_file_list(self) -> None:
        """ファイルリストを更新"""
        self.file_listbox.delete(0, tk.END)
        for i, file_path in enumerate(self.image_files):
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, f"{i+1:2d}. {filename}")
    
    def move_up(self) -> None:
        """選択されたファイルを上に移動"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.image_files[index], self.image_files[index-1] = \
                self.image_files[index-1], self.image_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index-1)
    
    def move_down(self) -> None:
        """選択されたファイルを下に移動"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.image_files) - 1:
            index = selection[0]
            self.image_files[index], self.image_files[index+1] = \
                self.image_files[index+1], self.image_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index+1)
    
    def remove_selected(self) -> None:
        """選択されたファイルを削除"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            del self.image_files[index]
            self.update_file_list()
            self.update_create_button_state()
    
    def select_output_file(self) -> None:
        """出力ファイルを選択"""
        file_path = filedialog.asksaveasfilename(
            title="GIFファイルを保存",
            defaultextension=".gif",
            filetypes=[("GIFファイル", "*.gif"), ("すべてのファイル", "*.*")]
        )
        
        if file_path:
            self.output_path_var.set(file_path)
    
    def update_create_button_state(self) -> None:
        """作成ボタンの状態を更新"""
        if len(self.image_files) >= 2 and self.output_path_var.get():
            self.create_button.config(state=tk.NORMAL)
        else:
            self.create_button.config(state=tk.DISABLED)
    
    def create_gif(self) -> None:
        """GIFを作成"""
        if len(self.image_files) < 2:
            messagebox.showerror("エラー", "少なくとも2つの画像ファイルが必要です")
            return
        
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showerror("エラー", "出力ファイルを指定してください")
            return
        
        # 別スレッドでGIF作成を実行
        thread = threading.Thread(target=self._create_gif_thread, args=(output_path,))
        thread.daemon = True
        thread.start()
    
    def _create_gif_thread(self, output_path: str) -> None:
        """GIF作成スレッド"""
        try:
            self.status_var.set("GIFを作成中...")
            self.create_button.config(state=tk.DISABLED)
            
            # 画像を読み込み
            images = []
            total_files = len(self.image_files)
            
            for i, file_path in enumerate(self.image_files):
                try:
                    # プログレス更新
                    progress = (i / total_files) * 50  # 読み込みは50%まで
                    self.progress_var.set(progress)
                    self.root.update()
                    
                    # 画像を開いてリサイズ（必要に応じて）
                    img = Image.open(file_path)
                    
                    # 最初の画像のサイズに合わせてリサイズ
                    if i == 0:
                        base_size = img.size
                    else:
                        img = img.resize(base_size, Image.Resampling.LANCZOS)
                    
                    images.append(img)
                    
                except Exception as e:
                    messagebox.showerror("エラー", f"画像の読み込みに失敗しました: {file_path}\n{str(e)}")
                    return
            
            # GIF作成
            duration = int(self.duration_var.get())
            loop = 0 if self.loop_var.get() else 1
            
            for i in range(len(images)):
                progress = 50 + (i / len(images)) * 50  # 作成は50-100%
                self.progress_var.set(progress)
                self.root.update()
            
            # GIFを保存
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=loop,
                optimize=True
            )
            
            self.progress_var.set(100)
            self.status_var.set(f"GIFが正常に作成されました: {output_path}")
            messagebox.showinfo("完了", f"GIFが正常に作成されました:\n{output_path}")
            
        except Exception as e:
            self.status_var.set("エラーが発生しました")
            messagebox.showerror("エラー", f"GIFの作成に失敗しました:\n{str(e)}")
        
        finally:
            self.create_button.config(state=tk.NORMAL)
            self.progress_var.set(0)
    
    def run(self) -> None:
        """アプリケーションを実行"""
        # 出力パスが変更された時のイベントハンドラー
        self.output_path_var.trace_add('write', lambda *args: self.update_create_button_state())
        
        self.root.mainloop()


def main():
    """メイン関数"""
    try:
        app = GifCreator()
        app.run()
    except Exception as e:
        print(f"アプリケーションの実行中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
