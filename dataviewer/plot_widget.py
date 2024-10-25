
import numpy as np
import pyqtgraph as pg
from PyDataCore import Data_Type
from PySide6.QtWidgets import QWidget, QVBoxLayout
from tabulate import tabulate


class SignalPlotWidget(QWidget):
    def __init__(self, data_pool, parent=None):
        super().__init__(parent)
        self.selected = False
        self.data_pool = data_pool
        self.data_id = None
        self.curves = {}  # Dictionnaire pour stocker les courbes par data_id
        self.max_points = 500  # Limiter à 500 points affichés pour optimiser la performance
        self.data_type = None
        self.x_min = None
        self.x_max = None

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Légende pour multiple signaux
        self.legend = self.plot_widget.addLegend(offset=(10, 10))
        self.plot_widget.setBackground('w')
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Limitation des axes par les données affichées
        self.plot_widget.getViewBox().sigXRangeChanged.connect(self.handle_zoom)
        self.plot_widget.scene().sigMouseClicked.connect(self.on_plot_clicked)

    def add_data(self, data_id, color='b'):
        """ Ajoute une courbe au plot. """
        if data_id in self.curves:
            print(f"Data {data_id} already displayed.")
            return

        # Récupération des informations sur les données
        data_info = self.data_pool.get_data_info(data_id)
        data_object = data_info['data_object'].iloc[0]
        is_limit = False
        # Vérification de compatibilité des types de données
        if not self.data_type:
            self.data_type = data_object.data_type
        if not self.is_compatible(data_id):
            print(f"Incompatible data type for plot. Expected {self.data_type}, got {data_object.data_type}")
            return
        if data_object.data_type == Data_Type.TEMP_LIMITS or data_object.data_type == Data_Type.FREQ_LIMITS:
            is_limit = True

        # Définition de la couleur par défaut pour les limites
        color = 'r' if is_limit else color

        # Initialisation des limites des abscisses
        if not self.x_min or not self.x_max:
            self.x_min, self.x_max = data_object.tmin, data_object.tmin + data_object.dt * data_object.num_samples

        # Ajout de la courbe et ajustement des limites
        curve = self.plot_widget.plot(pen=pg.mkPen(color))
        self.curves[data_id] = curve
        self.legend.addItem(curve, name=data_object.data_name)

        # Ajuste les limites si besoin
        if self.data_type == Data_Type.TEMPORAL_SIGNAL:
            self.x_min = min(self.x_min, data_object.tmin)
            self.x_max = max(self.x_max, data_object.tmin + data_object.dt * data_object.num_samples)
        elif self.data_type == Data_Type.FREQ_SIGNAL:
            self.x_min = min(self.x_min, data_object.fmin)
            self.x_max = max(self.x_max, data_object.fmin + data_object.df * data_object.num_samples)
        self.plot_widget.setLimits(xMin=self.x_min, xMax=self.x_max)

        # Affichage de la courbe
        self.display_signal(data_id, curve)

    def display_signal(self, data_id, curve=None):
        """ Affiche les données spécifiques à data_id avec simplification.
        :param
        data_id: ID de la donnée à afficher
        curve: Courbe à mettre à jour
        """
        data_object = self.data_pool.get_data_info(data_id)['data_object'].iloc[0]
        num_samples = data_object.num_samples
        dt = data_object.dt if self.data_type == Data_Type.TEMPORAL_SIGNAL else data_object.df
        chunk_size = max(1, num_samples // self.max_points)

        x_data, y_data_min, y_data_max = [], [], []

        for chunk_start in range(0, num_samples, chunk_size):
            chunk_end = min(chunk_start + chunk_size, num_samples)
            chunk = self.data_pool.get_data_chunk(data_id, chunk_start, chunk_size=chunk_size)

            if len(chunk) == 0:
                continue

            x_value = chunk_start * dt
            x_data.append(x_value)
            y_data_min.append(np.min(chunk))
            y_data_max.append(np.max(chunk))

        # Trace min/max data
        x_data = np.repeat(x_data, 2)
        y_data = np.empty_like(x_data)
        y_data[0::2], y_data[1::2] = y_data_min, y_data_max
        if curve:
            curve.setData(x_data, y_data)
        else:
            self.curves[data_id].setData(x_data, y_data)


    def handle_zoom(self, _, range):
        """ Ajuste l'affichage pour se limiter aux bornes du zoom. """
        x_min, x_max = range
        if x_min < self.x_min:
            x_min = self.x_min
        if x_max > self.x_max:
            x_max = self.x_max
        for data_id, curve in self.curves.items():
            self.display_signal(data_id, curve)

    def set_selection_style(self, is_selected):
        """ Appliquer un style visuel pour la sélection. """
        self.plot_widget.setBackground('lightgray' if is_selected else 'w')

    def on_plot_clicked(self, event):
        """ Gestion de clic pour sélection. """
        if self.plot_widget.sceneBoundingRect().contains(event.scenePos()):
            if not self.selected:
                self.select()
            else:
                self.deselect()

    def select(self):
        self.selected = True
        self.set_selection_style(True)

    def deselect(self):
        self.selected = False
        self.set_selection_style(False)

    def remove_data(self, data_id):
        """ Supprime une courbe spécifique du plot. """
        if data_id in self.curves:
            curve = self.curves.pop(data_id)
            self.legend.removeItem(curve)
            curve.clear()
            print(f"Removed curve for data_id {data_id}")

    def is_compatible(self, data_id):
        """
        Vérifie si la nouvelle donnée est compatible avec celles déjà affichées
        en fonction de l'axe des abscisses (temps/fréquence).
        Si le plot est vide (aucune donnée affichée), il est toujours compatible.
        """
        if not self.curves:
            return True

        new_data_info = self.data_pool.get_data_info(data_id)
        new_data_object = new_data_info['data_object'].iloc[0]
        new_data_type = new_data_object.data_type

        if new_data_type == self.data_type:
            return True

        if self.data_type == Data_Type.TEMPORAL_SIGNAL or self.data_type == Data_Type.TEMP_LIMITS:
            if new_data_type == Data_Type.TEMPORAL_SIGNAL or new_data_type == Data_Type.TEMP_LIMITS:
                return True
        elif self.data_type == Data_Type.FREQ_SIGNAL or self.data_type == Data_Type.FREQ_LIMITS:
            if new_data_type == Data_Type.FREQ_SIGNAL or new_data_type == Data_Type.FREQ_LIMITS:
                return True

        return False