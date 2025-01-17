from reportlab.pdfgen import canvas

def test_coordinates(pdf_path):
    c = canvas.Canvas(pdf_path)

    # Dibuja un grid de referencia en el PDF
    for x in range(0, 600, 50):  # Intervalos horizontales
        for y in range(0, 800, 50):  # Intervalos verticales
            c.drawString(x, y, f"({x},{y})")

    c.save()

if __name__ == "__main__":
    test_coordinates("generated/coordinate_test.pdf")
