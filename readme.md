# DataPoolViewer

**DataPoolViewer** est une bibliothèque Python permettant d'afficher et de manipuler visuellement les registres du `DataPool` (provenant de la bibliothèque PyDataCore) à l'aide d'une interface graphique basée sur **PySide6**.

Cette bibliothèque fournit une interface intuitive pour observer en temps réel les changements effectués dans un `DataPool`. Le `TreeView` est capable de visualiser les relations entre les sources de données, les données enregistrées et les abonnés. De plus, un mécanisme asynchrone permet de mettre à jour automatiquement les données sans que l'utilisateur n'ait besoin de recharger l'interface.

## Fonctionnalités

- **Visualisation en temps réel des registres du DataPool** : Les registres `data_registry`, `source_to_data`, et `subscriber_to_data` sont affichés sous forme d'arbre.
- **Fenêtre détachable (`QDockWidget`)** : Le `TreeView` peut être détaché de la fenêtre principale et déplacé.
- **Rafraîchissement automatique** : Le `TreeView` se met à jour en temps réel grâce à l'émission de signaux à chaque modification du `DataPool`.
- **Monkey Patching** : La classe `DataPoolNotifier` est utilisée pour injecter des signaux dans les méthodes du `DataPool` sans modifier la bibliothèque PyDataCore.

## Installation

1. Clonez le dépôt Git du projet :

   ```bash
   git clone https://github.com/<your-username>/DataPoolViewer.git

2. Installez les dépendances du projet :

   ```bash
   pip install -r requirements.txt
   
Dépendances principales :

PySide6 : Pour l'interface graphique.
PyDataCore : Bibliothèque gérant le DataPool.

3. Lancez l'exemple pour tester le projet :
 
   ```bash
   python examples/test_pool_viewer.py

## Utilisation
### Visualisation des registres de DataPool
Le fichier test_register.py montre comment créer une interface graphique qui permet de visualiser les registres du DataPool. Chaque changement dans le DataPool est automatiquement reflété dans l'interface.

### Mise à jour asynchrone des registres
Le fichier test_pool_viewer.py inclut une fonctionnalité asynchrone qui modifie le DataPool en temps réel à intervalles réguliers. Ces modifications sont visualisées dans le TreeView sans intervention manuelle.

### Exemple d'intégration
Voici un extrait de code de l'exemple test_register.py :
    
    ```bash
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyDataCore import DataPool, Data_Type
from dataviewer.widget import DataPoolViewerWidget, DataPoolNotifier
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Créer le DataPool
        self.pool = DataPool()

        # Créer le notifier et l'attacher au DataPool
        self.notifier = DataPoolNotifier()
        self.notifier.attach_to_pool(self.pool)

        # Initialisation du widget DataPoolViewer
        self.viewer_widget = DataPoolViewerWidget(self.pool.data_registry, self.pool.source_to_data, self.pool.subscriber_to_data)

        # Créer un QDockWidget pour rendre la vue détachable
        self.create_dockable_view()

        # Connecter le signal "data_changed" pour rafraîchir le TreeView
        self.notifier.data_changed.connect(self.refresh_view)

    def create_dockable_view(self):
        # Créer un QDockWidget pour rendre le DataPoolViewer détachable
        self.dock_widget = QDockWidget("DataPool Viewer", self)
        self.dock_widget.setWidget(self.viewer_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

    def refresh_view(self):
        # Effacer les éléments existants dans le TreeView avant de repeupler
        self.viewer_widget.model.clear()
        self.viewer_widget.populate_tree_view(self.pool.data_registry, self.pool.source_to_data, self.pool.subscriber_to_data)

## Structure du Projet
    
    
        DataPoolViewer/
        │
        ├── dataviewer/                     # Package principal pour la visualisation des registres
        │   ├── __init__.py
        │   ├── treeview.py                 # Contient la logique du QTreeView
        │   ├── widget.py                   # Contient le widget de visualisation du DataPool
        │   └── utils.py                    # (Optionnel) Fonctions utilitaires
        │
        ├── examples/                       # Exemples d'utilisation
        │   ├── test_register.py            # Exemple de base de visualisation
        │   └── test_pool_viewer.py         # Exemple avec mise à jour asynchrone
        │
        ├── tests/                          # Tests unitaires pour la bibliothèque
        │   └── test_widget.py
        │
        ├── LICENSE                         # Licence open source
        ├── README.md                       # Documentation de base du projet
        └── setup.py                        # Script d'installation pour le packaging

## Contribuer
Les contributions sont les bienvenues ! Si vous souhaitez apporter des améliorations ou ajouter des fonctionnalités, vous pouvez soumettre une pull request ou créer une issue.

## License
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.