import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PyDataCore import DataPool, Data_Type
from scipy import signal
import numpy as np

from dataviewer.datapoolvisualizer import DatapoolVisualizer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialiser le DataPool et y ajouter des données
        self.datapool = DataPool()

        # Ajouter un signal temporel
        t = np.linspace(0, 1, 500)
        square_signal = signal.square(2 * np.pi * 5 * t)
        temporal_data_id = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal", "source1", False, False, time_step=0.002, unit="V")
        self.datapool.store_data(temporal_data_id, square_signal, "source1")

        # Ajouter un signal fréquentiel (FFT)
        freq_signal = np.abs(np.fft.fft(square_signal))
        freq_data_id = self.datapool.register_data(Data_Type.FREQ_SIGNAL, "FFT of Square Signal", "source2", False, False, freq_step=0.1, unit="dB")
        self.datapool.store_data(freq_data_id, freq_signal, "source2")

        # Créer et ajouter le DatapoolVisualizer
        self.visualizer = DatapoolVisualizer(self.datapool, parent=self)
        self.setCentralWidget(self.visualizer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
