import tkinter as tk
from tkinter import messagebox
import subprocess

# Hàm chạy file Python khi nhấn nút
def run_python_script(script_name):
    try:
        subprocess.run(['python', script_name], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Lỗi", f"Không thể chạy {script_name}: {e}")

# Hàm tạo giao diện cho nút Huffman
def show_huffman_menu():
    clear_frame()

    # Tạo các nút trong menu Huffman
    compress_button = tk.Button(root, text="Nén", font=("Arial", 12), width=20, command=lambda: run_python_script('compress.py'))
    compress_button.pack(pady=10)

    decompress_button = tk.Button(root, text="Giải nén", font=("Arial", 12), width=20, command=lambda: run_python_script('decompress.py'))
    decompress_button.pack(pady=10)

    # Thêm nút quay lại màn hình chính
    back_button = tk.Button(root, text="Màn hình chính", font=("Arial", 12), width=20, command=create_main_menu)
    back_button.pack(pady=20)

# Hàm tạo giao diện cho nút LZW
def show_lzw_menu():
    clear_frame()

    # Tạo các nút trong menu LZW
    compress_button = tk.Button(root, text="Nén", font=("Arial", 12), width=20, command=lambda: run_python_script('LZW.py'))
    compress_button.pack(pady=10)

    decompress_button = tk.Button(root, text="Giải nén", font=("Arial", 12), width=20, command=lambda: run_python_script('LZWdecompress.py'))
    decompress_button.pack(pady=10)

    # Thêm nút quay lại màn hình chính
    back_button = tk.Button(root, text="Màn hình chính", font=("Arial", 12), width=20, command=create_main_menu)
    back_button.pack(pady=20)

# Hàm tạo giao diện cho nút Comparison ngoài màn hình chính và chạy luôn file comparison.py
def run_comparison():
    run_python_script('comparison.py')

def show_comparison_button():
    clear_frame()

    # Tạo nút Comparison với kích thước giống các nút khác
    comparison_button = tk.Button(root, text="So sánh", font=("Arial", 12), width=20, command=run_comparison)
    comparison_button.pack(pady=20)

# Hàm xóa giao diện hiện tại để tạo giao diện mới
def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()

# Hàm tạo menu chính
def create_main_menu():
    clear_frame()

    # Tạo các nút trong menu chính
    
    lzw_button = tk.Button(root, text="LZW", font=("Arial", 16), width=20, command=show_lzw_menu)
    lzw_button.pack(pady=20)
    
    huffman_button = tk.Button(root, text="Huffman", font=("Arial", 16), width=20, command=show_huffman_menu)
    huffman_button.pack(pady=20)

    # Thêm nút Comparison ở ngoài menu
    comparison_button = tk.Button(root, text="So sánh", font=("Arial", 16), width=20, command=run_comparison)
    comparison_button.pack(pady=20)

# Tạo cửa sổ giao diện chính
root = tk.Tk()
root.title("Compression Algorithm Menu")
root.geometry("400x350")

# Hiển thị menu chính
create_main_menu()

# Chạy giao diện
root.mainloop()
