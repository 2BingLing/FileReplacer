# FileReplacer

[中文版本](README.zh.md) | [English Version](README.md)

FileReplacer 是一个轻量级的文件内容替换工具，为静态网页开发者设计，用于快速替换文件中的固定链接、代码片段或文本内容。

## 功能特性

- **多格式支持**：支持 .md、.html、.txt 等多种文件格式
- **智能搜索**：使用正则表达式进行内容匹配，支持模糊匹配
- **交互式操作**：支持上下查询匹配结果，选择性替换
- **批量操作**：一键替换所有匹配的内容
- **实时预览**：显示匹配的文件路径、行号和内容
- **图形界面**：现代化的图形界面，支持中英文切换
- **多语言支持**：内置中英文语言切换功能

## 安装方法

### 方法一：直接运行 Python 脚本

1. 确保已安装 Python 3.6 或更高版本
2. 下载 `file_replacer.py` 文件到本地
3. 在命令行中运行：

```bash
python file_replacer.py
```

### 方法二：使用 EXE 文件（Windows）

1. 下载 `file_replacer.exe` 文件
2. 直接双击运行或在命令行中使用

## 使用示例

### 1. 搜索内容

```bash
# 在当前目录搜索包含 "old-link.com" 的所有文件
python file_replacer.py --pattern "old-link.com"

# 在指定目录搜索
python file_replacer.py --dir "path/to/directory" --pattern "old-link.com"
```

### 2. 交互式替换

```bash
# 搜索并进入交互式替换模式
python file_replacer.py --pattern "old-link.com" --replace "new-link.com"
```

### 3. 批量替换

```bash
# 搜索并批量替换所有匹配项
python file_replacer.py --pattern "old-link.com" --replace "new-link.com" --batch
```

## 图形界面使用

1. 运行 `file_replacer.py` 或 `file_replacer.exe` 启动图形界面
2. 在搜索参数区域选择目录或文件
3. 输入搜索模式和替换内容
4. 可选择开启模糊匹配模式
5. 点击"搜索"按钮查看匹配结果
6. 选择匹配项查看上下文内容
7. 点击"替换当前"或"替换全部"按钮执行替换
8. 在界面底部的状态标签中查看操作结果

## 语言切换

在图形界面中，点击"语言"按钮可以在中英文之间切换界面语言。

## 搜索模式说明

### 精确匹配模式
- 使用正则表达式进行精确匹配
- 适合查找固定的字符串、链接或代码片段
- 匹配结果准确，不会包含相似但不同的内容
- 示例：搜索 "https://old-link.com" 只会匹配完全相同的字符串

### 模糊匹配模式
- 使用相似度算法进行匹配
- 适合查找相似但不完全相同的内容
- 匹配结果包含相似度较高的内容
- 相似度阈值为 0.6（可在代码中调整）
- 示例：搜索 "https://old-link.com" 会匹配 "https://new-old-link.com" 等相似内容

## 常见问题

### Q: 为什么我的替换没有生效？
A: 请检查正则表达式是否正确，特别是特殊字符需要转义。在模糊匹配模式下，确保相似度足够高。

### Q: 支持哪些文件格式？
A: 默认支持 .md、.html、.txt 格式，您可以在代码中修改 `extensions` 参数添加其他格式。

### Q: 如何处理大文件？
A: 工具会逐行读取文件，对于非常大的文件可能会有性能影响，建议在小范围内使用。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！