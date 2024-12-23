import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PyDataCore import DataPool, Data_Type
from scipy import signal
import numpy as np
from src.DatapoolVisualizer.datapool_visualizer import DatapoolVisualizer


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
        tstep2 = t2[1] - t2[0]
        # Générer un signal carré
        square_signal = signal.square(2 * np.pi * 5 * t)
        square_signal2 = signal.square(2 * np.pi * 10 * t2)
        # déclarer le signal carré dans le DataPool
        temporal_data_id = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 5Hz", "source1", False,
                                                       False, time_step=tstep, unit="V")
        #stocker le signal carré dans le DataPool
        self.datapool.store_data(temporal_data_id, square_signal, "source1")

        temporal_data_id2 = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 10Hz", "source1",
                                                        False, False, time_step=tstep2, unit="V")
        self.datapool.store_data(temporal_data_id2, square_signal2, "source1")

        #ajouter un troisième signal temporel
        t3 = np.linspace(0, 1, 500)
        #calculer le time step
        tstep3 = t3[1] - t3[0]
        square_signal3 = signal.square(2 * np.pi * 15 * t3)
        temporal_data_id3 = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 15Hz", "source1",
                                                        False,
                                                        False, time_step=tstep3, unit="V")
        self.datapool.store_data(temporal_data_id3, square_signal3, "source1")
        # Ajouter des données fréquentielles pour la FFT (20 exemples avec des timestamps)
        freq_signals = []
        freq_step = 0.5  # Intervalle de fréquence
        fmin = 0.0  # Fréquence minimum
        unit = "Hz"  # Unité de fréquence
        timestamp = 0.0  # Timestamp initial

        for i in range(20):
            freq_signal = np.abs(np.fft.fft(np.sin(2 * np.pi * (5 + i) * t)))  # Exemple de FFT
            freq_data_id = self.datapool.register_data(
                Data_Type.FREQ_SIGNAL, f"Freq Signal {i + 1}", "source1", False, False,
                freq_step=freq_step, fmin=fmin, unit=unit, timestamp=timestamp
            )
            self.datapool.store_data(freq_data_id, freq_signal, "source1")
            freq_signals.append(freq_data_id)
            timestamp += 0.1  # Incrémenter le timestamp pour chaque signal

        # Enregistrer la séquence de signaux fréquentiels en tant que FFTS
        fft_data_id = self.datapool.register_data(
            Data_Type.FFTS, "FFT Sequence", "source1", False, False,
            freq_step=freq_step, fmin=fmin, unit=unit
        )

        # Déverrouiller les données FFTS pour les lire
        self.datapool.unlock_data(fft_data_id)

        fft_data_obj = self.datapool.get_data_info(fft_data_id)['data_object'].iloc[0]

        # Ajouter chaque signal fréquentiel dans la séquence FFT
        for data_id in freq_signals:
            freq_data_obj = self.datapool.get_data_info(data_id)['data_object'].iloc[0]
            fft_data_obj.add_fft_signal(freq_data_obj)

        #ajouter une data limite en fréquence
        freq_limit = self.datapool.register_data(data_type=Data_Type.FREQ_LIMIT, data_name="Freq Limit",
                                                 source_id="source1", protected=False, in_file=False, unit="Hz")
        #unlock the data
        self.datapool.unlock_data(freq_limit)
        #ajouter un subscriber
        self.datapool.add_subscriber(freq_limit, "sub1")
        freq_limit_obj = self.datapool.get_data_object(freq_limit, "sub1")
        freq_limit_obj.add_limit_point(5, -20)
        freq_limit_obj.add_limit_point(10, -5)
        freq_limit_obj.add_limit_point(99, -5)
        freq_limit_obj.add_limit_point(100, 100)
        freq_limit_obj.add_limit_point(200, 100)
        freq_limit_obj.add_limit_point(201, -5)
        freq_limit_obj.add_limit_point(250, -10)
        freq_limit_obj.set_interpolation_type("linear")

        #interpoler la limite de fréquence pour chaque fréquence
        interpolated_levels = []
        for i in range(250):
            interpolated_levels.append(freq_limit_obj.interpolate(i))

        #ajouter une data limite en temps
        temp_limit = self.datapool.register_data(data_type=Data_Type.TEMP_LIMIT, data_name="Temp Limit",
                                                 source_id="source1", protected=False, in_file=False, unit="s")
        #unlock the data
        self.datapool.unlock_data(temp_limit)
        #ajouter un subscriber
        self.datapool.add_subscriber(temp_limit, "sub1")
        temp_limit_obj = self.datapool.get_data_object(temp_limit, "sub1")
        temp_limit_obj.add_limit_point(0.5, 1, 0)

        # Créer et ajouter le DatapoolVisualizer
        self.visualizer = DatapoolVisualizer(self.datapool, parent=self)
        self.setCentralWidget(self.visualizer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
