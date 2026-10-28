from src.carga import cargar_datos, inspeccionar_datos, validar_estructura


def main():
    ruta = "datos/owid-co2-data.csv"
    datos = cargar_datos(ruta)

    if datos is not None:
        print("Carga realizada correctamente.")
        validar_estructura(datos)
        inspeccionar_datos(datos)
    else:
        print("El programa finalizó sin procesar los datos.")


if __name__ == "__main__":
    main()
