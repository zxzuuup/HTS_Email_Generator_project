# build_exe.py
import subprocess
import sys
import os


def main():
    spec_file = "HTS_Email_Generator_GUI.spec"
    # 入口点改为 main.py
    main_script = "src/main.py"
    exe_name = "HTS_Email_Generator_GUI"

    if not os.path.exists(spec_file):
        print(f"生成 .spec 文件: {spec_file}")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            "--add-data", "HTS_DB.xlsx;.",  # 注意：Windows 用 ; 分隔
            "--add-data", "EmailBlurb.xlsx;.",
            "--name", exe_name,
            main_script
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("生成 .spec 文件失败:")
            print(result.stderr)
            sys.exit(1)
        print(f".spec 文件已生成: {spec_file}")
    else:
        print(f"使用已存在的 .spec 文件: {spec_file}")

    print("开始使用 PyInstaller 构建...")
    cmd = [sys.executable, "-m", "PyInstaller", spec_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("PyInstaller 构建失败:")
        print(result.stderr)
        sys.exit(1)

    print("\nPyInstaller 构建成功!")
    print(f"可执行文件位于: dist/{exe_name}.exe")


if __name__ == "__main__":
    try:
        import PyInstaller
    except ImportError:
        print("未找到 PyInstaller。正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    main()