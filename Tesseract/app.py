from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Configura el prefijo de Tesseract para el idioma español
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tessdata_prefix = r'C:\Program Files\Tesseract-OCR\tessdata'

def preprocesar_imagen(imagen_path):
    img = cv2.imread(imagen_path)

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar un filtro de desenfoque para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Guardar la imagen preprocesada
    preprocessed_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'preprocessed')
    os.makedirs(preprocessed_dir, exist_ok=True)
    preprocessed_path = os.path.join(preprocessed_dir, os.path.basename(imagen_path))
    cv2.imwrite(preprocessed_path, blurred)

    return preprocessed_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Validar la orientación de la imagen
    img = cv2.imread(file_path)
    height, width = img.shape[:2]
    if height > width:
        return '<p style="color:red;">La imagen debe estar en orientación horizontal. Por favor, sube una imagen a lo ancho.</p>'

    # Preprocesar la imagen
    preprocessed_path = preprocesar_imagen(file_path)

    # Procesar la imagen preprocesada con Tesseract en español
    text = pytesseract.image_to_string(Image.open(preprocessed_path), lang='spa')

    return render_template('resultado.html', texto=text)

if __name__ == '__main__':
    app.run(debug=True)