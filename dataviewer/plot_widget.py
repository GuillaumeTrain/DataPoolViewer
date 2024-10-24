import numpy as np
import pyqtgraph as pg
from PyDataCore import Data_Type
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from tabulate import tabulate


class SignalPlotWidget(QWidget):
    def __init__(self, data_pool, data_id, signal_name=None, color='b', parent=None):
        super().__init__(parent)
        self.data_pool = data_pool
        self.data_id = data_id

        # Récupérer les informations sur le signal
        data_info = self.data_pool.get_data_info(self.data_id)

        # Afficher le data_info avec tabulate pour debug
        print(tabulate(data_info, headers='keys', tablefmt='pretty'))

        # Récupérer l'objet réel depuis le DataFrame (colonne 'data_object')
        data_object = data_info['data_object'].iloc[0]  # .iloc[0] pour obtenir la première ligne
        self.data_type = data_object.data_type

        print(f"Data type: {self.data_type}")

        # Si le signal est temporel
        if self.data_type == Data_Type.TEMPORAL_SIGNAL:
            self.df = None
            self.dt = data_object.dt
            self.tmin = data_object.tmin
            self.unit = data_object.unit
            print(f"dt: {self.dt}, tmin: {self.tmin}, unit: {self.unit}")

        # Si le signal est fréquentiel
        elif self.data_type == Data_Type.FREQ_SIGNAL:
            self.df = data_object.df
            self.dt = None
            self.fmin = data_object.fmin
            self.unit = data_object.unit
            print(f"df: {self.df}, fmin: {self.fmin}, unit: {self.unit}")

        # Si le nom du signal n'est pas donné, utiliser le nom stocké dans les données
        if signal_name is None:
            self.signal_name = data_object.data_name
            print(f"Signal name not provided. Using data stored name: {self.signal_name}")
        else:
            self.signal_name = signal_name

        self.color = color  # Couleur du signal
        self.max_points = 500  # Limiter à 500 points affichés pour optimiser la performance

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Initialisation de l'affichage
        self.curve = self.plot_widget.plot(pen=pg.mkPen(self.color))

        # Configuration initiale du graphique
        self.plot_widget.setBackground('w')  # Fond blanc
        self.plot_widget.setTitle(self.signal_name)
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Connecter l'événement de changement de zoom
        self.plot_widget.getViewBox().sigXRangeChanged.connect(self.handle_zoom)

        # Définir les titres des axes en fonction du type de signal
        self.setup_axis_titles()

        # Affichage initial
        self.display_signal()

    def display_signal(self, x_range=None):
        """ Affiche le signal avec simplification chunk par chunk """
        num_samples = self.get_total_samples()

        # Si x_range n'est pas défini, on affiche tout le signal
        if x_range is None:
            x_range = [0, num_samples * (self.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else self.df)]

        # Calcul de la taille des chunks pour ne pas dépasser 500 points affichés
        if num_samples > self.max_points:
            chunk_size = num_samples // self.max_points
            num_chunks = self.max_points
        else:
            chunk_size = 1
            num_chunks = num_samples

        # Lire et simplifier les données chunk par chunk
        x_data = []
        y_data_min = []
        y_data_max = []

        for chunk_index in range(num_chunks):
            chunk_start = chunk_index * chunk_size
            chunk_end = min(chunk_start + chunk_size, num_samples)

            # Lire le chunk spécifique via la méthode read_specific_chunk
            chunk = self.data_pool.get_data_chunk(self.data_id, chunk_index, chunk_size=chunk_size)

            # Vérifier si le chunk est vide avant de continuer
            if len(chunk) == 0:
                # print(f"Chunk {chunk_index} is empty, skipping.")
                continue

            # Simplification (min et max)
            min_value = np.min(chunk)
            max_value = np.max(chunk)

            # Ajouter les valeurs simplifiées
            x_value = chunk_index * chunk_size * (self.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else self.df)
            x_data.append(x_value)
            y_data_min.append(min_value)
            y_data_max.append(max_value)

        # Combiner min et max pour les tracer ensemble
        x_data = np.repeat(x_data, 2)
        y_data = np.empty_like(x_data)
        y_data[0::2] = y_data_min
        y_data[1::2] = y_data_max

        # Mise à jour du graphique
        self.curve.setData(x_data, y_data)

    def handle_zoom(self, _, range):
        """ Gestion du zoom pour ajuster l'affichage à la nouvelle plage visible """
        x_min, x_max = range
        self.update_display_for_zoom(x_min, x_max)

    def update_display_for_zoom(self, x_min, x_max):
        """ Mets à jour l'affichage des données en fonction du zoom """
        num_samples = self.get_total_samples()

        # Conversion de la plage x en indices
        start_index = max(0, int(x_min / (self.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else self.df)))
        end_index = min(num_samples, int(x_max / (self.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else self.df)))

        visible_samples = end_index - start_index

        # Calculer la nouvelle taille des chunks pour correspondre au nombre de points visibles
        if visible_samples > self.max_points:
            chunk_size = visible_samples // self.max_points
        else:
            chunk_size = 1

        # Lire et simplifier les données correspondant à la plage de zoom
        x_data = []
        y_data_min = []
        y_data_max = []

        for chunk_index in range(start_index, end_index, chunk_size):
            chunk = self.data_pool.get_data_chunk(self.data_id, chunk_index // chunk_size, chunk_size=chunk_size)

            # Vérifier si le chunk est vide avant de continuer
            if len(chunk) == 0:
                print(f"Chunk {chunk_index} is empty, skipping.")
                continue

            # Simplification (min et max)
            min_value = np.min(chunk)
            max_value = np.max(chunk)

            x_value = chunk_index * (self.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else self.df)
            x_data.append(x_value)
            y_data_min.append(min_value)
            y_data_max.append(max_value)

        # Combiner min et max pour les tracer ensemble
        x_data = np.repeat(x_data, 2)
        y_data = np.empty_like(x_data)
        y_data[0::2] = y_data_min
        y_data[1::2] = y_data_max

        # Mise à jour du graphique
        self.curve.setData(x_data, y_data)

    def get_total_samples(self):
        """ Retourne le nombre total d'échantillons du signal """
        data_info = self.data_pool.get_data_info(self.data_id)
        return data_info['data_object'].iloc[0].num_samples  # Accéder à l'objet data et retourner num_samples

    def setup_axis_titles(self):
        """ Configure les titres des axes en fonction du type de signal """
        if self.data_type == Data_Type.TEMPORAL_SIGNAL:
            self.plot_widget.setLabel('bottom', 'Time', units='s')  # Axe des abscisses : temps (secondes)
        elif self.data_type == Data_Type.FREQ_SIGNAL:
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')  # Axe des abscisses : fréquence (Hz)

        # Axe des ordonnées avec l'unité fournie dans les données
        self.plot_widget.setLabel('left', f'Amplitude ({self.unit})')
