from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyDataCore import DataPool, Data_Type
from dataviewer.datapool_viewer import DataPoolViewerWidget, DataPoolNotifier
import random


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Créer le DataPool
        self.pool = DataPool()

        # Créer le notifier et l'attacher au DataPool
        self.notifier = DataPoolNotifier()
        self.notifier.attach_to_pool(self.pool)

        # Initialisation du widget DataPoolViewer avec les vrais DataFrames de PyDataCore
        self.viewer_widget = DataPoolViewerWidget(self.pool.data_registry, self.pool.source_to_data, self.pool.subscriber_to_data)

        # Créer un QDockWidget pour rendre la vue détachable
        self.create_dockable_view()

        # Connecter le signal "data_changed" pour rafraîchir le TreeView
        self.notifier.data_changed.connect(self.refresh_view)

        # Simuler l'ajout initial de données au DataPool
        self.simulate_initial_data()

        # Démarrer la modification asynchrone
        self.start_async_modifications()

    def create_dockable_view(self):
        # Créer un QDockWidget pour rendre le DataPoolViewer détachable
        self.dock_widget = QDockWidget("DataPool Viewer", self)
        self.dock_widget.setWidget(self.viewer_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

    def refresh_view(self):
        # Rafraîchir le DataPoolViewer quand le DataPool est mis à jour
        self.viewer_widget.populate_tree_view(self.pool.data_registry, self.pool.source_to_data, self.pool.subscriber_to_data)

    def simulate_initial_data(self):
        # Simuler l'ajout initial de données dans le DataPool
        source_id_1 = "source1"
        source_id_2 = "source2"

        data_id_1 = self.pool.register_data(Data_Type.TEMPORAL_SIGNAL, "Temp Signal 1", source_id_1, time_step=0.01, unit="V")
        data_id_2 = self.pool.register_data(Data_Type.FREQ_SIGNAL, "Freq Signal 1", source_id_2, freq_step=1.0, unit="Hz")

        # Ajouter des abonnés
        self.pool.add_subscriber(data_id_1, "subscriber1")
        self.pool.add_subscriber(data_id_1, "subscriber2")
        self.pool.add_subscriber(data_id_2, "subscriber3")

        # Stocker des données réelles dans le DataPool
        signal_data = [0.1, 0.2, 0.3, 0.4, 0.5]  # Signal temporel exemple
        self.pool.store_data(data_id_1, signal_data, source_id_1)

        freq_data = [1.0, 1.1, 1.2, 1.3, 1.4]  # Signal fréquentiel exemple
        self.pool.store_data(data_id_2, freq_data, source_id_2)

    def start_async_modifications(self):
        # Démarrer une routine asynchrone pour modifier le DataPool à intervalles réguliers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.modify_data_pool)  # Appelle la méthode toutes les N millisecondes
        self.timer.start(2000)  # 2000ms = 2 secondes

    def modify_data_pool(self):
        # Modifications aléatoires dans le DataPool pour simuler des changements en temps réel

        # Choisir aléatoirement une modification à effectuer
        action = random.choice(['add_signal', 'update_signal', 'add_subscriber'])

        if action == 'add_signal':
            source_id = random.choice(['source1', 'source2'])
            data_id = self.pool.register_data(Data_Type.TEMPORAL_SIGNAL, f"New Temp Signal {random.randint(1, 100)}", source_id, time_step=0.01, unit="V")
            signal_data = [random.uniform(0.0, 1.0) for _ in range(5)]
            self.pool.store_data(data_id, signal_data, source_id)

        elif action == 'update_signal':
            # Prendre un signal existant et modifier ses données
            if not self.pool.data_registry.empty:
                data_row = self.pool.data_registry.sample(1).iloc[0]  # Sélectionner une donnée aléatoire
                data_id = data_row['data_id']
                new_data = [random.uniform(0.0, 1.0) for _ in range(5)]
                self.pool.store_data(data_id, new_data, random.choice(['source1', 'source2']))

        elif action == 'add_subscriber':
            # Ajouter un abonné à une donnée aléatoire
            if not self.pool.data_registry.empty:
                data_row = self.pool.data_registry.sample(1).iloc[0]  # Sélectionner une donnée aléatoire
                data_id = data_row['data_id']
                new_subscriber = f"subscriber{random.randint(4, 100)}"
                self.pool.add_subscriber(data_id, new_subscriber)

if __name__ == "__main__":
    app = QApplication([])

    # Créer la fenêtre principale
    window = MainWindow()
    window.show()

    app.exec()