import numpy as np
from PySide6.QtGui import Qt
from scipy import signal
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from dataviewer.plot_widget import SignalPlotWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Paramètres pour le signal carré
        sampling_interval = 0.000001  # Intervalle d'échantillonnage de "sampling_interval" secondes
        duration = 10*6*60  # Durée de "duration" secondes
        frequency = 1  # Fréquence de "frequency" Hz
        duty_cycle = 0.999  # Duty cycle de "duty_cycle" %

        # Calcul du nombre de points
        t = np.arange(0, duration, sampling_interval)

        # Générer le signal carré
        square_signal = signal.square(2 * np.pi * frequency * t, duty=duty_cycle)

        # Créer le widget de tracé pour visualiser le signal carré

        signal_plot_widget = SignalPlotWidget(square_signal, data_type='TEMPORAL_SIGNAL', signal_name="Square Signal", dt=sampling_interval, color='r',unit='V')

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