import strawberry
from typing import List, Optional
import csv
import os


# Definir el tipo basado en las columnas del CSV
@strawberry.type
class ItemType:
    id_tie_fecha_valor: str
    id_cli_cliente: str
    id_ga_vista: str
    id_ga_tipo_dispositivo: str
    id_ga_fuente_medio: str
    desc_ga_sku_producto: str
    desc_ga_categoria_producto: Optional[str] 
    fc_agregado_carrito_cant: float
    fc_ingreso_producto_monto: float
    fc_retirado_carrito_cant: Optional[float] 
    fc_detalle_producto_cant: float
    fc_producto_cant: float
    desc_ga_nombre_producto: Optional[str] 
    fc_visualizaciones_pag_cant: float
    flag_pipol: str
    SASASA: str
    id_ga_producto: str
    desc_ga_nombre_producto_1: str
    desc_ga_sku_producto_1: str
    desc_ga_marca_producto: str
    desc_ga_cod_producto: str
    desc_categoria_producto: str
    desc_categoria_prod_principal: str


# Load CSV data
def load_csv_data(file_path: str) -> List[ItemType]:
    items = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert to  float numeric values  (handle data empty fields)
            row["fc_agregado_carrito_cant"] = (
                float(row["fc_agregado_carrito_cant"])
                if row["fc_agregado_carrito_cant"]
                else 0.0  # default if empty
            )
            row["fc_ingreso_producto_monto"] = (
                float(row["fc_ingreso_producto_monto"])
                if row["fc_ingreso_producto_monto"]
                else 0.0  
            )
            row["fc_retirado_carrito_cant"] = (
                float(row["fc_retirado_carrito_cant"])
                if row["fc_retirado_carrito_cant"]
                else None  
            )
            row["fc_detalle_producto_cant"] = (
                float(row["fc_detalle_producto_cant"])
                if row["fc_detalle_producto_cant"]
                else 0.0 
            )
            row["fc_producto_cant"] = (
                float(row["fc_producto_cant"])
                if row["fc_producto_cant"]
                else 0.0  
            )
            row["fc_visualizaciones_pag_cant"] = (
                float(row["fc_visualizaciones_pag_cant"])
                if row["fc_visualizaciones_pag_cant"]
                else 0.0  
            )

            # Create ItemType instance  
            items.append(
                ItemType(
                    id_tie_fecha_valor=row["id_tie_fecha_valor"],
                    id_cli_cliente=row["id_cli_cliente"],
                    id_ga_vista=row["id_ga_vista"],
                    id_ga_tipo_dispositivo=row["id_ga_tipo_dispositivo"],
                    id_ga_fuente_medio=row["id_ga_fuente_medio"],
                    desc_ga_sku_producto=row["desc_ga_sku_producto"],
                    desc_ga_categoria_producto=row["desc_ga_categoria_producto"],
                    fc_agregado_carrito_cant=row["fc_agregado_carrito_cant"],
                    fc_ingreso_producto_monto=row["fc_ingreso_producto_monto"],
                    fc_retirado_carrito_cant=row["fc_retirado_carrito_cant"],
                    fc_detalle_producto_cant=row["fc_detalle_producto_cant"],
                    fc_producto_cant=row["fc_producto_cant"],
                    desc_ga_nombre_producto=row["desc_ga_nombre_producto"],
                    fc_visualizaciones_pag_cant=row["fc_visualizaciones_pag_cant"],
                    flag_pipol=row["flag_pipol"],
                    SASASA=row["SASASA"],
                    id_ga_producto=row["id_ga_producto"],
                    desc_ga_nombre_producto_1=row["desc_ga_nombre_producto_1"],
                    desc_ga_sku_producto_1=row["desc_ga_sku_producto_1"],
                    desc_ga_marca_producto=row["desc_ga_marca_producto"],
                    desc_ga_cod_producto=row["desc_ga_cod_producto"],
                    desc_categoria_producto=row["desc_categoria_producto"],
                    desc_categoria_prod_principal=row["desc_categoria_prod_principal"],
                )
            )
    return items
