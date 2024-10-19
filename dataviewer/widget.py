from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import QObject, Signal


class DataPoolViewerWidget(QWidget):
    def __init__(self, data_registry, source_to_data, subscriber_to_data, parent=None):
        super().__init__(parent)

        # Création du layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Création du TreeView pour afficher les données du DataPool
        self.tree_view = QTreeView()
        self.layout.addWidget(self.tree_view)

        # Création du modèle pour le TreeView
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Source -> Data -> Subscribers'])

        # Appel à la méthode pour remplir le TreeView avec les registres
        self.populate_tree_view(data_registry, source_to_data, subscriber_to_data)

        # Associer le modèle au TreeView
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()

    def populate_tree_view(self, data_registry, source_to_data, subscriber_to_data):
        """
        Remplit le TreeView avec toutes les colonnes des registres.
        """
        for _, source_row in source_to_data.iterrows():
            source_id = source_row['source_id']
            locked = source_row['locked']
            protected = source_row['protected']
            source_item = QStandardItem(f"Source ID: {source_id} (Locked: {locked}, Protected: {protected})")

            # Trouver les données associées à cette source
            data_rows = data_registry[data_registry['data_id'].isin(
                source_to_data[source_to_data['source_id'] == source_id]['data_id'].values
            )]

            for _, data_row in data_rows.iterrows():
                data_name = data_row['data_name']
                data_id = data_row['data_id']
                storage_type = data_row['storage_type']
                data_item = QStandardItem(f"Data Name: {data_name} (ID: {data_id}, Storage: {storage_type})")

                # Ajouter les abonnés pour cette donnée
                subscriber_rows = subscriber_to_data[subscriber_to_data['data_id'] == data_id]
                for _, subscriber_row in subscriber_rows.iterrows():
                    subscriber_id = subscriber_row['subscriber_id']
                    acquitted = subscriber_row['acquitements']
                    acquitted_status = "✔" if acquitted else "✘"
                    subscriber_item = QStandardItem(f"Subscriber ID: {subscriber_id} - Ack: {acquitted_status}")
                    data_item.appendRow(subscriber_item)

                # Ajouter la donnée comme sous-élément de la source
                source_item.appendRow(data_item)

            # Ajouter la source à l'arborescence principale
            self.model.appendRow(source_item)


class DataPoolNotifier(QObject):
    data_changed = Signal()

    def __init__(self):
        super().__init__()

    def attach_to_pool(self, pool):
        """
        Injecte le comportement de signal dans les méthodes du DataPool.
        """
        original_register_data = pool.register_data
        original_store_data = pool.store_data
        original_add_subscriber = pool.add_subscriber

        def wrapped_register_data(*args, **kwargs):
            result = original_register_data(*args, **kwargs)
            self.data_changed.emit()
            return result

        def wrapped_store_data(*args, **kwargs):
            result = original_store_data(*args, **kwargs)
            self.data_changed.emit()
            return result

        def wrapped_add_subscriber(*args, **kwargs):
            result = original_add_subscriber(*args, **kwargs)
            self.data_changed.emit()
            return result

        # Redéfinir les méthodes du DataPool (monkey patching)
        pool.register_data = wrapped_register_data
        pool.store_data = wrapped_store_data
        pool.add_subscriber = wrapped_add_subscriber
