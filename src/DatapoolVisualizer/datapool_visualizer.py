from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyDataCore import Data_Type
from src.DatapoolVisualizer.plot_controler import PlotController
from src.DatapoolVisualizer.datapool_viewer import DataPoolViewerWidget


class DatapoolVisualizer(QWidget):
    def __init__(self, data_pool, parent=None):
        super().__init__(parent)
        self.data_pool = data_pool

        # Création du layout principal
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Utiliser un QSplitter pour permettre un redimensionnement entre le TreeView et les Plots
        splitter = QSplitter()

        # Ajouter le DataPoolViewerWidget pour visualiser les données sous forme de TreeView
        self.data_pool_viewer = DataPoolViewerWidget(
            self.data_pool.data_registry,
            self.data_pool.source_to_data,
            self.data_pool.subscriber_to_data
        )
        splitter.addWidget(self.data_pool_viewer)

        # Ajouter le PlotController pour gérer les plots
        self.plot_controller = PlotController(self.data_pool)
        splitter.addWidget(self.plot_controller)

        # Ajouter le splitter dans le layout principal
        main_layout.addWidget(splitter)

        # Connecter l'événement de sélection d'une donnée dans le DataPoolViewerWidget
        self.data_pool_viewer.tree_view.clicked.connect(self.handle_data_selection)

    def handle_data_selection(self, index):
        """
        Handle data selection in DataPoolViewerWidget.
        Trigger playback for FFT data if selected.
        """
        item = self.data_pool_viewer.tree_view.model().itemFromIndex(index)
        if item is None:
            return

        # Extract data ID from selected item
        item_text = item.text()
        if "Data Name:" in item_text:
            data_id = self.extract_data_id_from_text(item_text)
            data_info = self.data_pool.get_data_info(data_id)
            data_type = data_info['data_object'].iloc[0].data_type

            # Route temporal, frequency, or FFT data types to PlotController
            if data_type in [Data_Type.TEMPORAL_SIGNAL, Data_Type.FREQ_SIGNAL, Data_Type.FFTS, Data_Type.FREQ_LIMIT,data_type.TEMP_LIMIT]:
                self.plot_controller.add_data_to_selected_plot(data_id)
            else:
                print(f"Data type {data_type} is not supported for plotting.")
        else:
            print("Selected item is not a data entry.")

    def extract_data_id_from_text(self, text):
        """
        Extrait l'ID de la donnée depuis le texte de l'élément.
        Le texte est supposé avoir le format "Data Name: <name> (ID: <id>, ...)"
        """
        start = text.find("ID: ") + 4
        end = text.find(",", start)
        return text[start:end]
