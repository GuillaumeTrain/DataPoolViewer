import numpy as np
from PyDataCore import DataPool, Data_Type
from PySide6.QtGui import Qt
from scipy import signal
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from dataviewer.plot_widget import SignalPlotWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Paramètres pour le signal carré
        sampling_interval = 0.000001  # Intervalle d'échantillonnage de "sampling_interval" secondes
        duration = 60  # Durée de "duration" secondes
        frequency = 1  # Fréquence de "frequency" Hz
        duty_cycle = 0.999  # Duty cycle de "duty_cycle" %

        # Calcul du nombre de points
        t = np.arange(0, duration, sampling_interval)

        # Générer le signal carré
        square_signal = signal.square(2 * np.pi * frequency * t, duty=duty_cycle)

        # Créer le widget de tracé pour visualiser le signal carré
        datapool = DataPool()
        data_id = datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "square_signal", "source", False, True,
                                         time_step=sampling_interval, unit="V")
        datapool.store_data(data_id, square_signal, "source", "./")
        signal_plot_widget = SignalPlotWidget(datapool, data_id, signal_name="Square Signal", color='r', parent=self)

        # Créer un QDockWidget pour rendre le plot détachable
        self.create_dockable_view(signal_plot_widget)

    def create_dockable_view(self, signal_plot_widget):
        # Créer un QDockWidget pour rendre le plot détachable
        dock_widget = QDockWidget("Square Signal Plot", self)
        dock_widget.setWidget(signal_plot_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)


if __name__ == "__main__":
    app = QApplication([])

    # Créer la fenêtre principale
    window = MainWindow()
    window.show()

    app.exec()
