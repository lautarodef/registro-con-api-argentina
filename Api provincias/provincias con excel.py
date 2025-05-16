import flet as ft
import requests
import pandas as pd
from datetime import datetime
import os

# Lista en memoria (útil para mostrar en pantalla)
ventas = []

# Obtener provincias ordenadas alfabéticamente
def obtener_provincias():
    url = "https://apis.datos.gob.ar/georef/api/provincias"
    resp = requests.get(url)
    data = resp.json()
    return sorted([p["nombre"] for p in data["provincias"]])

# Obtener localidades ordenadas alfabéticamente
def obtener_localidades(provincia):
    url = f"https://apis.datos.gob.ar/georef/api/localidades?provincia={provincia}&campos=nombre&max=1000"
    resp = requests.get(url)
    data = resp.json()
    return sorted([l["nombre"] for l in data["localidades"]])

# App principal
def main(page: ft.Page):
    page.title = "Registro de Ventas - Salidas de Escape"
    page.padding = 20
    page.bgcolor=ft.colors.RED_800
    

    # Componentes de selección
    provincia_dropdown = ft.Dropdown(label="Provincia", 
                                     width=250,
                                     border_color=ft.colors.BLACK,
                                     text_style=ft.TextStyle(color=ft.colors.BLACK,)
                                     )


    localidad_dropdown = ft.Dropdown(label="Ciudad", width=250,border_color=ft.colors.BLACK)
    modelo_dropdown = ft.Dropdown(label="SALIDA", width=250,border_color=ft.colors.BLACK,
                                  

        options=[
            ft.dropdown.Option("Modelo 1"),
            ft.dropdown.Option("Modelo 2"),
            ft.dropdown.Option("Modelo 3"),
            ft.dropdown.Option("Modelo 4"),
            ft.dropdown.Option("Modelo 5"),
        ]
    )

    # Texto para mostrar ventas
    ventas_text = ft.Text(value="", selectable=True)

    # Cargar provincias al inicio
    def cargar_provincias():
        provincias = obtener_provincias()
        provincia_dropdown.options = [ft.dropdown.Option(p) for p in provincias]
        page.update()

    # Cargar localidades según provincia seleccionada
    def on_provincia_changed(e):
        provincia = provincia_dropdown.value
        localidades = obtener_localidades(provincia)
        localidad_dropdown.options = [ft.dropdown.Option(l) for l in localidades]
        localidad_dropdown.value = None
        page.update()

    provincia_dropdown.on_change = on_provincia_changed

    # Mostrar ventas en pantalla
    def mostrar_ventas():
        texto = "\n".join([
            f"{v['Fecha']} - {v['Provincia']} - {v['Ciudad']} - {v['Modelo']}"
            for v in ventas
        ])
        ventas_text.value = texto
        page.update()

    # Registrar y guardar venta
    def registrar_venta(e):
        fecha = datetime.now().strftime("%Y-%m-%d")  
        provincia = provincia_dropdown.value
        ciudad = localidad_dropdown.value
        modelo = modelo_dropdown.value

        if provincia and ciudad and modelo:
            nueva_venta = {
                "Fecha": fecha,
                "Provincia": provincia,
                "Ciudad": ciudad,
                "Modelo": modelo
            }
            ventas.append(nueva_venta)
            mostrar_ventas()

            # Guardar en Excel
            archivo = "ventas.xlsx"
            df_nueva = pd.DataFrame([nueva_venta])

            if os.path.exists(archivo):
                df_existente = pd.read_excel(archivo)
                df_completo = pd.concat([df_existente, df_nueva], ignore_index=True)
            else:
                df_completo = df_nueva

            df_completo.to_excel(archivo, index=False)

            # Confirmación visual
            page.snack_bar = ft.SnackBar(
                ft.Text("✅ Venta registrada y guardada correctamente"),
                open=True
            )
            page.update()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("❗Debe seleccionar provincia, ciudad y modelo"),
                open=True
            )
            page.update()

    # Botón de registrar
    btn_registrar = ft.ElevatedButton("Registrar venta", on_click=registrar_venta)

    # Layout
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                provincia_dropdown,
                localidad_dropdown,
                btn_registrar,
                ft.Text("ventas registradas:", weight="bold"),ventas_text
              ],
            #   alignment=ft.MainAxisAlignment.CENTER,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True
        ),
        
    )

    # Cargar provincias al iniciar
    cargar_provincias()

# Ejecutar app
ft.app(target=main)
