import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt


class SignalPlotWidget(QWidget):
    def __init__(self, signal_data, data_type, signal_name="Signal", fmin=None, tmin=None, df=None, dt=None, color='b',unit=None, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.signal_data = signal_data
        self.data_type = data_type  # TEMPORAL_SIGNAL ou FREQ_SIGNAL
        self.signal_name = signal_name  # Nom du signal à afficher dans le titre
        self.fmin = fmin
        self.tmin = tmin
        self.df = df
        self.dt = dt
        self.color = color  # Couleur du signal
        self.chunk_size = 100000  # Taille du chunk à partir duquel on commence la simplification

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Initialisation de l'affichage
        self.curve = self.plot_widget.plot(pen=pg.mkPen(self.color))

        # Variables pour le zoom
        self.zoom_factor = 1.0
        self.max_points = 100000
        self.x_min = None
        self.x_max = None

        # Configuration initiale du graphique
        self.plot_widget.setBackground('w')  # Fond blanc
        self.plot_widget.setTitle(self.signal_name)
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Gestion du zoom (molette)
        self.plot_widget.getViewBox().sigRangeChanged.connect(self.handle_zoom)

        # Définir les titres des axes en fonction du type de signal
        self.setup_axis_titles()

        # Affichage initial
        self.display_signal()

    def display_signal(self, x_range=None):
        """ Affiche le signal avec simplification si nécessaire """
        num_samples = len(self.signal_data)
        if self.dt is not None and self.x_min is None and self.x_max is None:
            self.x_min = 0
            self.x_max = num_samples * self.dt

        if x_range is not None:
            x_start, x_end = x_range
            start_idx = int(max(0, (x_start - self.x_min) / self.dt))
            end_idx = int(min(num_samples, (x_end - self.x_min) / self.dt))
        else:
            start_idx = 0
            end_idx = num_samples

        visible_data = self.signal_data[start_idx:end_idx]
        visible_x = np.arange(start_idx, end_idx) * self.dt

        # Si le nombre de points dépasse la limite, on applique une simplification
        if len(visible_data) > self.chunk_size:
            x, y = self.simplify_signal(visible_x, visible_data, self.chunk_size)
        else:
            x = visible_x
            y = visible_data

        # Mise à jour du graphique
        self.curve.setData(x, y)
        self.plot_widget.setLimits(xMin=self.x_min, xMax=self.x_max)  # Limiter les abscisses

    def simplify_signal(self, x_data, y_data, max_points):
        """ Simplifie le signal en utilisant la méthode du min/max pour chaque chunk """
        num_samples = len(y_data)
        chunk_size = max(num_samples // max_points, 1)  # Calcul de la taille des chunks

        # Découper les données en chunks
        num_chunks = num_samples // chunk_size
        remaining_samples = num_samples % chunk_size

        # Extraire min et max par chunk
        simplified_x = x_data[:num_chunks * chunk_size:chunk_size]
        simplified_y_min = np.min(y_data[:num_chunks * chunk_size].reshape(-1, chunk_size), axis=1)
        simplified_y_max = np.max(y_data[:num_chunks * chunk_size].reshape(-1, chunk_size), axis=1)

        # Gérer les samples restants
        if remaining_samples > 0:
            remaining_x = x_data[-remaining_samples:]
            remaining_y_min = np.min(y_data[-remaining_samples:])
            remaining_y_max = np.max(y_data[-remaining_samples:])
            simplified_x = np.append(simplified_x, remaining_x[0])
            simplified_y_min = np.append(simplified_y_min, remaining_y_min)
            simplified_y_max = np.append(simplified_y_max, remaining_y_max)

        # Intercaler min et max pour une visualisation correcte
        simplified_x = np.repeat(simplified_x, 2)
        simplified_y = np.empty(simplified_x.shape)
        simplified_y[0::2] = simplified_y_min
        simplified_y[1::2] = simplified_y_max

        return simplified_x, simplified_y

    def handle_zoom(self):
        """ Gestion du zoom, bloque le zoom max à la résolution du signal """
        x_range = self.plot_widget.getViewBox().viewRange()[0]

        # Limiter le zoom maximum à la résolution du signal (dt ou df)
        if self.dt and (x_range[1] - x_range[0]) < (10 * self.dt):
            self.plot_widget.setXRange(x_range[0], x_range[0] + 10 * self.dt)
        else:
            self.display_signal(x_range=x_range)

    def setup_axis_titles(self):
        """ Configure les titres des axes en fonction du type de signal """
        if self.data_type == 'TEMPORAL_SIGNAL':
            self.plot_widget.setLabel('bottom', 'Time', units='s')  # Axe des abscisses : temps (secondes)
        elif self.data_type == 'FREQ_SIGNAL':
            self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')  # Axe des abscisses : fréquence (Hz)

        # Axe des ordonnées avec l'unité fournie dans les données
        self.plot_widget.setLabel('left', f'Amplitude  ({self.unit})')
