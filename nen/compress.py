import os
from tkinter import Tk, Listbox, Button, Label, messagebox
from PIL import Image
from collections import defaultdict, Counter
from bitarray import bitarray
import pickle
import time
from connect import get_db_connection  # Import the connection function

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_table(data):
    return Counter(data)

def build_huffman_tree(freq_table):
    nodes = [Node(char, freq) for char, freq in freq_table.items()]

    while len(nodes) > 1:
        nodes.sort(key=lambda node: node.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        nodes.append(merged)

    return nodes[0]

def build_huffman_codes(root, prefix='', codebook=defaultdict()):
    if root is not None:
        if root.char is not None:
            codebook[root.char] = prefix
        build_huffman_codes(root.left, prefix + '0', codebook)
        build_huffman_codes(root.right, prefix + '1', codebook)
    return codebook

def encode_data(data, codebook):
    bit_array = bitarray()
    for byte in data:
        bit_array.extend(codebook[byte])
    return bit_array

def huffman_compress(input_file, conn):
    start_time = time.time()
   
    # Read image data
    img = Image.open(input_file)
    img_data = list(img.tobytes())  # Convert bytes to list of integers
    width, height = img.size        # Get image dimensions
   
    # Create frequency table
    freq_table = build_frequency_table(img_data)
   
    # Build Huffman Tree
    huffman_tree = build_huffman_tree(freq_table)
   
    # Build Huffman Codes
    huffman_codes = build_huffman_codes(huffman_tree)
   
    # Encode data
    encoded_data = encode_data(img_data, huffman_codes)
    compressed_data = pickle.dumps((huffman_codes, encoded_data))

    image_name = os.path.basename(input_file)
   
    # Create table if not exists
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS huffman_compress (
                id SERIAL PRIMARY KEY,
                image_name TEXT,
                compressed_data BYTEA,
                width INTEGER,
                height INTEGER
            )
        """)
        conn.commit()

    # Insert compressed data and image dimensions into database
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO huffman_compress (image_name, compressed_data, width, height)
            VALUES (%s, %s, %s, %s)
        """, (image_name, compressed_data, width, height))
        conn.commit()
   
    end_time = time.time()
    compression_time = end_time - start_time
   
    messagebox.showinfo("Thành công", f"Ảnh '{image_name}' đã được nén và lưu vào cơ sở dữ liệu trong {compression_time:.2f} giây")

def on_compress():
    """Handle the compress button click."""
    selected_idx = file_listbox.curselection()
    if not selected_idx:
        messagebox.showwarning("Cảnh báo", "Chọn ảnh để nén")
        return

    selected_file = file_listbox.get(selected_idx[0])
    input_file = os.path.join(folder_path, selected_file)

    # Get the database connection from the db_connection.py file
    conn = get_db_connection()
    if conn:
        huffman_compress(input_file, conn)
        conn.close()

# GUI setup
folder_path = "images"
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

root = Tk()
root.title("Huffman Compression")
root.geometry("600x400")

Label(root, text="Chọn ảnh để nén:", font=("Arial", 14)).pack(pady=10)

file_listbox = Listbox(root, font=("Arial", 12), width=60, height=15)
file_listbox.pack(pady=10)

for file in files:
    file_listbox.insert("end", file)

Button(root, text="Nén ảnh", font=("Arial", 14), command=on_compress).pack(pady=10)

root.mainloop()
