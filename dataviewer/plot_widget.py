import numpy as np
from PyDataCore import Data_Type
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSlider, QPushButton, QHBoxLayout
import pyqtgraph as pg
from scipy.stats import alpha


class SignalPlotWidget(QWidget):
    # def __init__(self, data_pool, parent=None):
    #     super().__init__(parent)
    #     self.selected = False
    #     self.data_pool = data_pool
    #     self.curves = {}  # Stocker les courbes par data_id
    #     self.extra_axes = []  # Stocker les (AxisItem, ViewBox)
    #     self.max_points = 500  # Limite de points affichés pour les performances
    #     self.data_type = None
    #     self.x_min = None
    #     self.x_max = None
    #
    #     # PyQtGraph plot widget
    #     self.plot_widget = pg.PlotWidget()
    #     layout = QVBoxLayout()
    #     layout.addWidget(self.plot_widget)
    #     self.setLayout(layout)
    #
    #     # Légende pour les courbes multiples
    #     self.legend = self.plot_widget.addLegend(offset=(10, 10))
    #     self.plot_widget.setBackground('w')
    #     self.plot_widget.setMouseEnabled(x=True, y=True)
    #     self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
    #
    #     # Assurer la synchronisation des vues
    #     self.plot_widget.getViewBox().sigXRangeChanged.connect(self.handle_zoom)
    #     self.plot_widget.scene().sigMouseClicked.connect(self.on_plot_clicked)
    #
    #     # Assurer que l'axe Y gauche est visible dès le départ
    #     self.plot_widget.plotItem.showAxis('right')
    #     self.plot_widget.plotItem.hideAxis('left')
    #     self.plot_widget.plotItem.showLabel('right')
    #
    #     # Synchroniser les redimensionnements pour les ViewBox
    #     self.plot_widget.plotItem.vb.sigResized.connect(self.update_viewbox_geometry)
    def __init__(self, data_pool, parent=None):
        super().__init__(parent)
        self.selected = False
        self.data_pool = data_pool
        self.curves = {}
        self.extra_axes = []
        self.max_points = 500
        self.data_type = None
        self.x_min = None
        self.x_max = None
        self.fft_timer = QTimer(self)  # Timer for FFT animation
        self.fft_timer.timeout.connect(self.update_animation_frame)
        self.current_frame = 0  # Current frame in the FFT sequence
        self.is_animating = False  # Animation state

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

        # Animation Controls
        self.init_animation_controls(layout)

        # Legend and plot setup
        self.legend = self.plot_widget.addLegend(offset=(10, 10))
        self.plot_widget.setBackground('w')
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Sync view boxes
        self.plot_widget.getViewBox().sigXRangeChanged.connect(self.handle_zoom)
        self.plot_widget.scene().sigMouseClicked.connect(self.on_plot_clicked)
        self.plot_widget.plotItem.showAxis('right')
        self.plot_widget.plotItem.hideAxis('left')
        self.plot_widget.plotItem.showLabel('right')
        self.plot_widget.plotItem.vb.sigResized.connect(self.update_viewbox_geometry)

    def add_data(self, data_id, color='b'):
        """ Ajouter une courbe au graphique et lui assigner un axe Y si nécessaire. """
        """Add data to the plot and handle FFTS data specifically for animation."""
        data_info = self.data_pool.get_data_info(data_id)
        data_object = data_info['data_object'].iloc[0]

        # Check if this is FFT data
        if data_object.data_type == Data_Type.FFTS:
            self.setup_fft_animation(data_object, color)
            return  # FFT data handled, no further processing

        if data_id in self.curves:
            print(f"Data {data_id} already displayed.")
            return

        # Récupération des informations de la donnée
        data_info = self.data_pool.get_data_info(data_id)
        data_object = data_info['data_object'].iloc[0]
        is_limit = False

        # Déterminer si la donnée est une limite
        if data_object.data_type in (Data_Type.TEMP_LIMITS, Data_Type.FREQ_LIMITS):
            is_limit = True

        # Couleur par défaut pour les limites
        color = 'r' if is_limit else color

        # Initialisation des x_min et x_max pour le graphique selon le type de signal
        if data_object.data_type == Data_Type.TEMPORAL_SIGNAL:
            if self.x_min is None or self.x_max is None:
                self.x_min = data_object.tmin
                self.x_max = data_object.tmin + data_object.dt * data_object.num_samples
        elif data_object.data_type == Data_Type.FREQ_SIGNAL:
            if self.x_min is None or self.x_max is None:
                self.x_min = data_object.fmin
                self.x_max = data_object.fmin + data_object.df * data_object.num_samples

        # Si c'est la première courbe, créer un ViewBox séparé pour elle
        if len(self.curves) == 0:
            # Créer un ViewBox séparé pour la première courbe
            viewbox = pg.ViewBox()
            self.plot_widget.scene().addItem(viewbox)
            viewbox.setXLink(self.plot_widget.plotItem.vb)  # Lier l'axe X avec le ViewBox principal

            # Ajouter un axe Y à droite pour la première courbe
            #cacher l'axe Y par défaut
            self.plot_widget.plotItem.hideAxis('right')

            axis = pg.AxisItem('right')
            self.plot_widget.plotItem.layout.addItem(axis, 2, 3)  # Placer à droite du graphique
            axis.linkToView(viewbox)  # Lier l'axe Y au ViewBox
            axis.setLabel(data_object.data_name, color=color)
            # axis.setPen(pg.mkPen(color))
            axis.setGrid(150)

            # Ajouter la courbe au ViewBox séparé
            curve = pg.PlotCurveItem(pen=pg.mkPen(color))
            viewbox.addItem(curve)

            # Désactiver l'auto-scaling du ViewBox principal (pour la première courbe)
            self.plot_widget.getViewBox().enableAutoRange(False, y=False)
            self.plot_widget.getViewBox().setYRange(-10, 10)  # Fixer des limites manuelles de l'axe Y si nécessaire

            # Stocker la courbe, l'axe et le ViewBox
            self.extra_axes.append((axis, viewbox))
        else:
            # Ajouter un axe Y supplémentaire à droite pour les courbes suivantes
            viewbox = pg.ViewBox()
            self.plot_widget.scene().addItem(viewbox)
            viewbox.setXLink(self.plot_widget.plotItem.vb)  # Lier l'axe X avec le ViewBox principal

            # Créer un nouvel axe Y à droite pour la courbe supplémentaire
            axis = pg.AxisItem('right')
            self.plot_widget.plotItem.layout.addItem(axis, 2, 3 + len(self.extra_axes))  # Ajouter l'axe à droite
            axis.linkToView(viewbox)  # Lier l'axe Y au ViewBox
            axis.setLabel(data_object.data_name, color=color)
            # axis.setPen(pg.mkPen(color))
            # axis.setGrid(255)

            # Ajouter la courbe au nouveau ViewBox
            curve = pg.PlotCurveItem(pen=pg.mkPen(color))
            viewbox.addItem(curve)

            # Stocker l'axe et le ViewBox pour les courbes supplémentaires
            self.extra_axes.append((axis, viewbox))

        # Ajouter la courbe à la liste des courbes tracées
        self.curves[data_id] = curve
        self.legend.addItem(curve, name=data_object.data_name)

        # Mettre à jour les limites en fonction de la nouvelle courbe
        if data_object.data_type == Data_Type.TEMPORAL_SIGNAL:
            self.x_min = min(self.x_min, data_object.tmin)
            self.x_max = max(self.x_max, data_object.tmin + data_object.dt * data_object.num_samples)
        elif data_object.data_type == Data_Type.FREQ_SIGNAL:
            self.x_min = min(self.x_min, data_object.fmin)
            self.x_max = max(self.x_max, data_object.fmin + data_object.df * data_object.num_samples)

        self.plot_widget.setLimits(xMin=self.x_min, xMax=self.x_max)

        # Afficher les données du signal
        self.display_signal(data_id, curve)

        # Synchroniser les ViewBox avec le graphique principal
        self.update_viewbox_geometry()

    def add_curve_with_extra_axis(self, curve, label, color):
        """ Ajouter une courbe avec son propre axe Y à droite. """
        viewbox = pg.ViewBox()
        self.plot_widget.scene().addItem(viewbox)
        viewbox.setXLink(self.plot_widget.plotItem.vb)  # Lier l'axe X avec le ViewBox principal

        # Créer un nouvel axe Y à droite
        axis = pg.AxisItem('right')
        self.plot_widget.plotItem.layout.addItem(axis, 2, 3 + len(self.extra_axes))  # Ajouter l'axe à droite
        axis.linkToView(viewbox)  # Lier l'axe Y au ViewBox
        axis.setLabel(label, color=color)
        # axis.setPen(pg.mkPen(color))
        #afficher la grille
        # axis.setGrid(255)

        # Ajouter la courbe au nouveau ViewBox (lié au nouvel axe Y)
        viewbox.addItem(curve)
        self.extra_axes.append((axis, viewbox))

        # S'assurer que les ViewBox sont bien synchronisés avec la taille du graphique
        self.update_viewbox_geometry()

    def display_signal(self, data_id, curve=None):
        """ Afficher les données pour un data_id spécifique """
        data_object = self.data_pool.get_data_info(data_id)['data_object'].iloc[0]
        num_samples = data_object.num_samples
        dt = data_object.dt if data_object.data_type == Data_Type.TEMPORAL_SIGNAL else data_object.df
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

        # Affichage des points min/max
        x_data = np.repeat(x_data, 2)
        y_data = np.empty_like(x_data)
        y_data[0::2], y_data[1::2] = y_data_min, y_data_max
        if curve:
            curve.setData(x_data, y_data)
        else:
            self.curves[data_id].setData(x_data, y_data)

    def handle_zoom(self, _, range):
        """ Ajuster l'affichage du zoom. """
        x_min, x_max = range
        if x_min < self.x_min:
            x_min = self.x_min
        if x_max > self.x_max:
            x_max = self.x_max
        for data_id, curve in self.curves.items():
            self.display_signal(data_id, curve)

    def update_viewbox_geometry(self):
        """ S'assurer que tous les ViewBox sont synchronisés avec la géométrie du graphique principal. """
        for _, viewbox in self.extra_axes:
            viewbox.setGeometry(self.plot_widget.plotItem.vb.sceneBoundingRect())
            viewbox.linkedViewChanged(self.plot_widget.plotItem.vb, viewbox.XAxis)

    def set_selection_style(self, is_selected):
        """ Appliquer un style visuel pour la sélection. """
        self.plot_widget.setBackground('lightgray' if is_selected else 'w')

    def on_plot_clicked(self, event):
        """ Gestion de l'événement de clic pour la sélection du graphique. """
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
        """ Supprimer une courbe spécifique du graphique. """
        if data_id in self.curves:
            curve = self.curves.pop(data_id)
            self.legend.removeItem(curve)
            curve.clear()
            print(f"Removed curve for data_id {data_id}")

    def is_compatible(self, data_id):
        """
        Vérifier si la nouvelle donnée est compatible avec celles déjà affichées.
        Si le graphique est vide, elle est toujours compatible.
        """
        if not self.curves:
            return True

        new_data_info = self.data_pool.get_data_info(data_id)
        new_data_object = new_data_info['data_object'].iloc[0]
        new_data_type = new_data_object.data_type
        print(f"New data type: {new_data_type} - Current data type: {self.data_type}")
        if new_data_type == self.data_type or self.data_type is None:
            return True

        if self.data_type == Data_Type.TEMPORAL_SIGNAL or self.data_type == Data_Type.TEMP_LIMITS:
            if new_data_type == Data_Type.TEMPORAL_SIGNAL or new_data_type == Data_Type.TEMP_LIMITS:
                return True
        elif self.data_type == Data_Type.FREQ_SIGNAL or self.data_type == Data_Type.FREQ_LIMITS:
            if new_data_type == Data_Type.FREQ_SIGNAL or new_data_type == Data_Type.FREQ_LIMITS:
                return True

        return False

    def init_animation_controls(self, layout):
        """ Initialize animation playback controls for FFT data. """
        control_layout = QHBoxLayout()

        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_animation)
        control_layout.addWidget(self.play_button)

        # Pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_animation)
        control_layout.addWidget(self.pause_button)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_animation)
        control_layout.addWidget(self.stop_button)

        # Timestamp slider
        self.timestamp_slider = QSlider()
        self.timestamp_slider.setOrientation(pg.QtCore.Qt.Horizontal)
        self.timestamp_slider.valueChanged.connect(self.seek_frame)
        control_layout.addWidget(self.timestamp_slider)

        # Current frame label
        self.frame_label = QLabel("Frame: 0")
        control_layout.addWidget(self.frame_label)

        layout.addLayout(control_layout)

    def setup_fft_animation(self, fft_data, color):
        """Setup the plot and slider for FFT animation."""
        self.fft_data = fft_data  # Store FFT data for playback
        self.timestamp_slider.setMaximum(len(fft_data.fft_signals) - 1)
        self.timestamp_slider.setValue(0)
        self.current_frame = 0
        self.is_animating = False

        # Create a curve for FFT data
        self.fft_curve = self.plot_widget.plot(pen=pg.mkPen(color))
        self.curves[fft_data.data_id] = self.fft_curve
        self.legend.addItem(self.fft_curve, name=fft_data.data_name)

        # Display the first frame
        self.display_fft_frame(0)

    def display_fft_frame(self, frame_index):
        """Display a single FFT frame (frequency domain data) by index."""
        fft_signal = self.fft_data.fft_signals[frame_index]
        freq_range = np.linspace(fft_signal.fmin, fft_signal.fmin + fft_signal.df * fft_signal.num_samples,
                                 fft_signal.num_samples)
        self.fft_curve.setData(freq_range, fft_signal.data)
        self.frame_label.setText(f"Frame: {frame_index}")

    def play_animation(self):
        """Start or resume the FFT animation."""
        if not self.is_animating:
            self.fft_timer.start(100)  # Update every 100 ms
            self.is_animating = True

    def pause_animation(self):
        """Pause the FFT animation."""
        self.fft_timer.stop()
        self.is_animating = False

    def stop_animation(self):
        """Stop the FFT animation and reset to the first frame."""
        self.fft_timer.stop()
        self.is_animating = False
        self.current_frame = 0
        self.timestamp_slider.setValue(0)
        self.display_fft_frame(0)

    def update_animation_frame(self):
        """Advance the animation to the next frame."""
        if self.current_frame < len(self.fft_data.fft_signals) - 1:
            self.current_frame += 1
            self.timestamp_slider.setValue(self.current_frame)
            self.display_fft_frame(self.current_frame)
        else:
            self.stop_animation()  # End animation when reaching the last frame

    def seek_frame(self, frame_index):
        """Seek to a specific frame in the FFT animation."""
        self.current_frame = frame_index
        self.display_fft_frame(frame_index)
