import numpy as np
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QPushButton, QVBoxLayout, QWidget
from PyDataCore import DataPool, Data_Type
from scipy import signal
from dataviewer.plotcontroler import PlotController  # Importez votre classe PlotController ici

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialiser le DataPool et y ajouter des signaux
        self.datapool = DataPool()

        # Paramètres pour un signal carré (temporel)
        sampling_interval = 0.001  # Intervalle d'échantillonnage (s)
        duration = 2  # Durée (s)
        frequency = 2  # Fréquence (Hz)

        # Calcul du nombre de points et génération du signal
        t = np.arange(0, duration, sampling_interval)
        square_signal = signal.square(2 * np.pi * frequency * t)

        # Enregistrement de ce signal temporel dans le DataPool
        temporal_data_id = self.datapool.register_data(
            Data_Type.TEMPORAL_SIGNAL, "square_signal", "source1", False, False,
            time_step=sampling_interval, unit="V"
        )
        self.datapool.store_data(temporal_data_id, square_signal, "source1")

        # Paramètres pour un signal fréquentiel (spectre FFT d'un signal)
        freq_step = 0.5  # Intervalle de fréquence (Hz)
        freq_values = np.linspace(0, 100, 200)  # Fréquences
        amplitude_spectrum = np.abs(np.fft.fft(square_signal))

        # Enregistrement de ce signal fréquentiel dans le DataPool
        freq_data_id = self.datapool.register_data(
            Data_Type.FREQ_SIGNAL, "fft_square_signal", "source2", False, False,
            freq_step=freq_step, unit="dB"
        )
        self.datapool.store_data(freq_data_id, amplitude_spectrum, "source2")

        # Création du PlotController
        self.plot_controller = PlotController(self.datapool, parent=self)

        # Création d'un QDockWidget pour rendre le PlotController détachable
        dock_widget = QDockWidget("Plot Controller", self)
        dock_widget.setWidget(self.plot_controller)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)



if __name__ == "__main__":
    app = QApplication([])

    # Créer la fenêtre principale
    window = MainWindow()
    window.show()

    app.exec()
