import processing
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsCoordinateTransform
)
from PyQt5.QtCore import QVariant

#Diálogo para selecionar o arquivo
file_dialog = QFileDialog()
file_path, _ = file_dialog.getOpenFileName(None, "Selecione o arquivo vetorial", "", "Todos os arquivos (*)")

if not file_path:
    print("Nenhum arquivo selecionado.")
else:
    #Carregar a camada a partir do arquivo selecionado
    layer = QgsVectorLayer(file_path, "Camada Original", "ogr")
    if not layer.isValid():
        print("Falha ao carregar a camada.")
    else:
        #Defina o sistema de coordenadas de destino (EPSG code)
        dest_crs = 'EPSG:4674'  #Exemplo: SIRGAS2000

        #Reprojetar a camada
        reprojected_layer = processing.run("native:reprojectlayer", {
            'INPUT': layer,
            'TARGET_CRS': QgsCoordinateReferenceSystem(dest_crs),
            'OUTPUT': 'memory:'
        })['OUTPUT']

        QgsProject.instance().addMapLayer(reprojected_layer)

  #Defina as novas colunas a serem adicionadas
        new_fields = [
            QgsField("solicitante", QVariant.String),
            QgsField("nome", QVariant.String),
            QgsField("descricao", QVariant.String),
            QgsField("executor", QVariant.String),
        ]

        #Adicionar novas colunas à camada reprojetada
        reprojected_layer.startEditing()
        for field in new_fields:
            if reprojected_layer.fields().indexFromName(field.name()) == -1:
                reprojected_layer.addAttribute(field)
        reprojected_layer.updateFields()

        #Definir os valores das colunas especificadas
        for feature in reprojected_layer.getFeatures():
            reprojected_layer.changeAttributeValue(feature.id(), reprojected_layer.fields().indexFromName('executor'), "Empresa W")
            reprojected_layer.changeAttributeValue(feature.id(), reprojected_layer.fields().indexFromName('nome'), "Area de estudo W")
            reprojected_layer.changeAttributeValue(feature.id(), reprojected_layer.fields().indexFromName('solicitante'), "Solicitante W")
            reprojected_layer.changeAttributeValue(feature.id(), reprojected_layer.fields().indexFromName('descricao'), "Monitoramento da area W")

        reprojected_layer.commitChanges()

        #Excluir colunas antigas
        reprojected_layer.startEditing()
        fields_to_keep = [field.name() for field in new_fields]
        fields_to_delete = [field.name() for field in reprojected_layer.fields() if field.name() not in fields_to_keep]
        
        reprojected_layer.dataProvider().deleteAttributes([reprojected_layer.fields().indexFromName(field) for field in fields_to_delete])
        reprojected_layer.updateFields()
        reprojected_layer.commitChanges()

        print("Camada reprojetada, colunas adicionadas, valores preenchidos e colunas antigas excluídas com sucesso.")
