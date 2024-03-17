import os

def copy_files_to_txt(directory, output_file):
    file_extensions = ['.py', '.txt', '.json', '.md', '.gitignore']  # 添加需要复制的文件扩展名
    with open(output_file, 'w', encoding='utf-8') as output_txt:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    output_txt.write("File: {}\n".format(relative_path))
                    output_txt.write("=" * 20 + "\n")
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        output_txt.write(input_file.read())
                    output_txt.write("\n\n")

directory_to_copy = r"H:\CHATGPTTOPLAYER\MindLoom\MindLoom"  # 修改为您要复制的目录
output_txt_file = "output.txt"  # 输出的txt文件名

copy_files_to_txt(directory_to_copy, output_txt_file)

