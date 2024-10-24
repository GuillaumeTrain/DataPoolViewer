import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyDataCore import Data_Type

from dataviewer.plot_widget import SignalPlotWidget


# class PlotController(QWidget):
#     def __init__(self, data_pool, parent=None):
#         super().__init__(parent)
#         self.data_pool = data_pool
#         self.plots = []  # Liste des objets SignalPlotWidget
#         self.groups = []  # Liste des groupes de plots
#         self.selected_plot = None  # Le plot actuellement sélectionné
#
#         # Layout pour organiser les plots et les contrôles
#         self.layout = QVBoxLayout()
#         self.setLayout(self.layout)
#
#         # Zone pour les boutons de contrôle
#         control_layout = QHBoxLayout()
#         self.layout.addLayout(control_layout)
#
#         # Boutons de contrôle
#         add_plot_button = QPushButton("Add Plot")
#         add_plot_button.clicked.connect(self.add_plot)
#         control_layout.addWidget(add_plot_button)
#
#         group_plots_button = QPushButton("Group Selected Plots")
#         group_plots_button.clicked.connect(self.group_selected_plots)
#         control_layout.addWidget(group_plots_button)
#
#         ungroup_plots_button = QPushButton("Ungroup Selected Plots")
#         ungroup_plots_button.clicked.connect(self.ungroup_selected_plots)
#         control_layout.addWidget(ungroup_plots_button)
#
#         remove_plots_button = QPushButton("Remove Selected Plots")
#         remove_plots_button.clicked.connect(self.remove_selected_plots)
#         control_layout.addWidget(remove_plots_button)
#
#     def add_plot(self):
#         """
#         Ajoute un nouveau plot dans la fenêtre.
#         """
#         plot = SignalPlotWidget(self.data_pool)
#         self.plots.append(plot)
#
#         # Ajouter le nouveau plot au layout
#         self.layout.addWidget(plot)
#
#     def group_selected_plots(self):
#         """
#         Groupe les plots sélectionnés ensemble pour synchroniser leur axe des abscisses.
#         """
#         selected_plots = [plot for plot in self.plots if plot.is_selected()]
#         if len(selected_plots) > 1:
#             self.groups.append(selected_plots)
#             self.sync_x_axes(selected_plots)
#             print(f"Grouped {len(selected_plots)} plots together.")
#
#     def ungroup_selected_plots(self):
#         """
#         Dégroupe les plots sélectionnés s'ils font partie d'un groupe.
#         """
#         selected_plots = [plot for plot in self.plots if plot.is_selected()]
#
#         # Pour chaque plot sélectionné, on vérifie s'il est dans un groupe
#         for plot in selected_plots:
#             for group in self.groups:
#                 if plot in group:
#                     # Désynchroniser tous les plots du groupe
#                     for p in group:
#                         p.plot_widget.setXLink(None)
#                     # Retirer le plot du groupe
#                     group.remove(plot)
#                     print(f"Plot {plot} ungrouped.")
#
#                     # Si le groupe devient vide ou contient moins de 2 éléments, supprimer le groupe
#                     if len(group) <= 1:
#                         self.groups.remove(group)
#                         print("Group removed due to insufficient plots.")
#
#     def sync_x_axes(self, plots):
#         """
#         Synchronise les axes des abscisses pour tous les plots du groupe.
#         """
#         first_plot = plots[0].plot_widget.getViewBox()
#         for plot in plots[1:]:
#             plot.plot_widget.setXLink(first_plot)
#
#     def remove_selected_plots(self):
#         """
#         Supprime les plots sélectionnés de la fenêtre et les retire de la liste des plots.
#         """
#         selected_plots = [plot for plot in self.plots if plot.is_selected()]
#         for plot in selected_plots:
#             # Retirer du layout et de la liste des plots
#             self.layout.removeWidget(plot)
#             plot.deleteLater()  # Supprime le widget de manière propre
#             self.plots.remove(plot)
#             print(f"Plot {plot} removed.")

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyDataCore import Data_Type
from dataviewer.plot_widget import SignalPlotWidget


