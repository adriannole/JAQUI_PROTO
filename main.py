import os
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

# Ruta de la plantilla PDF
PDF_TEMPLATE = "templates/plantilla.pdf"
GENERATED_PDF = "generated/formulario_relleno.pdf"

class PDFGeneratorApp(App):
    def build(self):
        self.layout = GridLayout(cols=2, padding=10, spacing=10)

        # Campos a rellenar
        self.fields = {
            "PROVINCIA": TextInput(hint_text="Provincia"),
            "CANTÓN": TextInput(hint_text="Cantón"),
            "CLIENTE": TextInput(hint_text="Cliente"),
            "CORREO": TextInput(hint_text="Correo"),
            "TELÉFONO": TextInput(hint_text="Teléfono"),
            "OBSERVACIONES": TextInput(hint_text="Observaciones", multiline=True),
        }

        # Añadir campos al layout
        for label, input_field in self.fields.items():
            self.layout.add_widget(Label(text=label))
            self.layout.add_widget(input_field)

        # Botón para generar PDF
        self.generate_button = Button(text="Generar PDF")
        self.generate_button.bind(on_press=self.generate_pdf)
        self.layout.add_widget(self.generate_button)

        # Botón para limpiar campos
        self.clear_button = Button(text="Nuevo Registro")
        self.clear_button.bind(on_press=self.clear_fields)
        self.layout.add_widget(self.clear_button)

        return self.layout

    def generate_pdf(self, instance):
        # Crear un canvas temporal para escribir los datos
        temp_canvas_path = "generated/temp_canvas.pdf"
        c = canvas.Canvas(temp_canvas_path)

        # Coordenadas específicas para cada campo
        coordinates = {
            "PROVINCIA": (300, 650),
            "CANTÓN": (100, 680),
            "CLIENTE": (100, 660),
            "CORREO": (100, 640),
            "TELÉFONO": (100, 620),
            "OBSERVACIONES": (100, 600),
        }

        # Escribir los datos en el canvas
        for field, (x, y) in coordinates.items():
            c.drawString(x, y, f"{field}: {self.fields[field].text}")

        c.save()

        # Combinar el canvas temporal con la plantilla
        self.overlay_pdf(temp_canvas_path, GENERATED_PDF)

        # Confirmación
        print(f"PDF generado en: {GENERATED_PDF}")

    def overlay_pdf(self, overlay_path, output_path):
        # Leer la plantilla y el canvas generado
        reader = PdfReader(PDF_TEMPLATE)
        overlay_reader = PdfReader(overlay_path)
        writer = PdfWriter()

        # Combinar las dos páginas
        for page in reader.pages:
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        # Guardar el PDF final
        with open(output_path, "wb") as f:
            writer.write(f)

    def clear_fields(self, instance):
        for input_field in self.fields.values():
            input_field.text = ""

if __name__ == "__main__":
    # Crear carpetas si no existen
    os.makedirs("templates", exist_ok=True)
    os.makedirs("generated", exist_ok=True)

    PDFGeneratorApp().run()
