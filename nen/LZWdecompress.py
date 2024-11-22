import os
import lzma
from tkinter import Tk, Listbox, Button, Label, Scrollbar, END, messagebox
import time
from connect import get_db_connection  # Import the connection function

# Hàm lấy danh sách tên ảnh từ database
def fetch_image_names(cursor):
    try:
        cursor.execute("SELECT image_name FROM compressed_images;")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi truy xuất ảnh: {e}")
        return []

# Hàm lấy dữ liệu nén từ database
def fetch_compressed_image_from_db(image_name, cursor):
    try:
        query = "SELECT compressed_data FROM compressed_images WHERE image_name = %s;"
        cursor.execute(query, (image_name,))
        result = cursor.fetchone()
        if result:
            return result[0]  # compressed_data
        else:
            messagebox.showwarning("Warning", f"Không thể tìm thấy dữ liệu ảnh '{image_name}'.")
            return None
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi truy xuất ảnh: {e}")
        return None

# Hàm giải nén dữ liệu LZMA
def decompress_image_data(compressed_data):
    try:
        start_time = time.time()  # Bắt đầu tính thời gian
        decompressed_data = lzma.decompress(compressed_data)
        end_time = time.time()  # Kết thúc tính thời gian
        messagebox.showinfo("Thông tin", f"Thời gian giải nén: {end_time - start_time:.4f} giây")
        return decompressed_data
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi giải nén ảnh: {e}")
        return None

# Hàm lưu ảnh giải nén vào file
def save_decompressed_image(image_name, decompressed_data):
    try:
        # Đảm bảo thư mục 'LZWdecompress' tồn tại
        output_folder = os.path.join(os.getcwd(), "LZWdecompress")
        os.makedirs(output_folder, exist_ok=True)
        
        # Lưu dữ liệu vào file TIFF
        output_path = os.path.join(output_folder, image_name)
        with open(output_path, "wb") as f:
            f.write(decompressed_data)
        messagebox.showinfo("Thành công", f"Ảnh đã được giải nén ở: {output_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lưu ảnh: {e}")

# Hàm xử lý khi người dùng nhấn nút "Giải nén"
def on_decompress_button_click(listbox, cursor):
    selected_image = listbox.get(listbox.curselection())
    compressed_data = fetch_compressed_image_from_db(selected_image, cursor)
    if compressed_data:
        decompressed_data = decompress_image_data(compressed_data)
        if decompressed_data:
            save_decompressed_image(selected_image, decompressed_data)

# Tạo giao diện tkinter
root = Tk()
root.title("Image Decompression Tool")

# Label hiển thị hướng dẫn
label = Label(root, text="Chọn ảnh để giải nén:")
label.pack()

# Listbox hiển thị danh sách ảnh
listbox = Listbox(root, width=80, height=20)
listbox.pack()

# Thêm scrollbar cho listbox
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Nút giải nén
decompress_button = Button(root, text="Giải nén", command=lambda: on_decompress_button_click(listbox, cursor))
decompress_button.pack()

# Kết nối đến database thông qua connect.py
conn = get_db_connection()
if conn is None:
    messagebox.showerror("Lỗi", "Không thể kết nối cơ sở dữ liệu")
    root.quit()  # Exit if connection failed

cursor = conn.cursor()

# Lấy danh sách tên ảnh từ database và thêm vào listbox
image_names = fetch_image_names(cursor)
for image_name in image_names:
    listbox.insert(END, image_name)

# Chạy giao diện
root.mainloop()

# Đóng kết nối
cursor.close()
conn.close()
