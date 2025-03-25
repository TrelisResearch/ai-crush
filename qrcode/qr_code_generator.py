import qrcode
from PIL import Image
import matplotlib.pyplot as plt

def generate_qr_code(url, filename="qrcode.png"):
    """
    Generate a QR code from a URL and save it to a file.
    
    Args:
        url (str): The URL to encode in the QR code
        filename (str): The filename to save the QR code image to
    
    Returns:
        str: The path to the saved QR code image
    """
    # Create qr code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to the QR code
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    img.save(filename)
    
    return filename

def display_qr_code(image_path):
    """
    Display the QR code image.
    
    Args:
        image_path (str): Path to the QR code image file
    """
    # Load the image
    img = Image.open(image_path)
    
    # Display the image using matplotlib
    plt.imshow(img)
    plt.axis('off')  # Hide axes
    plt.title('QR Code')
    plt.show()

def main():
    # The URL to convert to QR code
    url = "https://forms.gle/JH1KHPFprntnErsL9"
    
    print(f"Generating QR code for: {url}")
    
    # Generate the QR code
    qr_image_path = generate_qr_code(url)
    
    print(f"QR code saved to: {qr_image_path}")
    
    # Display the QR code
    display_qr_code(qr_image_path)
    
    print("QR code displayed. You can also scan it with your phone's camera.")

if __name__ == "__main__":
    main() 