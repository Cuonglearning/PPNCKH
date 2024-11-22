import os
from tkinter import *
from tkinter import ttk, messagebox
from connect import get_db_connection  # Import the connection function

def compare_files(original_file, decompressed_file):
    """So sánh nội dung giữa hai file."""
    with open(original_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
        return f1.read() == f2.read()

def check_compression_details(algorithm, conn):
    if algorithm == "Huffman":
        table_name = "huffman_compress"
        decompressed_folder = "HuffmanDecompress"
    elif algorithm == "LZW":
        table_name = "compressed_images"
        decompressed_folder = "LZWdecompress"
    else:
        messagebox.showerror("Error", "Invalid algorithm selected!")
        return

    # Fetch all image names from the database table
    with conn.cursor() as cur:
        cur.execute(f"SELECT image_name FROM {table_name}")
        images = cur.fetchall()

    # Show available images to user
    if not images:
        messagebox.showinfo("Không có dữ liệu", f"Không tìm thấy ảnh trong bảng '{table_name}'.")
        return

    def on_image_select():
        selected_image = image_combo.get()
        if not selected_image:
            messagebox.showwarning("Cảnh báo", "Hãy chọn một ảnh!")
            return

        # Compare file sizes
        original_file = os.path.join("images", selected_image)
        decompressed_file = os.path.join(decompressed_folder, selected_image)

        if not os.path.exists(original_file):
            messagebox.showerror("Lỗi", f"Không tìm thấy ảnh gốc '{original_file}'!")
            return
        if not os.path.exists(decompressed_file):
            messagebox.showerror("Lỗi", f"Không tìm thấy ảnh '{decompressed_file}' đã giải nén!")
            return

        original_size = os.path.getsize(original_file)
        with conn.cursor() as cur:
            cur.execute(f"SELECT compressed_data FROM {table_name} WHERE image_name = %s", (selected_image,))
            compressed_data = cur.fetchone()
            compressed_size = len(compressed_data[0]) if compressed_data else 0

        decompressed_size = os.path.getsize(decompressed_file)
        files_match = compare_files(original_file, decompressed_file)

        # Show comparison results
        result_text = (
            f"Kết quả so sánh ảnh {selected_image}:\n"
            f"- Dung lượng ảnh gốc: {original_size / (1024**2):.2f} MB\n"
            f"- Dung lượng sau khi nén: {compressed_size / (1024**2):.2f} MB\n"
            f"- Dung lượng sau khi giải nén: {decompressed_size / (1024**2):.2f} MB\n"
            f"- File gốc và file giải nén có khớp không: {'Có' if files_match else 'Không'}"
        )
        messagebox.showinfo("Kết quả so sánh", result_text)

    # Create a new window for selecting an image
    select_window = Toplevel(root)
    select_window.title(f"Chọn ảnh - {algorithm} Compression")
    select_window.geometry("600x300")  # Increase window size

    Label(select_window, text="Chọn một ảnh:").pack(pady=5)
    image_combo = ttk.Combobox(select_window, values=[img[0] for img in images], state="readonly", width=70)  # Wider ComboBox
    image_combo.pack(pady=5)

    Button(select_window, text="So sánh", command=on_image_select).pack(pady=10)

# Main GUI application
def main():
    global root
    root = Tk()
    root.title("So sánh nén ảnh")
    root.geometry("500x250")  # Increase main window size

    # Get the database connection from connect.py
    conn = get_db_connection()
    if conn is None:
        messagebox.showerror("Lỗi", "Không thể kết nối cơ sở dữ liệu.")
        root.quit()  # Exit if connection failed

    def on_algorithm_select():
        selected_algorithm = algorithm_combo.get()
        if not selected_algorithm:
            messagebox.showwarning("Cảnh báo", "Please select an algorithm!")
        else:
            check_compression_details(selected_algorithm, conn)

    Label(root, text="Select Compression Algorithm:").pack(pady=20)
    algorithm_combo = ttk.Combobox(root, values=["Huffman", "LZW"], state="readonly", width=50)  # Wider ComboBox
    algorithm_combo.pack(pady=10)

    Button(root, text="Next", command=on_algorithm_select).pack(pady=20)

    root.mainloop()
    conn.close()

if __name__ == "__main__":
    main()
