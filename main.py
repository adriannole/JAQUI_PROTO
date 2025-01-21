import os
import threading
from datetime import datetime
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
from kivy.uix.spinner import Spinner
from kivy.animation import Animation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame, Paragraph
from PyPDF2 import PdfReader, PdfWriter
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown

Window.clearcolor = (0.95, 0.95, 0.95, 1)

# Ruta de la plantilla PDF
PDF_TEMPLATE = "templates/PLANILLA_GLOBAL.pdf"
GENERATED_FOLDER = "generated"

# Listas de provincias y cantones
PROVINCIAS_CANTONES = {
    "Azuay": ["Cuenca", "Gualaceo", "Paute", "Nabón", "Girón", "Chordeleg", "Sígsig", "Sevilla de Oro", "Guachapala", "El Pan", "Oña", "Santa Isabel", "Pucará"],
    "Bolívar": ["Guaranda", "San Miguel", "Chillanes", "Echeandía", "Caluma", "Las Naves", "Chimbo"],
    "Cañar": ["Azogues", "Biblián", "Cañar", "La Troncal", "El Tambo", "Déleg", "Suscal"],
    "Carchi": ["Tulcán", "Montúfar", "San Pedro de Huaca", "Mira", "Bolívar", "Espejo"],
    "Chimborazo": ["Riobamba", "Guano", "Colta", "Chambo", "Alausí", "Guamote", "Cumandá", "Pallatanga", "Penipe"],
    "Cotopaxi": ["Latacunga", "Pujilí", "Salcedo", "Saquisilí", "Sigchos", "La Maná"],
    "El Oro": ["Machala", "Pasaje", "Santa Rosa", "Huaquillas", "Arenillas", "Zaruma", "Piñas", "Portovelo", "El Guabo", "Atahualpa", "Chilla", "Las Lajas"],
    "Esmeraldas": ["Esmeraldas", "Atacames", "Quinindé", "San Lorenzo", "Muisne", "Rioverde", "Eloy Alfaro"],
    "Galápagos": ["Puerto Ayora", "Puerto Villamil", "Puerto Baquerizo Moreno"],
    "Guayas": ["Guayaquil", "Samborondón", "Daule", "Durán", "Milagro", "Playas", "Salitre", "Balao", "Naranjal", "El Triunfo", "Naranjito", "Balzar", "Colimes", "Pedro Carbo", "Yaguachi", "Simón Bolívar", "Isidro Ayora"],
    "Imbabura": ["Ibarra", "Otavalo", "Cotacachi", "Antonio Ante", "Pimampiro", "Urcuquí"],
    "Loja": ["Loja", "Catamayo", "Macará", "Paltas", "Saraguro", "Calvas", "Chaguarpamba", "Espíndola", "Gonzanamá", "Olmedo", "Pindal", "Puyango", "Quilanga", "Sozoranga", "Zapotillo"],
    "Los Ríos": ["Babahoyo", "Quevedo", "Vinces", "Ventanas", "Puebloviejo", "Buena Fe", "Mocache", "Quinsaloma", "Urdaneta", "Palenque"],
    "Manabí": ["Portoviejo", "Manta", "Chone", "Jipijapa", "Montecristi", "Sucre", "Pedernales", "Bahía de Caráquez", "Rocafuerte", "Santa Ana", "Tosagua", "Pichincha", "Bolívar", "El Carmen", "Jama", "Flavio Alfaro", "San Vicente"],
    "Morona Santiago": ["Macas", "Gualaquiza", "Sucúa", "Logroño", "Palora", "Huamboya", "San Juan Bosco", "Taisha", "Tiwintza", "Limón Indanza", "Pablo Sexto"],
    "Napo": ["Tena", "Archidona", "El Chaco", "Quijos", "Carlos Julio Arosemena Tola"],
    "Orellana": ["Francisco de Orellana", "La Joya de los Sachas", "Loreto", "Aguarico"],
    "Pastaza": ["Puyo", "Mera", "Santa Clara", "Arajuno"],
    "Pichincha": ["Quito", "Cayambe", "Mejía", "Pedro Moncayo", "Rumiñahui", "Pedro Vicente Maldonado", "San Miguel de los Bancos"],
    "Santa Elena": ["Santa Elena", "La Libertad", "Salinas"],
    "Santo Domingo de los Tsáchilas": ["Santo Domingo", "La Concordia"],
    "Sucumbíos": ["Lago Agrio", "Shushufindi", "Cuyabeno", "Putumayo", "Gonzalo Pizarro", "Sucumbíos"],
    "Tungurahua": ["Ambato", "Baños", "Pelileo", "Píllaro", "Cevallos", "Tisaleo", "Mocha", "Quero"],
    "Zamora Chinchipe": ["Zamora", "Yantzaza", "El Pangui", "Centinela del Cóndor", "Nangaritza", "Palanda", "Chinchipe", "Paquisha"]
}

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=20)
        self.logo = Image(source="images/logo.png", size_hint=(1, 0.7))
        self.layout.add_widget(self.logo)

        self.label = Label(
            text="[b][color=#000000]TECMAN PDF GENERATOR V1.0[/color][/b]",
            markup=True,
            font_size=24,
            bold=True,
            halign="center",
            valign="middle",
        )

        self.layout.add_widget(self.label)

        self.add_widget(self.layout)
        self.start_animation()

    def start_animation(self):
        anim = Animation(color=(1, 1, 1, 1), font_size=40, duration=0.5)
        anim.start(self.label)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source="images/background.png", size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)

        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=25)

        scroll_view = ScrollView(size_hint=(1, 0.8))
        form_layout = GridLayout(cols=2, padding=20, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        self.fields = {
            "PLANILLA": TextInput(hint_text="Número de planilla N° UIO-XX", multiline=False, input_filter="int"),
            "PROVINCIA": Spinner(text="Selecciona una provincia", size_hint=(1, None), height=dp(30)),
            "CANTÓN": Spinner(text="Selecciona un cantón", size_hint=(1, None), height=dp(30)),
            "USUARIO ": TextInput(hint_text="Usuario responsable", multiline=False),
            "CORREO": TextInput(hint_text="Correo electrónico", multiline=False),
            "TELÉFONO": TextInput(hint_text="Teléfono de contacto", multiline=False),
            "RAZÓN SOCIAL": TextInput(hint_text="Razón social o nombre", multiline=False),
            "DIRECCION": TextInput(hint_text="Escribe la dirección", multiline=False),
            "FECHA": TextInput(hint_text="DD/MM/AAAA", multiline=False, readonly=False),
            "DEPARTAMENTO/PISO": TextInput(hint_text="Departamento o unidad", multiline=False),
            "CONTADOR": TextInput(hint_text="Nombre del contador", multiline=False),
            "SERIE": TextInput(hint_text="Número de serie", multiline=False),
            "OBSERVACIONES": TextInput(hint_text="Observaciones generales", multiline=True),
            "PARTE AFECTADA": TextInput(hint_text="Descripción de la parte afectada", multiline=True),
            "PARTE INSTALADA": TextInput(hint_text="Descripción de la parte instalada", multiline=True),
            "TECNICO RESPONSABLE": TextInput(hint_text="Nombre del tecnico responsable", multiline=False),
        }

        for label, input_field in self.fields.items():
            form_layout.add_widget(Label(text=label, size_hint=(0.3, None), height=dp(35), font_size=12, bold=True, color=(0, 0, 0, 1)))
            if label == "FECHA":
                date_layout = BoxLayout(orientation="horizontal")
                date_layout.add_widget(input_field)
                date_button = Button(text="Hoy", size_hint=(0.3, None), height=dp(35))
                date_button.bind(on_press=self.set_today_date)
                date_layout.add_widget(date_button)
                form_layout.add_widget(date_layout)
            else:
                form_layout.add_widget(input_field)

        self.fields["PROVINCIA"].values = ()
        self.province_dropdown = DropDown()
        self.province_dropdown.background_normal = ''
        self.province_dropdown.background_color = (0.1, 0.1, 0.2, 1)
        grid = GridLayout(cols=2, spacing=5, padding=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for prov in PROVINCIAS_CANTONES.keys():
            btn = Button(text=prov, size_hint_y=None, height=dp(30))
            btn.background_normal = ''
            btn.background_color = (0.1, 0.1, 0.2, 1)
            btn.color = (1, 1, 1, 1)
            btn.bind(on_release=lambda btn: self.province_dropdown.select(btn.text))
            grid.add_widget(btn)
        self.province_dropdown.add_widget(grid)
        self.fields["PROVINCIA"].bind(on_release=self.province_dropdown.open)
        self.province_dropdown.bind(
            on_select=lambda instance, x: setattr(self.fields["PROVINCIA"], 'text', x)
        )

        with self.province_dropdown.canvas.before:
            Color(0.1, 0.1, 0.2, 1)
            self.dropdown_bg_rect = Rectangle()

        self.province_dropdown.bind(size=self.update_dropdown_bg, pos=self.update_dropdown_bg)

        self.fields["PROVINCIA"].bind(text=self.update_cantones)

        scroll_view.add_widget(form_layout)

        button_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)
        self.generate_button = Button(
            text="Generar PDF",
            font_size=14,
            background_color=(0, 0.6, 0.8, 1),
            size_hint=(0.5, 0.5)
        )
        self.generate_button.bind(on_press=self.check_fields_and_generate_pdf)

        self.clear_button = Button(
            text="Nuevo Registro",
            font_size=14,
            background_color=(0.9, 0.2, 0.2, 1),
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

    def update_cantones(self, spinner, provincia):
        self.fields["CANTÓN"].values = PROVINCIAS_CANTONES.get(provincia, [])

    def set_today_date(self, instance):
        self.fields["FECHA"].text = datetime.now().strftime("%d/%m/%Y")

    def check_fields_and_generate_pdf(self, instance):
        missing_fields = [field for field, input_field in self.fields.items() if not input_field.text and field not in ["OBSERVACIONES", "PARTE AFECTADA", "PARTE INSTALADA"]]
        if missing_fields:
            self.show_popup("Aviso", f"Faltan los campos: {', '.join(missing_fields)}.")
            return

        if "@" not in self.fields["CORREO"].text:
            self.show_popup("Error", "Correo no válido. Asegúrate de incluir '@'.")
            return

        self.show_loading_popup()
        threading.Thread(target=self.generate_pdf).start()

    def show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size=14))
        close_button = Button(text="Cerrar", size_hint=(1, 0.3))
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        close_button.bind(on_press=popup.dismiss)
        content.add_widget(close_button)
        popup.open()

    def show_loading_popup(self):
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        progress_bar = ProgressBar(max=100, value=0)
        content.add_widget(progress_bar)
        self.loading_popup = Popup(title="Generando PDF", content=content, size_hint=(0.5, 0.5), auto_dismiss=False)
        self.loading_popup.open()

        def update_progress(dt):
            progress_bar.value += 5
            if progress_bar.value >= 100:
                Clock.unschedule(update_progress)

        Clock.schedule_interval(update_progress, 0.1)

    def generate_pdf(self):
        c = canvas.Canvas(f"{GENERATED_FOLDER}/temp_canvas.pdf", pagesize=letter)
        c.setFont("Helvetica", 6.5)

        coordinates = {
            "PLANILLA": (504, 655),
            "PROVINCIA": (330, 576),
            "CANTÓN": (458, 576),
            "USUARIO ": (390, 123),
            "CORREO": (398, 627),
            "TELÉFONO": (396, 612),
            "RAZÓN SOCIAL": (130, 627),
            "DIRECCION": (130, 612),
            "FECHA": (130, 596),
            "DEPARTAMENTO/PISO": (396, 596),
            "CONTADOR": (396, 549),
            "SERIE": (458, 549),
            "OBSERVACIONES": (72, 349, 494, 90),
            "PARTE AFECTADA": (69, 249, 200, 75),
            "PARTE INSTALADA": (69, 179, 200, 75),
            "TECNICO RESPONSABLE": (198, 122),
        }

        paragraph_style = ParagraphStyle(
            "CustomParagraph",
            fontName="Helvetica",
            fontSize=7,
            leading=13,
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

        Clock.schedule_once(lambda dt: self.loading_popup.dismiss(), 0)
        Clock.schedule_once(lambda dt: self.show_popup("Éxito", f"PDF generado: {output_file}"), 0)

    def clear_fields(self, instance):
        for input_field in self.fields.values():
            input_field.text = ""

    def update_dropdown_bg(self, *args):
        self.dropdown_bg_rect.size = self.province_dropdown.size
        self.dropdown_bg_rect.pos = self.province_dropdown.pos

class PDFGeneratorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))

        def switch_to_main(*args):
            sm.current = "main"

        Clock.schedule_once(switch_to_main, 3)
        return sm

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("generated", exist_ok=True)
    PDFGeneratorApp().run()
