import os
import qrcode
from config2 import QR_FOLDER
def generate_book_copy_qr(copy_code):
    os.makedirs(QR_FOLDER, exist_ok=True)
    filename = f"{copy_code}.png"
    file_path = os.path.join(QR_FOLDER,filename)
    qr = qrcode.QRCode(version=1,box_size=10,border=4)
    qr.add_data(copy_code)
    qr.make(fit=True)
    image = qr.make_image()
    image.save(file_path)
    return f"qrcodes/{filename}"