
# DataPoolViewer

**DataPoolViewer** est une bibliothèque Python permettant d'afficher, manipuler visuellement les registres du `DataPool` (provenant de la bibliothèque **PyDataCore**) et tracer des signaux en temps réel avec une interface graphique basée sur **PySide6** et **PyQtGraph**.

Cette bibliothèque fournit une interface intuitive pour observer en temps réel les changements effectués dans un `DataPool`. En plus de la visualisation des relations entre les sources de données et les abonnés, **DataPoolViewer** permet de tracer des signaux volumineux tout en optimisant les performances.

## Fonctionnalités

- **Visualisation en temps réel des registres du DataPool** : Les registres `data_registry`, `source_to_data`, et `subscriber_to_data` sont affichés sous forme d'arbre dans un `TreeView`.
- **Traçage de signaux volumineux avec simplification** : Visualisation de signaux temporels (`TEMPORAL_SIGNAL`) et fréquentiels (`FREQ_SIGNAL`), avec simplification du signal pour améliorer les performances lorsque le nombre de points est important.
- **Zoom dynamique** : Gestion du zoom sur les graphiques, avec ajustement des données affichées en fonction de la plage de zoom pour optimiser les performances.
- **Fenêtre détachable (`QDockWidget`)** : Les éléments de l'interface, tels que le `TreeView` et les graphiques, peuvent être détachés de la fenêtre principale et déplacés.
- **Rafraîchissement automatique** : Le `TreeView` se met à jour en temps réel grâce à l'émission de signaux à chaque modification du `DataPool`.
- **Monkey Patching** : La classe `DataPoolNotifier` est utilisée pour injecter des signaux dans les méthodes du `DataPool` sans modifier la bibliothèque PyDataCore.
- **Affichage des axes et unités** : Les graphiques affichent les axes avec des unités adaptées (temps, fréquence, amplitude).
- **Curseurs interactifs** (en développement) : Bientôt disponible pour interagir avec le signal tracé.

## Installation

1. Clonez le dépôt Git du projet :

   ```bash
   git clone https://github.com/<your-username>/DataPoolViewer.git
   ```

2. Installez les dépendances du projet :

   ```bash
   pip install -r requirements.txt
   ```

Dépendances principales :
- **PySide6** : Pour l'interface graphique.
- **PyDataCore** : Bibliothèque gérant le DataPool.
- **PyQtGraph** : Pour tracer les signaux.

3. Lancez l'exemple pour tester le projet :

   ```bash
   python examples/test_pool_viewer.py
   ```

## Utilisation

### Visualisation des registres de DataPool

Le fichier `test_register.py` montre comment créer une interface graphique qui permet de visualiser les registres du DataPool. Chaque changement dans le DataPool est automatiquement reflété dans l'interface.

### Traçage des signaux avec simplification

Le fichier `test_plot_widget.py` montre comment générer et tracer un signal de grande taille, tel qu'un signal carré avec un `duty cycle` de 99.9% et une fréquence d'échantillonnage élevée. Le graphique est capable de gérer efficacement des millions de points grâce à la simplification par min/max sur des chunks de données.

### Exemple d'intégration

Voici un extrait de code montrant comment visualiser un signal stocké dans un DataPool et le tracer dans une interface graphique :

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from dataviewer.plot_widget import SignalPlotWidget
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Paramètres pour le signal carré
        sampling_interval = 0.0001
        duration = 50  # Durée en secondes
        frequency = 1  # Fréquence en Hz
        duty_cycle = 0.999  # Duty cycle

        # Générer un signal carré
        t = np.arange(0, duration, sampling_interval)
        square_signal = signal.square(2 * np.pi * frequency * t, duty=duty_cycle)

        # Tracer le signal
        signal_plot_widget = SignalPlotWidget(square_signal, data_type='TEMPORAL_SIGNAL', dt=sampling_interval)

        # Afficher le widget
        dock_widget = QDockWidget("Square Signal", self)
        dock_widget.setWidget(signal_plot_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
```

### Structure du Projet

    DataPoolViewer/
    │
    ├── dataviewer/                     # Package principal pour la visualisation et traçage des données
    │   ├── __init__.py
    │   ├── treeview.py                 # Contient la logique du QTreeView pour visualiser le DataPool
    │   ├── widget.py                   # Contient le widget de visualisation des registres du DataPool
    │   └── plot_widget.py              # Contient le widget pour tracer des signaux temporels/fréquentiels
    │
    ├── examples/                       # Exemples d'utilisation
    │   ├── test_register.py            # Exemple de base de visualisation du DataPool
    │   └── test_pool_viewer.py         # Exemple avec mise à jour asynchrone du DataPool
    │
    ├── tests/                          # Tests unitaires pour la bibliothèque
    │   ├── test_plot_widget.py         # Test de traçage de signal
    │   └── test_widget.py              # Test du widget de visualisation du DataPool
    │
    ├── LICENSE                         # Licence open source
    ├── README.md                       # Documentation de base du projet
    └── setup.py                        # Script d'installation pour le packaging

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez apporter des améliorations ou ajouter des fonctionnalités, vous pouvez soumettre une pull request ou créer une issue.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.
