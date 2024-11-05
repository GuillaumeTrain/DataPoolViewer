import PyDataCore
import numpy as np
from PyDataCore import Data_Type, FreqSignalData, FFTSData, TemporalSignalData
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSlider, QPushButton, QHBoxLayout, QColorDialog
import pyqtgraph as pg
from pyqtgraph import mkColor, mkPen, PlotItem, PlotCurveItem

import colorsys


class SignalPlotWidget(QWidget):
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
        self.y_axis_grouped = False  # Y-axis grouping state

        # Layout principal
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        main_layout.addLayout(layout)

        # # Animation Controls
        #
        # self.init_animation_controls(main_layout)
        # Animation Controls (initially hidden)
        self.animation_controls = QWidget()
        self.animation_controls.setVisible(False)  # Start hidden
        self.init_animation_controls(self.animation_controls)
        main_layout.addWidget(self.animation_controls)

        # Widget de légende en dessous
        self.legend_widget = QWidget()
        self.legend_layout = QHBoxLayout(self.legend_widget)
        main_layout.addWidget(self.legend_widget)

        # Legend and plot setup
        # self.legend = self.plot_widget.addLegend(offset=(10, 10))
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

        if data_id in self.curves:
            print(f"Data {data_id} already displayed.")
            return

        # Récupération des informations de la donnée
        data_info = self.data_pool.get_data_info(data_id)
        data_object = data_info['data_object'].iloc[0]
        is_limit = False

        # Déterminer si la donnée est une limite
        if data_object.data_type in (Data_Type.TEMP_LIMIT, Data_Type.FREQ_LIMIT):
            is_limit = True

        # Initialisation des x_min et x_max pour le graphique selon le type de signal

        if data_object.data_type == Data_Type.TEMPORAL_SIGNAL:
            if self.x_min is None or self.x_max is None:
                self.x_min = data_object.tmin
                self.x_max = data_object.tmin + data_object.dt * data_object.num_samples
            else:
                self.x_min = min(self.x_min, data_object.tmin)
                self.x_max = max(self.x_max, data_object.tmin + data_object.dt * data_object.num_samples)
            # print(f'temp x_min: {self.x_min} - x_max: {self.x_max}')
        elif data_object.data_type == Data_Type.FREQ_SIGNAL:
            if self.x_min is None or self.x_max is None:
                self.x_min = data_object.fmin
                self.x_max = data_object.fmin + data_object.df * data_object.num_samples
            else:
                self.x_min = min(self.x_min, data_object.fmin)
                self.x_max = max(self.x_max, data_object.fmin + data_object.df * data_object.num_samples)
                # print(f'Freq x_min: {self.x_min} - x_max: {self.x_max}')
        elif data_object.data_type == Data_Type.FFTS:
            if self.x_min is None or self.x_max is None:
                # recuperer la premiere FFT des FFTS
                fft_data_object = data_object.fft_signals[0]
                self.x_min = fft_data_object.fmin
                self.x_max = fft_data_object.fmin + fft_data_object.df * fft_data_object.num_samples
            else:
                # recuperer la premiere FFT des FFTS
                fft_data_object = data_object.fft_signals[0]
                self.x_min = min(self.x_min, fft_data_object.fmin)
                self.x_max = max(self.x_max, fft_data_object.fmin + fft_data_object.df * fft_data_object.num_samples)
                # print(f'FFT x_min: {self.x_min} - x_max: {self.x_max}')
        elif data_object.data_type == Data_Type.FREQ_LIMIT:
            if self.x_min is None or self.x_max is None:
                self.x_min = data_object.freq_min
                self.x_max = data_object.freq_max
            else:
                self.x_min = min(self.x_min, data_object.freq_min)
                self.x_max = max(self.x_max, data_object.freq_max)
            # print(f'Freq limit x_min: {self.x_min} - x_max: {self.x_max}')
        elif data_object.data_type == Data_Type.TEMP_LIMIT:
            if self.x_min is None or self.x_max is None:
                # recupérer le xmin et xmax du plot
                self.x_min = self.plot_widget.plotItem.vb.viewRange()[0][0]
                self.x_max = self.plot_widget.plotItem.vb.viewRange()[0][1]
            # print(f'Temp limit x_min: {self.x_min} - x_max: {self.x_max}')

        if len(self.curves) == 0:
            #cacher les axes Y
            self.plot_widget.plotItem.hideAxis('left')
            self.plot_widget.plotItem.hideAxis('right')
        # Ajouter un axe Y supplémentaire à droite pour les courbes suivantes
        viewbox = pg.ViewBox()
        self.plot_widget.scene().addItem(viewbox)
        viewbox.setXLink(self.plot_widget.plotItem.vb)  # Lier l'axe X avec le ViewBox principal

        # Créer un nouvel axe Y à droite pour la courbe supplémentaire
        axis = pg.AxisItem('right')
        # axis.showLabel()
        self.plot_widget.plotItem.layout.addItem(axis, 2, 3 + len(self.extra_axes))  # Ajouter l'axe à droite
        axis.linkToView(viewbox)  # Lier l'axe Y au ViewBox
        axis.setLabel(data_object.data_name, color=color)
        self.plot_widget.plotItem.setXRange(self.x_min, self.x_max)

        # Ajouter la courbe au nouveau ViewBox
        curve = pg.PlotCurveItem(pen=pg.mkPen(color))
        # Check if this is FFT data
        if data_object.data_type == Data_Type.FFTS:
            print(f"FFT data detected: {data_object.data_name}")
            curve, axis = self.setup_fft_animation(data_object, color)
            axis.setLabel(data_object.data_name, color=color)
            axis.linkToView(viewbox)  # Lier l'axe Y au ViewBox
            axis = pg.AxisItem('right')
        viewbox.addItem(curve)

        # Stocker l'axe et le ViewBox pour les courbes supplémentaires
        self.extra_axes.append((axis, viewbox))

        # return # FFT data handled, no further processing
        # Ajouter la courbe à la liste des courbes tracées

        self.curves[data_id] = curve
        # self.legend.addItem(curve, name=data_object.data_name)

        self.plot_widget.setLimits(xMin=self.x_min, xMax=self.x_max)

        # Afficher les données du signal
        self.display_signal(data_id, curve)

        # Synchroniser les ViewBox avec le graphique principal
        self.update_viewbox_geometry()

        # Ajouter un élément de légende en dessous
        self.add_legend_item(data_id, data_object.data_name, color=color)

        # redefinir une couleur qui change en fonction du nombre de courbes pour toutes les courbes
        for i, dataid in enumerate(self.curves.keys()):
            print(f"Data id: {dataid}")

            # recuperer le type de la data
            datacurve = self.data_pool.get_data_info(dataid)['data_object'].iloc[0]
            data_type = datacurve.data_type
            print(f"Data type: {data_type}")
            #si la data est une limite, on met du rouge sinon on met couleur en fonction de l'index de la courbe
            if data_type == Data_Type.FREQ_LIMIT or datacurve.data_type == Data_Type.TEMP_LIMIT:
                print("Data is a limit")
                color: QColor = QColor('red')
            else:
                color: QColor = self.generate_color(i, len(self.curves))
            if color.isValid():
                # recuperer le label de la courbe
                print(f"Data name: {datacurve.data_name}")
                color_button: QColorDialog = None
                label: QLabel = None
                label , color_button = self.find_label_and_color_button_by_data_name(datacurve.data_name)

                print(f"Label: {label.text()}, Color button: {color_button}")
                # changer la couleur de la courbe
                self.change_curve_color(dataid, label, color_button, rgb_color=color)

    def display_signal(self, data_id, curve=None):
        """ Afficher les données pour un data_id spécifique """
        data_object = self.data_pool.get_data_info(data_id)['data_object'].iloc[0]

        if data_object.data_type == Data_Type.FFTS:
            self.curves[data_id] = self.fft_curve
            self.display_fft_frame(0)
            return
        elif data_object.data_type == Data_Type.FREQ_LIMIT:
            # Special handling for frequency limits
            x_data = np.linspace(self.x_min, self.x_max, self.max_points)
            y_data = [data_object.interpolate(freq) for freq in x_data]  # Interpolate limit level at each frequency

            # Use a dashed line or specific color for frequency limits
            if curve:
                curve.setData(x_data, y_data, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
            else:
                limit_curve = pg.PlotCurveItem(x_data, y_data, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
                self.curves[data_id] = limit_curve
                self.plot_widget.addItem(limit_curve)
            return
        elif data_object.data_type == Data_Type.TEMP_LIMIT:
            # Special handling for temporal limits
            x_data = np.linspace(self.x_min, self.x_max, self.max_points)
            level = [level for level, transparency_time, release_time in data_object.data][0]
            y_data = [level for t in x_data]  # Interpolate limit level at each frequency
            # print(f"x_data: {x_data} - y_data: {y_data}")
            if curve:
                curve.setData(x_data, y_data, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
            else:
                limit_curve = pg.PlotCurveItem(x_data, y_data, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
                self.curves[data_id] = limit_curve
                self.plot_widget.addItem(limit_curve)
            return

        data_x_min = data_object.tmin if data_object.data_type is Data_Type.TEMPORAL_SIGNAL else data_object.fmin
        data_x_max = data_x_min + data_object.dt * data_object.num_samples if data_object.data_type is Data_Type.TEMPORAL_SIGNAL else data_x_min + data_object.df * data_object.num_samples
        plot_x_min, plot_x_max = curve.getViewBox().viewRange()[0][0], curve.getViewBox().viewRange()[0][1]
        # Calculate chunk size based on the zoomed range to limit to `max_points`
        visible_range = plot_x_max - plot_x_min
        curve: PlotCurveItem
        print(
            f"Displaying data for {data_object.data_name}, type: {data_object.data_type},data_id: {data_id},data_object: {data_object}")

        num_samples = data_object.num_samples
        resolution = data_object.dt if data_object.data_type == Data_Type.TEMPORAL_SIGNAL else data_object.df

        # visible_range = self.x_max - self.x_min
        chunk_size = max(1, int(visible_range / resolution) // self.max_points)

        print(f"Visible range: {visible_range}, Chunk size: {chunk_size}, Max points: {self.max_points}")

        # Determine start and end chunk indices based on x_min and x_max
        start_index = max(0, int(self.x_min / resolution))
        end_index = min(num_samples, int(self.x_max / resolution))
        visible_samples = end_index - start_index

        # Adjust chunk size if visible_samples is less than max_points
        if visible_samples < self.max_points:
            chunk_size = 1

        # Prepare arrays to store simplified x and y values
        x_data, y_data_min, y_data_max = [], [], []

        # Loop through data in chunks and simplify each chunk
        for chunk_start in range(start_index, end_index, chunk_size):
            chunk = self.data_pool.get_data_chunk(data_id, chunk_start // chunk_size, chunk_size=chunk_size)

            if len(chunk) == 0:
                continue

            # Min and max values within the chunk for simplification
            min_value = np.min(chunk)
            max_value = np.max(chunk)

            # x_value for each chunk based on start index and resolution
            x_value = chunk_start * resolution
            x_data.append(x_value)
            y_data_min.append(min_value)
            y_data_max.append(max_value)

        # Combine min and max for line drawing
        x_data = np.repeat(x_data, 2)
        y_data = np.empty_like(x_data)
        y_data[0::2], y_data[1::2] = y_data_min, y_data_max

        # Update plot data
        if curve:
            curve.setData(x_data, y_data)
        else:
            self.curves[data_id].setData(x_data, y_data)

    def setup_fft_animation(self, fft_data, color):
        """Setup the plot and slider for FFT animation."""
        self.fft_data = fft_data  # Store FFT data for playback
        self.timestamp_slider.setMaximum(len(fft_data.fft_signals) - 1)
        self.timestamp_slider.setValue(0)
        self.current_frame = 0
        self.is_animating = False

        # Create a curve for FFT data
        self.fft_curve = self.plot_widget.plot(pen=pg.mkPen(color))
        # recuperer l'axe Y
        axis = self.plot_widget.getAxis('right')
        # self.fft_curve = pg.PlotCurveItem(pen=pg.mkPen(color))
        self.curves[fft_data.data_id] = self.fft_curve

        # afficher le player controler
        self.animation_controls.setVisible(True)

        # Display the first frame
        self.display_fft_frame(0)
        return self.fft_curve, axis

    def init_animation_controls(self, parent_widget):
        """ Initialize animation playback controls for FFT data. """
        control_layout = QHBoxLayout(parent_widget)

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

    def display_fft_frame(self, frame_index):
        """Display a single FFT frame (frequency domain data) by index."""
        fft_signal: FreqSignalData = self.fft_data.fft_signals[frame_index]
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

    def add_legend_item(self, data_id, name, color):
        """ Crée un élément de légende cliquable pour changer la couleur de la courbe. """
        label = QLabel(name)
        label.setStyleSheet(f"font-weight: bold;")

        # Bouton pour changer la couleur
        color_button = QPushButton("")
        color_button.setStyleSheet(f"background-color: {color};")
        color_button.clicked.connect(lambda: self.change_curve_color(data_id, label, color_button))

        # Ajouter au layout de la légende
        self.legend_layout.addWidget(label)
        self.legend_layout.addWidget(color_button)

    def handle_zoom(self, _, range):
        """Adjust display based on the zoom range, dynamically changing x_min and x_max."""
        x_min, x_max = range

        # Restrict x_min and x_max within the signal range
        # self.x_min = max(self.x_min, x_min)
        # self.x_max = min(self.x_max, x_max)

        # Update x_min and x_max for all curves
        self.x_min = x_min
        self.x_max = x_max

        # Trigger a full display refresh for all data curves
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

        if self.data_type == Data_Type.TEMPORAL_SIGNAL or self.data_type == Data_Type.TEMP_LIMIT:
            if new_data_type == Data_Type.TEMPORAL_SIGNAL or new_data_type == Data_Type.TEMP_LIMIT:
                return True
        elif self.data_type == Data_Type.FREQ_SIGNAL or self.data_type == Data_Type.FREQ_LIMIT:
            if new_data_type == Data_Type.FREQ_SIGNAL or new_data_type == Data_Type.FREQ_LIMIT:
                return True

        return False

    def toggle_y_axis_grouping(self):
        """
        Active ou désactive l'affichage d'un axe Y partagé, sans modifier les ViewBoxes.
        """
        if not self.y_axis_grouped:
            # Activer un axe Y unique pour toutes les courbes
            # Cacher tous les axes individuels
            for axis, viewbox in self.extra_axes:
                axis.hide()

            # Ajouter un seul axe Y partagé si non existant
            if not hasattr(self, 'shared_axis'):
                self.shared_axis = pg.AxisItem('right')
                self.shared_axis.setGrid(150)
                # Ajouter l'axe partagé à droite du layout
                self.plot_widget.plotItem.layout.addItem(self.shared_axis, 2, 3 + len(self.extra_axes))

            # Lier l'axe partagé au ViewBox principal
            self.shared_axis.linkToView(self.plot_widget.plotItem.vb)

            # Synchroniser tous les ViewBoxes avec le ViewBox principal
            for _, viewbox in self.extra_axes:
                viewbox.setYLink(self.plot_widget.plotItem.vb)

            # Afficher l'axe partagé
            self.shared_axis.show()
            self.y_axis_grouped = True

        else:
            # Désactiver l'axe Y unique et rétablir les axes individuels
            if hasattr(self, 'shared_axis'):
                # Cacher l'axe partagé au lieu de le supprimer
                self.shared_axis.hide()

            # Dissocier les liens Y de tous les ViewBoxes
            for _, viewbox in self.extra_axes:
                viewbox.setYLink(None)

            # Réafficher les axes individuels
            for i, (axis, viewbox) in enumerate(self.extra_axes):
                axis.show()
                axis.linkToView(viewbox)  # Relier chaque axe Y à son viewbox spécifique
                self.plot_widget.plotItem.layout.addItem(axis, 2, 3 + i)  # Réajouter chaque axe à droite dans le layout

            self.y_axis_grouped = False

    def find_label_and_color_button_by_data_name(self, data_name):
        """ Trouver l'élément de légende correspondant au nom de la donnée. """
        for i in range(0, self.legend_layout.count(), 2):
            label = self.legend_layout.itemAt(i).widget()
            print(label.text())
            if data_name in label.text():
                # Trouver le bouton de couleur correspondant
                color_button = self.legend_layout.itemAt(i + 1).widget()
                return label, color_button

    def change_curve_color(self, data_id, label, color_button=None, rgb_color=None):
        """ Permet de changer la couleur de la courbe en cliquant sur l'élément de légende. """
        color = None
        if rgb_color:
            color = QColor(rgb_color)
            print(f"Changing color to {color.name()}")
        elif color_button:
            color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            label.setStyleSheet(f"font-weight: bold;")
            color_button.setStyleSheet(f"background-color: {hex_color};")
            self.curves[data_id].setPen(pg.mkPen(hex_color))

    def generate_color(self, index, num_curves):
        """
        Génère une couleur unique en fonction de l'index et du nombre de courbes.
        Exclut le rouge en évitant les teintes proches de 0 ou 1.
        """
        # Ajuster l'index pour éviter les teintes proches de 0 ou 1
        hue = (index / num_curves) * 0.8 + 0.1  # Décalage pour éviter le rouge (autour de 0 ou 1)
        hue = hue % 1.0  # Assurer que la teinte est dans [0, 1]
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return QColor(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
