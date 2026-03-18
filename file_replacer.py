import os
import re
import argparse
import difflib
from typing import List, Dict, Tuple

# 尝试导入 PyQt5，如果没有安装则使用 tkinter
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QTreeView, QTextEdit, 
                               QFileDialog, QMessageBox, QSplitter, QComboBox)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
    USE_PYQT = True
except ImportError:
    pass


class FileReplacer:
    def __init__(self, extensions: List[str] = ['.md', '.html', '.txt']):
        self.extensions = extensions
        self.matches = []
        self.fuzzy_mode = False
    
    def search_files(self, directory: str, pattern: str) -> List[Dict]:
        """搜索目录下的文件，查找匹配的内容"""
        self.matches = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            for line_num, line in enumerate(lines, 1):
                                if self._match_pattern(line, pattern):
                                    self.matches.append({
                                        'file': file_path,
                                        'line': line_num,
                                        'content': line.strip()
                                    })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        return self.matches
    
    def search_single_file(self, file_path: str, pattern: str) -> List[Dict]:
        """搜索单个文件，查找匹配的内容"""
        self.matches = []
        if any(file_path.endswith(ext) for ext in self.extensions):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if self._match_pattern(line, pattern):
                            self.matches.append({
                                'file': file_path,
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        return self.matches
    
    def _match_pattern(self, line: str, pattern: str) -> bool:
        """匹配模式，支持精确匹配和模糊匹配"""
        if not self.fuzzy_mode:
            # 精确匹配
            return bool(re.search(pattern, line))
        else:
            # 模糊匹配
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, line, pattern).ratio()
            # 相似度阈值，可调整
            return similarity > 0.6
    
    def replace_content(self, file_path: str, old_pattern: str, new_content: str) -> bool:
        """替换文件中的内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.fuzzy_mode:
                # 模糊匹配模式下，直接替换整个文件内容
                # 这里简化处理，实际应用中可能需要更复杂的逻辑
                # 例如，只替换匹配的行
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if self._match_pattern(line, old_pattern):
                        new_lines.append(new_content)
                    else:
                        new_lines.append(line)
                new_content = '\n'.join(new_lines)
            else:
                # 精确匹配模式下，使用正则替换
                new_content = re.sub(old_pattern, new_content, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"Error replacing in {file_path}: {e}")
            return False
    
    def batch_replace(self, old_pattern: str, new_content: str) -> int:
        """批量替换所有匹配的内容"""
        count = 0
        for match in self.matches:
            if self.replace_content(match['file'], old_pattern, new_content):
                count += 1
        return count
    
    def get_context(self, file_path: str, line_num: int, context_lines: int = 3) -> List[str]:
        """获取匹配行的上下文内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.read().split('\n')
            
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            
            context = []
            for i in range(start, end):
                prefix = "→ " if i == line_num - 1 else "  "
                context.append(f"{prefix}{i + 1}: {lines[i]}")
            
            return context
        except Exception as e:
            print(f"Error getting context: {e}")
            return []

def interactive_mode(replacer, matches, pattern, replace_content):
    """交互式模式，支持上下查询和替换操作"""
    current_index = 0
    while True:
        if not matches:
            print("No matches found.")
            break
        
        match = matches[current_index]
        print(f"\nMatch {current_index + 1}/{len(matches)}:")
        print(f"File: {match['file']}")
        print(f"Line: {match['line']}")
        print(f"Content: {match['content']}")
        
        print("\nCommands:")
        print("  n: next match")
        print("  p: previous match")
        print("  r: replace this match")
        print("  a: replace all matches")
        print("  q: quit")
        
        command = input("Enter command: ").lower()
        
        if command == 'n':
            current_index = (current_index + 1) % len(matches)
        elif command == 'p':
            current_index = (current_index - 1) % len(matches)
        elif command == 'r':
            if replacer.replace_content(match['file'], pattern, replace_content):
                print("Replaced successfully")
                # 更新当前匹配项的内容
                with open(match['file'], 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')
                    if match['line'] <= len(lines):
                        match['content'] = lines[match['line'] - 1].strip()
        elif command == 'a':
            count = replacer.batch_replace(pattern, replace_content)
            print(f"Replaced {count} occurrences")
            break
        elif command == 'q':
            break
        else:
            print("Invalid command. Try again.")

class FileReplacerGUI:
    def __init__(self, root=None):
        if USE_PYQT:
            # 语言字典
            self.languages = {
                'zh': {
                    'window_title': 'FileReplacer - 文件内容替换工具',
                    'dir_label': '目录:',
                    'browse_dir': '浏览文件夹',
                    'file_label': '文件:',
                    'browse_file': '浏览文件',
                    'pattern_label': '搜索模式:',
                    'search_button': '搜索',
                    'replace_label': '替换为:',
                    'fuzzy_button': '开启模糊匹配',
                    'fuzzy_button_off': '关闭模糊匹配',
                    'result_label': '匹配结果',
                    'context_label': '上下文',
                    'replace_current': '替换当前',
                    'replace_all': '替换全部',
                    'exit_button': '退出',
                    'language_button': '语言',
                    'status_ready': '就绪',
                    'status_search_complete': '搜索完成，找到 {count} 个匹配项',
                    'status_replace_success': '替换成功',
                    'status_replace_fail': '替换失败',
                    'status_replace_all': '替换成功，替换了 {count} 个匹配项',
                    'error_no_pattern': '错误：请输入搜索模式',
                    'error_no_path': '错误：请选择目录或文件',
                    'error_no_replace': '错误：请输入替换内容',
                    'warning_no_matches': '警告：没有找到匹配项',
                    'browse_dir_title': '选择搜索目录',
                    'browse_file_title': '选择文件'
                },
                'en': {
                    'window_title': 'FileReplacer - File Content Replacement Tool',
                    'dir_label': 'Directory:',
                    'browse_dir': 'Browse Directory',
                    'file_label': 'File:',
                    'browse_file': 'Browse File',
                    'pattern_label': 'Search Pattern:',
                    'search_button': 'Search',
                    'replace_label': 'Replace with:',
                    'fuzzy_button': 'Enable Fuzzy Match',
                    'fuzzy_button_off': 'Disable Fuzzy Match',
                    'result_label': 'Match Results',
                    'context_label': 'Context',
                    'replace_current': 'Replace Current',
                    'replace_all': 'Replace All',
                    'exit_button': 'Exit',
                    'language_button': 'Language',
                    'status_ready': 'Ready',
                    'status_search_complete': 'Search completed, found {count} matches',
                    'status_replace_success': 'Replacement successful',
                    'status_replace_fail': 'Replacement failed',
                    'status_replace_all': 'Replacement successful, replaced {count} occurrences',
                    'error_no_pattern': 'Error: Please enter search pattern',
                    'error_no_path': 'Error: Please select directory or file',
                    'error_no_replace': 'Error: Please enter replacement content',
                    'warning_no_matches': 'Warning: No matches found',
                    'browse_dir_title': 'Select Search Directory',
                    'browse_file_title': 'Select File'
                }
            }
            
            # 当前语言
            self.current_language = 'zh'
            
            # PyQt5 实现
            self.app = QApplication([])
            self.window = QMainWindow()
            self.window.setWindowTitle(self.languages[self.current_language]['window_title'])
            self.window.setGeometry(100, 100, 1000, 800)
            
            # 设置窗口图标（预留位置）
            # 请将 icon.ico 文件放在与 file_replacer.py 同一目录下
            # 或者修改下面的路径为你的图标文件路径
            icon_path = "icon.ico"
            if os.path.exists(icon_path):
                from PyQt5.QtGui import QIcon
                self.window.setWindowIcon(QIcon(icon_path))
            
            # 简化样式，确保按钮显示
            self.window.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                }
                QLabel {
                    color: #333333;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            
            self.replacer = FileReplacer()
            self.current_match_index = 0
            
            # 中心部件
            central_widget = QWidget()
            self.window.setCentralWidget(central_widget)
            
            # 主布局
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(10)
            
            # 目录选择
            dir_layout = QHBoxLayout()
            self.dir_label = QLabel(self.languages[self.current_language]['dir_label'])
            self.dir_edit = QLineEdit(".")
            self.browse_button = QPushButton(self.languages[self.current_language]['browse_dir'])
            self.browse_button.clicked.connect(self.browse_directory)
            dir_layout.addWidget(self.dir_label)
            dir_layout.addWidget(self.dir_edit)
            dir_layout.addWidget(self.browse_button)
            main_layout.addLayout(dir_layout)
            
            # 文件选择
            file_layout = QHBoxLayout()
            self.file_label = QLabel(self.languages[self.current_language]['file_label'])
            self.file_edit = QLineEdit("")
            self.file_button = QPushButton(self.languages[self.current_language]['browse_file'])
            self.file_button.clicked.connect(self.browse_file)
            file_layout.addWidget(self.file_label)
            file_layout.addWidget(self.file_edit)
            file_layout.addWidget(self.file_button)
            main_layout.addLayout(file_layout)
            
            # 搜索模式
            pattern_layout = QHBoxLayout()
            self.pattern_label = QLabel(self.languages[self.current_language]['pattern_label'])
            self.pattern_edit = QLineEdit()
            self.search_button = QPushButton(self.languages[self.current_language]['search_button'])
            self.search_button.clicked.connect(self.search)
            pattern_layout.addWidget(self.pattern_label)
            pattern_layout.addWidget(self.pattern_edit)
            pattern_layout.addWidget(self.search_button)
            main_layout.addLayout(pattern_layout)
            
            # 替换内容
            replace_layout = QHBoxLayout()
            self.replace_label = QLabel(self.languages[self.current_language]['replace_label'])
            self.replace_edit = QLineEdit()
            replace_layout.addWidget(self.replace_label)
            replace_layout.addWidget(self.replace_edit)
            main_layout.addLayout(replace_layout)
            
            # 模糊匹配选项
            fuzzy_layout = QHBoxLayout()
            self.fuzzy_checkbox = QPushButton(self.languages[self.current_language]['fuzzy_button'])
            self.fuzzy_checkbox.setCheckable(True)
            self.fuzzy_checkbox.clicked.connect(self.toggle_fuzzy_mode)
            fuzzy_layout.addWidget(self.fuzzy_checkbox)
            main_layout.addLayout(fuzzy_layout)
            
            # 状态标签
            self.status_label = QLabel(self.languages[self.current_language]['status_ready'])
            main_layout.addWidget(self.status_label)
            
            # 匹配结果列表
            self.result_label = QLabel(self.languages[self.current_language]['result_label'])
            main_layout.addWidget(self.result_label)
            
            self.result_model = QStandardItemModel()
            self.result_model.setHorizontalHeaderLabels(['文件路径', '行号', '内容'])
            self.result_tree = QTreeView()
            self.result_tree.setModel(self.result_model)
            self.result_tree.setColumnWidth(0, 400)
            self.result_tree.setColumnWidth(1, 80)
            self.result_tree.setColumnWidth(2, 300)
            self.result_tree.clicked.connect(self.on_result_select)
            main_layout.addWidget(self.result_tree)
            
            # 上下文显示
            self.context_label = QLabel(self.languages[self.current_language]['context_label'])
            main_layout.addWidget(self.context_label)
            
            self.context_text = QTextEdit()
            self.context_text.setFont(QFont("Courier New", 10))
            self.context_text.setReadOnly(True)
            main_layout.addWidget(self.context_text)
            
            # 操作按钮区域
            button_layout = QHBoxLayout()
            self.replace_current_button = QPushButton(self.languages[self.current_language]['replace_current'])
            self.replace_current_button.clicked.connect(self.replace_current)
            self.replace_all_button = QPushButton(self.languages[self.current_language]['replace_all'])
            self.replace_all_button.clicked.connect(self.replace_all)
            
            # 语言切换按钮
            self.language_button = QPushButton(self.languages[self.current_language]['language_button'])
            self.language_button.clicked.connect(self.toggle_language)
            
            self.exit_button = QPushButton(self.languages[self.current_language]['exit_button'])
            self.exit_button.clicked.connect(self.window.close)
            
            button_layout.addWidget(self.replace_current_button)
            button_layout.addWidget(self.replace_all_button)
            button_layout.addStretch()
            button_layout.addWidget(self.language_button)
            button_layout.addWidget(self.exit_button)
            main_layout.addLayout(button_layout)
            
            self.window.show()
        else:
            # 备用 tkinter 实现
            self.root = root
            self.root.title("FileReplacer - 文件内容替换工具")
            self.root.geometry("1000x800")
            self.root.configure(bg="#f8f9fa")
            
            self.replacer = FileReplacer()
            self.current_match_index = 0
            
            # 创建主框架
            self.main_frame = ttk.Frame(root, padding="20")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 搜索参数区域
            self.search_frame = ttk.LabelFrame(self.main_frame, text="搜索参数", padding="20")
            self.search_frame.pack(fill=tk.X, pady=10)
            
            # 目录选择
            ttk.Label(self.search_frame, text="目录:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
            self.dir_var = tk.StringVar(value=".")
            ttk.Entry(self.search_frame, textvariable=self.dir_var, width=60).grid(row=0, column=1, padx=10, pady=10)
            ttk.Button(self.search_frame, text="浏览文件夹", command=self.browse_directory).grid(row=0, column=2, padx=10, pady=10)
            
            # 文件选择
            ttk.Label(self.search_frame, text="文件:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
            self.file_var = tk.StringVar(value="")
            ttk.Entry(self.search_frame, textvariable=self.file_var, width=60).grid(row=1, column=1, padx=10, pady=10)
            ttk.Button(self.search_frame, text="浏览文件", command=self.browse_file).grid(row=1, column=2, padx=10, pady=10)
            
            # 搜索模式
            ttk.Label(self.search_frame, text="搜索模式:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
            self.pattern_var = tk.StringVar()
            ttk.Entry(self.search_frame, textvariable=self.pattern_var, width=60).grid(row=2, column=1, padx=10, pady=10)
            ttk.Button(self.search_frame, text="搜索", command=self.search).grid(row=2, column=2, padx=10, pady=10)
            
            # 替换内容
            ttk.Label(self.search_frame, text="替换为:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
            self.replace_var = tk.StringVar()
            ttk.Entry(self.search_frame, textvariable=self.replace_var, width=60).grid(row=3, column=1, padx=10, pady=10)
            
            # 结果和上下文区域（上下排版）
            self.result_frame = ttk.Frame(self.main_frame)
            self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # 匹配结果列表
            self.result_list_frame = ttk.LabelFrame(self.result_frame, text="匹配结果", padding="10")
            self.result_list_frame.pack(fill=tk.X, pady=5)
            
            self.result_tree = ttk.Treeview(self.result_list_frame, columns=('file', 'line', 'content'), show='headings')
            self.result_tree.heading('file', text='文件路径')
            self.result_tree.heading('line', text='行号')
            self.result_tree.heading('content', text='内容')
            self.result_tree.column('file', width=300)
            self.result_tree.column('line', width=50)
            self.result_tree.column('content', width=200)
            self.result_tree.pack(fill=tk.X, expand=True)
            self.result_tree.bind('<<TreeviewSelect>>', self.on_result_select)
            
            # 上下文显示
            self.context_frame = ttk.LabelFrame(self.result_frame, text="上下文", padding="10")
            self.context_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            self.context_text = tk.Text(self.context_frame, wrap=tk.WORD, font=('Courier New', 10))
            self.context_text.pack(fill=tk.BOTH, expand=True)
            
            # 操作按钮区域
            self.button_frame = ttk.Frame(self.main_frame)
            self.button_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(self.button_frame, text="替换当前", command=self.replace_current).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="替换全部", command=self.replace_all).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.button_frame, text="退出", command=root.quit).pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self):
        if USE_PYQT:
            directory = QFileDialog.getExistingDirectory(self.window, "选择搜索目录", ".")
            if directory:
                self.dir_edit.setText(directory)
                # 清空文件选择
                self.file_edit.setText("")
        else:
            directory = filedialog.askdirectory(initialdir=".", title="选择搜索目录")
            if directory:
                self.dir_var.set(directory)
                # 清空文件选择
                if hasattr(self, 'file_var'):
                    self.file_var.set("")
    
    def browse_file(self):
        if USE_PYQT:
            file_path, _ = QFileDialog.getOpenFileName(self.window, "选择文件", ".", "All Files (*);;Markdown Files (*.md);;HTML Files (*.html);;Text Files (*.txt)")
            if file_path:
                self.file_edit.setText(file_path)
                # 清空目录选择
                self.dir_edit.setText("")
        else:
            file_path = filedialog.askopenfilename(initialdir=".", title="选择文件", 
                                                filetypes=[("All Files", "*"), 
                                                           ("Markdown Files", "*.md"), 
                                                           ("HTML Files", "*.html"), 
                                                           ("Text Files", "*.txt")])
            if file_path:
                if hasattr(self, 'file_var'):
                    self.file_var.setText(file_path)
                # 清空目录选择
                self.dir_var.set("")
    
    def toggle_fuzzy_mode(self):
        """切换模糊匹配模式"""
        if USE_PYQT:
            if self.fuzzy_checkbox.isChecked():
                self.replacer.fuzzy_mode = True
                self.fuzzy_checkbox.setText(self.languages[self.current_language]['fuzzy_button_off'])
            else:
                self.replacer.fuzzy_mode = False
                self.fuzzy_checkbox.setText(self.languages[self.current_language]['fuzzy_button'])
    
    def toggle_language(self):
        """切换界面语言"""
        if USE_PYQT:
            # 切换语言
            if self.current_language == 'zh':
                self.current_language = 'en'
            else:
                self.current_language = 'zh'
            
            # 更新界面文本
            self.window.setWindowTitle(self.languages[self.current_language]['window_title'])
            self.dir_label.setText(self.languages[self.current_language]['dir_label'])
            self.browse_button.setText(self.languages[self.current_language]['browse_dir'])
            self.file_label.setText(self.languages[self.current_language]['file_label'])
            self.file_button.setText(self.languages[self.current_language]['browse_file'])
            self.pattern_label.setText(self.languages[self.current_language]['pattern_label'])
            self.search_button.setText(self.languages[self.current_language]['search_button'])
            self.replace_label.setText(self.languages[self.current_language]['replace_label'])
            
            # 更新模糊匹配按钮文本
            if self.fuzzy_checkbox.isChecked():
                self.fuzzy_checkbox.setText(self.languages[self.current_language]['fuzzy_button_off'])
            else:
                self.fuzzy_checkbox.setText(self.languages[self.current_language]['fuzzy_button'])
            
            self.language_button.setText(self.languages[self.current_language]['language_button'])
            self.result_label.setText(self.languages[self.current_language]['result_label'])
            self.context_label.setText(self.languages[self.current_language]['context_label'])
            self.replace_current_button.setText(self.languages[self.current_language]['replace_current'])
            self.replace_all_button.setText(self.languages[self.current_language]['replace_all'])
            self.exit_button.setText(self.languages[self.current_language]['exit_button'])
            
            # 更新状态标签
            self.status_label.setText(self.languages[self.current_language]['status_ready'])
    
    def search(self):
        if USE_PYQT:
            directory = self.dir_edit.text()
            file_path = self.file_edit.text()
            pattern = self.pattern_edit.text()
            
            if not pattern:
                self.status_label.setText(self.languages[self.current_language]['error_no_pattern'])
                return
            
            # 清空结果
            self.result_model.clear()
            # 更新表头
            if self.current_language == 'zh':
                self.result_model.setHorizontalHeaderLabels(['文件路径', '行号', '内容'])
            else:
                self.result_model.setHorizontalHeaderLabels(['File Path', 'Line', 'Content'])
            
            # 执行搜索
            if file_path:
                # 搜索单个文件
                matches = self.replacer.search_single_file(file_path, pattern)
            elif directory:
                # 搜索目录
                matches = self.replacer.search_files(directory, pattern)
            else:
                self.status_label.setText(self.languages[self.current_language]['error_no_path'])
                return
            
            # 显示结果
            for i, match in enumerate(matches):
                row = []
                row.append(QStandardItem(match['file']))
                row.append(QStandardItem(str(match['line'])))
                row.append(QStandardItem(match['content']))
                self.result_model.appendRow(row)
            
            # 在状态标签中显示搜索结果数量
            self.status_label.setText(self.languages[self.current_language]['status_search_complete'].format(count=len(matches)))
        else:
            directory = self.dir_var.get()
            file_path = self.file_var.get()
            pattern = self.pattern_var.get()
            
            if not pattern:
                messagebox.showerror("错误", "请输入搜索模式")
                return
            
            # 清空结果
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 执行搜索
            if file_path:
                # 搜索单个文件
                matches = self.replacer.search_single_file(file_path, pattern)
            elif directory:
                # 搜索目录
                matches = self.replacer.search_files(directory, pattern)
            else:
                messagebox.showerror("错误", "请选择目录或文件")
                return
            
            # 显示结果
            for i, match in enumerate(matches):
                self.result_tree.insert('', tk.END, iid=i, values=(match['file'], match['line'], match['content']))
            
            # 显示搜索结果数量
            messagebox.showinfo("搜索完成", f"找到 {len(matches)} 个匹配项")
    
    def on_result_select(self, event):
        if USE_PYQT:
            selected_indexes = self.result_tree.selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0].row()
                self.current_match_index = index
                match = self.replacer.matches[index]
                
                # 显示上下文
                context = self.replacer.get_context(match['file'], match['line'])
                self.context_text.setText("\n".join(context))
        else:
            selected_items = self.result_tree.selection()
            if selected_items:
                index = int(selected_items[0])
                self.current_match_index = index
                match = self.replacer.matches[index]
                
                # 显示上下文
                context = self.replacer.get_context(match['file'], match['line'])
                self.context_text.delete(1.0, tk.END)
                self.context_text.insert(tk.END, "\n".join(context))
    
    def replace_current(self):
        if USE_PYQT:
            selected_indexes = self.result_tree.selectedIndexes()
            if not selected_indexes:
                # 使用状态标签显示警告，而不是弹窗
                self.status_label.setText(self.languages[self.current_language]['warning_no_matches'])
                return
            
            pattern = self.pattern_edit.text()
            replace_content = self.replace_edit.text()
            
            if not replace_content:
                self.status_label.setText(self.languages[self.current_language]['error_no_replace'])
                return
            
            index = selected_indexes[0].row()
            match = self.replacer.matches[index]
            
            if self.replacer.replace_content(match['file'], pattern, replace_content):
                self.status_label.setText(self.languages[self.current_language]['status_replace_success'])
                # 更新结果列表
                with open(match['file'], 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')
                    if match['line'] <= len(lines):
                        new_content = lines[match['line'] - 1].strip()
                        self.result_model.item(index, 2).setText(new_content)
                # 更新上下文
                context = self.replacer.get_context(match['file'], match['line'])
                self.context_text.setText("\n".join(context))
            else:
                self.status_label.setText(self.languages[self.current_language]['status_replace_fail'])
        else:
            selected_items = self.result_tree.selection()
            if not selected_items:
                messagebox.showwarning("警告", "请先选择一个匹配项")
                return
            
            pattern = self.pattern_var.get()
            replace_content = self.replace_var.get()
            
            if not replace_content:
                messagebox.showerror("错误", "请输入替换内容")
                return
            
            index = int(selected_items[0])
            match = self.replacer.matches[index]
            
            if self.replacer.replace_content(match['file'], pattern, replace_content):
                messagebox.showinfo("成功", "替换成功")
                # 更新结果列表
                with open(match['file'], 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')
                    if match['line'] <= len(lines):
                        new_content = lines[match['line'] - 1].strip()
                        self.result_tree.item(index, values=(match['file'], match['line'], new_content))
                # 更新上下文
                self.on_result_select(None)
            else:
                messagebox.showerror("错误", "替换失败")
    
    def replace_all(self):
        if USE_PYQT:
            pattern = self.pattern_edit.text()
            replace_content = self.replace_edit.text()
            
            if not replace_content:
                self.status_label.setText(self.languages[self.current_language]['error_no_replace'])
                return
            
            if not self.replacer.matches:
                self.status_label.setText(self.languages[self.current_language]['warning_no_matches'])
                return
            
            count = self.replacer.batch_replace(pattern, replace_content)
            self.status_label.setText(self.languages[self.current_language]['status_replace_all'].format(count=count))
            
            # 重新搜索以更新结果
            self.search()
        else:
            pattern = self.pattern_var.get()
            replace_content = self.replace_var.get()
            
            if not replace_content:
                messagebox.showerror("错误", "请输入替换内容")
                return
            
            if not self.replacer.matches:
                messagebox.showwarning("警告", "没有找到匹配项")
                return
            
            count = self.replacer.batch_replace(pattern, replace_content)
            messagebox.showinfo("成功", f"替换了 {count} 个匹配项")
            
            # 重新搜索以更新结果
            self.search()
    
    def run(self):
        if USE_PYQT:
            self.app.exec_()

if __name__ == "__main__":
    # 检查是否有命令行参数
    import sys
    if len(sys.argv) > 1:
        # 命令行模式
        parser = argparse.ArgumentParser(description="File content replacement tool")
        parser.add_argument('--dir', default='.', help="Directory to search")
        parser.add_argument('--pattern', required=True, help="Pattern to search for")
        parser.add_argument('--replace', help="Content to replace with")
        parser.add_argument('--batch', action='store_true', help="Batch replace all matches")
        
        args = parser.parse_args()
        
        replacer = FileReplacer()
        matches = replacer.search_files(args.dir, args.pattern)
        
        print(f"Found {len(matches)} matches:")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['file']}:{match['line']} - {match['content']}")
        
        if args.replace:
            if args.batch:
                count = replacer.batch_replace(args.pattern, args.replace)
                print(f"Replaced {count} occurrences")
            else:
                # 交互式模式
                interactive_mode(replacer, matches, args.pattern, args.replace)
    else:
        # 图形界面模式
        if USE_PYQT:
            app = FileReplacerGUI()
            app.run()
        else:
            root = tk.Tk()
            app = FileReplacerGUI(root)
            root.mainloop()
