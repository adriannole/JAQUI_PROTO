import os
import threading
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph
from PyPDF2 import PdfReader, PdfWriter

# Ruta de la plantilla PDF
PDF_TEMPLATE = "templates/plantilla.pdf"
GENERATED_FOLDER = "generated"

from kivy.animation import Animation

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=20)
        
        # Logo en el centro
        self.logo = Image(source="images/logo.png", size_hint=(1, 0.7))
        self.layout.add_widget(self.logo)
        
        # Texto debajo del logo
        self.label = Label(
            text="TECMAN PDF GENERATOR",
            font_size=20,
            bold=True,
            color=(1, 1, 1, 0),  # Transparente al inicio
            
        )
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)
        
        # Iniciar animación
        self.start_animation()

    def start_animation(self):
        # Animación para el texto: cambiar opacidad y tamaño
        anim = Animation(color=(1, 1, 1, 1), font_size=40, duration=0.5)
        anim.start(self.label)

# Pantalla principal de la aplicación
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fondo con imagen
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)  # Blanco como base
            self.bg_rect = Rectangle(source="images/background.png", size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        # Configuración de la interfaz
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # ScrollView para formulario
        scroll_view = ScrollView(size_hint=(1, 0.8))
        form_layout = GridLayout(cols=2, padding=20, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Campos a rellenar
        self.fields = {
            "PLANILLA": TextInput(hint_text="Número de planilla N° UIO-XX", multiline=False),
            "PROVINCIA": TextInput(hint_text="Escribe la provincia", multiline=False),
            "CANTÓN": TextInput(hint_text="Escribe el cantón", multiline=False),
            "CLIENTE": TextInput(hint_text="Nombre del cliente", multiline=False),
            "CORREO": TextInput(hint_text="Correo electrónico", multiline=False),
            "TELÉFONO": TextInput(hint_text="Teléfono de contacto", multiline=False),
            "RAZÓN SOCIAL": TextInput(hint_text="Razón social o nombre", multiline=False),
            "DIRECCION": TextInput(hint_text="Escribe la dirección", multiline=False),
            "FECHA": TextInput(hint_text="DD/MM/AAAA", multiline=False),
            "DEPARTAMENTO/UNIDAD": TextInput(hint_text="Departamento o unidad", multiline=False),
            "CONTADOR": TextInput(hint_text="Nombre del contador", multiline=False),
            "SERIE": TextInput(hint_text="Número de serie", multiline=False),
            "OBSERVACIONES": TextInput(hint_text="Observaciones generales", multiline=True),
            "PARTE AFECTADA": TextInput(hint_text="Descripción de la parte afectada", multiline=True),
            "PARTE INSTALADA": TextInput(hint_text="Descripción de la parte instalada", multiline=True),
            "RESPONSABLE": TextInput(hint_text="Nombre del responsable", multiline=False),
        }

        # Añadir campos al layout
        for label, input_field in self.fields.items():
            form_layout.add_widget(Label(text=label, size_hint=(0.3, None), height=dp(35), font_size=12, bold=True, color=(0, 0, 0, 1)))
            input_field.size_hint = (0.7, None)
            input_field.height = dp(35)
            form_layout.add_widget(input_field)

        scroll_view.add_widget(form_layout)

        # Botones con diseño minimalista
        button_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)
        
        self.generate_button = Button(
            text="Generar PDF",
            font_size=14,
            background_color=(0, 0.5, 0.8, 1),
            size_hint=(0.5, 0.5)
        )
        self.generate_button.bind(on_press=self.check_fields_and_generate_pdf)
        
        self.clear_button = Button(
            text="Nuevo Registro",
            font_size=14,
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint=(0.5, 0.5)
        )
        self.clear_button.bind(on_press=self.clear_fields)
        
        button_layout.add_widget(self.generate_button)
        button_layout.add_widget(self.clear_button)

        self.layout.add_widget(scroll_view)
        self.layout.add_widget(button_layout)
        self.add_widget(self.layout)

    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def check_fields_and_generate_pdf(self, instance):
        # Validar campos
        missing_fields = [field for field, input_field in self.fields.items() if not input_field.text]
        if missing_fields:
            self.show_popup("Aviso", f"Faltan los campos: {', '.join(missing_fields)}. Puede continuar exportando.")

        # Iniciar animación de carga y generar el PDF
        self.show_loading_popup()
        threading.Thread(target=self.generate_pdf).start()

    def show_popup(self, title, message):
        # Ventana emergente para mostrar mensajes
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size=14))
        close_button = Button(text="Cerrar", size_hint=(1, 0.3))
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        close_button.bind(on_press=popup.dismiss)
        content.add_widget(close_button)
        popup.open()

    def show_loading_popup(self):
        # Ventana emergente con barra de progreso
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        progress_bar = ProgressBar(max=100, value=0)
        content.add_widget(progress_bar)
        self.loading_popup = Popup(title="Generando PDF", content=content, size_hint=(0.5, 0.5), auto_dismiss=False)
        self.loading_popup.open()

        # Simular progreso
        def update_progress(dt):
            progress_bar.value += 5
            if progress_bar.value >= 100:
                Clock.unschedule(update_progress)
        
        Clock.schedule_interval(update_progress, 0.1)

    def generate_pdf(self):
        # Crear un canvas temporal para escribir los datos
        c = canvas.Canvas(f"{GENERATED_FOLDER}/temp_canvas.pdf", pagesize=letter)

        # Configurar tipo y tamaño de letra para campos simples
        c.setFont("Helvetica", 6.5)

        # Coordenadas específicas para cada campo
        coordinates = {
            "PLANILLA": (504, 655),
            "PROVINCIA": (330, 576),
            "CANTÓN": (458, 576),
            "CLIENTE": (390, 123),
            "CORREO": (398, 627),
            "TELÉFONO": (396, 612),
            "RAZÓN SOCIAL": (130, 627),
            "DIRECCION": (130, 612),
            "FECHA": (130, 596),
            "DEPARTAMENTO/UNIDAD": (396, 596),
            "CONTADOR": (396, 549),
            "SERIE": (458, 549),
            "OBSERVACIONES": (72, 349, 494, 90),  # (x, y, ancho, alto)
            "PARTE AFECTADA": (69, 249, 200, 75),  # (x, y, ancho, alto)
            "PARTE INSTALADA": (69, 179, 200, 75),  # (x, y, ancho, alto)
            "RESPONSABLE": (198, 122),
        }

        # Crear estilo de párrafo para campos largos
        paragraph_style = ParagraphStyle(
            "CustomParagraph",
            fontName="Helvetica",
            fontSize=7,
            leading=13,  # Espaciado entre líneas
        )

        # Escribir los valores en las posiciones con ajuste de texto como párrafo
        for field, coords in coordinates.items():
            value = self.fields[field].text
            if field in ["OBSERVACIONES", "PARTE AFECTADA", "PARTE INSTALADA"]:
                x, y, width, height = coords
                frame = Frame(x, y, width, height, showBoundary=0)
                paragraph = Paragraph(value, paragraph_style)
                frame.addFromList([paragraph], c)
            else:
                x, y = coords
                if field == "PLANILLA":
                    c.setFont("Helvetica-Bold", 9.5)
                c.drawString(x, y, value)
                c.setFont("Helvetica", 6.5)  # Restablecer fuente

        c.save()

        # Crear archivo final con el nombre según el campo "RAZÓN SOCIAL"
        razon_social = self.fields["RAZÓN SOCIAL"].text or "sin_nombre"
        output_file = f"{GENERATED_FOLDER}/{razon_social}.pdf"

        reader = PdfReader(PDF_TEMPLATE)
        overlay_reader = PdfReader(f"{GENERATED_FOLDER}/temp_canvas.pdf")
        writer = PdfWriter()

        for page in reader.pages:
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        with open(output_file, "wb") as f:
            writer.write(f)

        # Cerrar animación de carga y confirmar éxito
        Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)
        Clock.schedule_once(lambda dt: self.show_popup("Éxito", f"PDF generado: {output_file}"), 0)

    def clear_fields(self, instance):
        for input_field in self.fields.values():
            input_field.text = ""

class PDFGeneratorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))

        # Cambiar a la pantalla principal después de 3 segundos
        def switch_to_main(*args):
            sm.current = "main"

        Clock.schedule_once(switch_to_main, 3)
        return sm

if __name__ == "__main__":
    # Crear carpetas si no existen
    os.makedirs("templates", exist_ok=True)
    os.makedirs("generated", exist_ok=True)
    PDFGeneratorApp().run()
