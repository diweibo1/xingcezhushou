@echo off
pyinstaller --onefile ^
            --windowed ^
            --icon=E:\\行测错题助手
            --add-data "question_data.db" ^
            main.py
echo 打包完成！生成文件在dist文件夹
pause
