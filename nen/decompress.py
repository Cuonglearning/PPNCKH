import os
from tkinter import Tk, Listbox, Button, Label, messagebox
from PIL import Image
from bitarray import bitarray
import pickle
import time
from connect import get_db_connection  # Import the connection function

def decode_data(encoded_data, huffman_codes):
    reverse_codebook = {v: k for k, v in huffman_codes.items()}
    decoded_data = []
    buffer = ''
    for bit in encoded_data.to01():
        buffer += bit
        if buffer in reverse_codebook:
            decoded_data.append(reverse_codebook[buffer])
            buffer = ''
    return bytes(decoded_data)

def huffman_decompress(image_name, conn):
    start_time = time.time()

    # Retrieve compressed data from database using image name
    with conn.cursor() as cur:
        cur.execute("""
            SELECT image_name, compressed_data, width, height
            FROM huffman_compress
            WHERE image_name = %s
        """, (image_name,))
        result = cur.fetchone()
        if not result:
            messagebox.showerror("Lỗi", f"Không tìm thấy ảnh '{image_name}'")
            return
        
        _, compressed_data, width, height = result

    # Unpack compressed data
    huffman_codes, encoded_data = pickle.loads(compressed_data)
    encoded_bitarray = bitarray()
    encoded_bitarray.frombytes(encoded_data)

    # Decode data
    decoded_data = decode_data(encoded_bitarray, huffman_codes)

    # Define output folder and file name
    output_folder = "HuffmanDecompress"
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, image_name)

    # Convert back to image and save
    img = Image.frombytes("L", (width, height), decoded_data)
    img.save(output_file)

    end_time = time.time()
    decompression_time = end_time - start_time

    messagebox.showinfo("Thành công", f"Ảnh '{image_name}' đã được giải nén vào '{output_file}' trong {decompression_time:.2f} giây")

def on_decompress():
    """Handle the decompress button click."""
    selected_idx = file_listbox.curselection()
    if not selected_idx:
        messagebox.showwarning("Cảnh báo", "Chọn ảnh để giải nén.")
        return

    selected_image = file_listbox.get(selected_idx[0])
    huffman_decompress(selected_image, conn)

# GUI setup
root = Tk()
root.title("Huffman Decompression")
root.geometry("600x400")

Label(root, text="Chọn ảnh để giải nén:", font=("Arial", 14)).pack(pady=10)

file_listbox = Listbox(root, font=("Arial", 12), width=60, height=15)
file_listbox.pack(pady=10)

Button(root, text="Giải nén", font=("Arial", 14), command=on_decompress).pack(pady=10)

# Get the database connection from connect.py
conn = get_db_connection()
if conn is None:
    messagebox.showerror("lỗi", "Không thể kết nối cơ sở dữ liệu.")
    root.quit()  # Exit if connection failed

# Populate Listbox with compressed image names from database
with conn.cursor() as cur:
    cur.execute("SELECT image_name FROM huffman_compress")
    images = cur.fetchall()
    for image in images:
        file_listbox.insert("end", image[0])

root.mainloop()

conn.close()
