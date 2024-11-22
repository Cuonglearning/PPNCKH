import os
import lzma
from PIL import Image
import io
from tkinter import Tk, filedialog, Label, Button, messagebox
import time
import psycopg2
from connect import get_db_connection  # Import the connection function

def create_compressed_table(conn):
    """Create table for storing compressed images."""
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compressed_images (
            id SERIAL PRIMARY KEY,
            image_name TEXT NOT NULL,
            compressed_data BYTEA NOT NULL
        );
        """)
        conn.commit()

def compress_tiff_image(image_path):
    """Compress a TIFF image using LZMA."""
    try:
        with Image.open(image_path) as img:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="TIFF")
            original_data = img_byte_arr.getvalue()

        start_time = time.time()
        compressed_data = lzma.compress(original_data)
        end_time = time.time()
        compression_time = end_time - start_time

        return compressed_data, compression_time
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi nén ảnh: {e}")
        return None, 0

def save_compressed_image_to_db(image_name, compressed_data, conn):
    """Save compressed image data to PostgreSQL."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO compressed_images (image_name, compressed_data)
            VALUES (%s, %s);
            """, (image_name, psycopg2.Binary(compressed_data)))
            conn.commit()
            messagebox.showinfo("Thảnh công", f"Ảnh '{image_name}' đã được nén trong cơ sở dữ liệu.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi lưu ảnh vào cơ sở dữ liệu: {e}")

def select_and_compress_image():
    """Handle the image selection and compression process."""
    image_path = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=[("TIFF files", "*.tif *.tiff")]
    )
    if not image_path:
        return

    image_name = os.path.basename(image_path)
    compressed_data, compression_time = compress_tiff_image(image_path)

    if compressed_data:
        save_compressed_image_to_db(image_name, compressed_data, conn)
        messagebox.showinfo("Thông tin", f"Thời gian nén: {compression_time:.2f} giây")

# GUI setup
root = Tk()
root.title("TIFF Image Compressor")
root.geometry("400x200")

Label(root, text="Nén ảnh vào cơ sở dữ liệu", font=("Arial", 14)).pack(pady=10)
Button(root, text="Chọn ảnh để nén", font=("Arial", 12), command=select_and_compress_image).pack(pady=10)

# Get the database connection from connect.py
conn = get_db_connection()
if conn is None:
    messagebox.showerror("Lỗi", "Không thể kết nối cơ sở dữ liệu.")
    root.quit()  # Exit if connection failed

create_compressed_table(conn)

root.mainloop()

conn.close()
