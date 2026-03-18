# FileReplacer

[中文版本](README.zh.md) | English Version

FileReplacer is a lightweight file content replacement tool designed for static web page developers to quickly replace fixed links, code snippets, or text content in files.

## Features

- **Multi-format support**: Supports .md, .html, .txt and other file formats
- **Intelligent search**: Uses regular expressions for content matching, supports fuzzy matching
- **Interactive operation**: Supports browsing through matching results and selective replacement
- **Batch operation**: One-click replacement of all matching content
- **Real-time preview**: Displays matching file paths, line numbers, and content
- **Graphical interface**: Modern graphical interface with Chinese and English switching
- **Multi-language support**: Built-in Chinese and English language switching functionality

## Installation

### Method 1: Run Python script directly

1. Ensure Python 3.6 or higher is installed
2. Download the `file_replacer.py` file to your local machine
3. Run in the command line:

```bash
python file_replacer.py
```

### Method 2: Use EXE file (Windows)

1. Download the `file_replacer.exe` file
2. Double-click to run or use in the command line

## Usage Examples

### 1. Search content

```bash
# Search all files containing "old-link.com" in the current directory
python file_replacer.py --pattern "old-link.com"

# Search in a specified directory
python file_replacer.py --dir "path/to/directory" --pattern "old-link.com"
```

### 2. Interactive replacement

```bash
# Search and enter interactive replacement mode
python file_replacer.py --pattern "old-link.com" --replace "new-link.com"
```

### 3. Batch replacement

```bash
# Search and batch replace all matches
python file_replacer.py --pattern "old-link.com" --replace "new-link.com" --batch
```

## Graphical Interface Usage

1. Run `file_replacer.py` or `file_replacer.exe` to start the graphical interface
2. Select a directory or file in the search parameters section
3. Enter the search pattern and replacement content
4. Optionally enable fuzzy matching mode
5. Click the "Search" button to view matching results
6. Select a match to view context content
7. Click "Replace Current" or "Replace All" buttons to perform replacement
8. View operation results in the status label at the bottom of the interface

## Language Switching

In the graphical interface, click the "Language" button to switch between Chinese and English interface languages.

## Search Mode Explanation

### Exact Matching Mode
- Uses regular expressions for exact matching
- Suitable for finding fixed strings, links, or code snippets
- Matching results are accurate and do not include similar but different content
- Example: Searching for "https://old-link.com" will only match exactly the same string

### Fuzzy Matching Mode
- Uses similarity algorithm for matching
- Suitable for finding similar but not identical content
- Matching results include content with high similarity
- Similarity threshold is 0.6 (can be adjusted in the code)
- Example: Searching for "https://old-link.com" will match "https://new-old-link.com" and other similar content

## Frequently Asked Questions

### Q: Why isn't my replacement taking effect?
A: Please check if the regular expression is correct, especially special characters need to be escaped. In fuzzy matching mode, ensure the similarity is high enough.

### Q: Which file formats are supported?
A: By default, .md, .html, and .txt formats are supported. You can modify the `extensions` parameter in the code to add other formats.

### Q: How to handle large files?
A: The tool reads files line by line, which may have performance implications for very large files. It is recommended to use it within a small scope.

## License

MIT License

## Contribution

Welcome to submit Issues and Pull Requests!