class PlotController(QWidget):
    def __init__(self, data_pool, parent=None):
        super().__init__(parent)
        self.data_pool = data_pool
        self.plots = []  # Liste des objets SignalPlotWidget
        self.groups = []  # Liste des groupes de plots
        self.selected_plot = None  # Le plot actuellement sélectionné

        # Layout pour organiser les plots et les contrôles
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Zone pour les boutons de contrôle
        control_layout = QHBoxLayout()
        self.layout.addLayout(control_layout)

        # Boutons de contrôle
        add_plot_button = QPushButton("Add Plot")
        add_plot_button.clicked.connect(self.add_plot)
        control_layout.addWidget(add_plot_button)

        group_plots_button = QPushButton("Group Selected Plots")
        group_plots_button.clicked.connect(self.group_selected_plots)
        control_layout.addWidget(group_plots_button)

        ungroup_plots_button = QPushButton("Ungroup Selected Plots")
        ungroup_plots_button.clicked.connect(self.ungroup_selected_plots)
        control_layout.addWidget(ungroup_plots_button)

        remove_plots_button = QPushButton("Remove Selected Plots")
        remove_plots_button.clicked.connect(self.remove_selected_plots)
        control_layout.addWidget(remove_plots_button)

    def add_plot(self):
        """
        Ajoute un nouveau plot dans la fenêtre.
        """
        plot = SignalPlotWidget(self.data_pool)
        self.plots.append(plot)

        # Ajouter le nouveau plot au layout
        self.layout.addWidget(plot)

        # Connecter le clic sur le plot pour le sélectionner
        plot.mouseClickEvent = lambda ev: self.select_plot(plot)

    def select_plot(self, plot):
        """
        Sélectionne un plot. Une fois sélectionné, un clic sur une donnée pourra l'afficher dans ce plot.
        """
        self.selected_plot = plot
        print(f"Plot selected: {plot}")

    def group_selected_plots(self):
        """
        Groupe les plots sélectionnés ensemble pour synchroniser leur axe des abscisses.
        """
        selected_plots = [plot for plot in self.plots if plot.is_selected()]
        if len(selected_plots) > 1:
            self.groups.append(selected_plots)
            self.sync_x_axes(selected_plots)
            print(f"Grouped {len(selected_plots)} plots together.")

    def ungroup_selected_plots(self):
        """
        Dégroupe les plots sélectionnés s'ils font partie d'un groupe.
        """
        selected_plots = [plot for plot in self.plots if plot.is_selected()]

        # Pour chaque plot sélectionné, on vérifie s'il est dans un groupe
        for plot in selected_plots:
            for group in self.groups:
                if plot in group:
                    # Désynchroniser tous les plots du groupe
                    for p in group:
                        p.plot_widget.setXLink(None)
                    # Retirer le plot du groupe
                    group.remove(plot)
                    print(f"Plot {plot} ungrouped.")

                    # Si le groupe devient vide ou contient moins de 2 éléments, supprimer le groupe
                    if len(group) <= 1:
                        self.groups.remove(group)
                        print("Group removed due to insufficient plots.")

    def sync_x_axes(self, plots):
        """
        Synchronise les axes des abscisses pour tous les plots du groupe.
        """
        first_plot = plots[0].plot_widget.getViewBox()
        for plot in plots[1:]:
            plot.plot_widget.setXLink(first_plot)

    def remove_selected_plots(self):
        """
        Supprime les plots sélectionnés de la fenêtre et les retire de la liste des plots.
        """
        selected_plots = [plot for plot in self.plots if plot.is_selected()]
        for plot in selected_plots:
            # Retirer du layout et de la liste des plots
            self.layout.removeWidget(plot)
            plot.deleteLater()  # Supprime le widget de manière propre
            self.plots.remove(plot)
            print(f"Plot {plot} removed.")

    def add_data_to_selected_plot(self, data_id):
        """
        Ajoute une donnée sélectionnée au plot actuellement sélectionné.
        Vérifie la compatibilité du domaine des abscisses.
        """
        # Chercher le plot sélectionné
        selected_plot = next((plot for plot in self.plots if plot.is_selected()), None)

        if selected_plot:
            # Vérification de compatibilité avec les données déjà présentes
            if not selected_plot.is_compatible(data_id):
                print(f"Incompatible data for the selected plot.")
                return

            # Ajouter la donnée au plot
            selected_plot.display_data(data_id)
            print(f"Data {data_id} added to the selected plot.")
        else:
            print("No plot selected to add data to.")


