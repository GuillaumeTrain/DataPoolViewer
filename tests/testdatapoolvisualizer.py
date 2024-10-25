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
        #calculer le time step
        tstep = t[1] - t[0]
        t2 = np.linspace(0, 2, 750)
        #calculer le time step
        tstep2 = t2[1] - t2[0]
        square_signal = signal.square(2 * np.pi * 5 * t)

        square_signal2 = signal.square(2 * np.pi * 10 * t2)
        temporal_data_id = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 5Hz", "source1", False, False, time_step=tstep, unit="V")
        self.datapool.store_data(temporal_data_id, square_signal, "source1")
        temporal_data_id2 = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 10Hz", "source1", False,
                                                       False, time_step=tstep2, unit="V")
        self.datapool.store_data(temporal_data_id2, square_signal2, "source1")

        #ajouter un troisième signal temporel
        t3 = np.linspace(0, 1, 500)
        #calculer le time step
        tstep3 = t3[1] - t3[0]
        square_signal3 = signal.square(2 * np.pi * 15 * t3)
        temporal_data_id3 = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 15Hz", "source1", False,
                                                       False, time_step=tstep3, unit="V")
        self.datapool.store_data(temporal_data_id3, square_signal3, "source1")


        # Créer et ajouter le DatapoolVisualizer
        self.visualizer = DatapoolVisualizer(self.datapool, parent=self)
        self.setCentralWidget(self.visualizer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
