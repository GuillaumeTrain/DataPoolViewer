from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyDataCore import Data_Type
from src.DatapoolVisualizer.plot_widget import SignalPlotWidget


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

        # bouton pour grouper/dégrouper les axes Y
        toggle_y_axes_button = QPushButton("Grouper/Dégrouper les axes Y")
        toggle_y_axes_button.clicked.connect(self.toggle_y_axis_grouping)
        control_layout.addWidget(toggle_y_axes_button)

    def toggle_y_axis_grouping(self):
        """
        Active ou désactive le regroupement des axes Y pour le plot sélectionné.
        """
        selected_plots: SignalPlotWidget = [plot for plot in self.plots if plot.selected]

        if selected_plots:
            for selected_plot in selected_plots:
                selected_plot.toggle_y_axis_grouping()
            print(f"Toggled Y-axis grouping for the selected plot. axes grouped: {selected_plot.y_axis_grouped}")
        else:
            print("No plot selected to toggle Y-axis grouping.")

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
        selected_plots = [plot for plot in self.plots if plot.selected]
        if len(selected_plots) > 1:
            self.groups.append(selected_plots)
            self.sync_x_axes(selected_plots)
            print(f"Grouped {len(selected_plots)} plots together.")

    def ungroup_selected_plots(self):
        """
        Dégroupe les plots sélectionnés s'ils font partie d'un groupe.
        """
        selected_plots = [plot for plot in self.plots if plot.selected]

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
        selected_plots = [plot for plot in self.plots if plot.selected]
        for plot in selected_plots:
            # Retirer du layout et de la liste des plots
            self.layout.removeWidget(plot)
            plot.deleteLater()  # Supprime le widget de manière propre
            self.plots.remove(plot)
            print(f"Plot {plot} removed.")

    def add_data_to_selected_plot(self, data_id):
        """
        Adds selected data to the currently selected plot, supporting FFT playback.
        """
        selected_plot = next((plot for plot in self.plots if plot.selected), None)

        if selected_plot:
            data_info = self.data_pool.get_data_info(data_id)
            data_object = data_info['data_object'].iloc[0]
            data_type = data_object.data_type
            selected_plot: SignalPlotWidget
            if data_type in [Data_Type.TEMPORAL_SIGNAL, Data_Type.FREQ_SIGNAL]:
                # Regular temporal or frequency data addition
                if selected_plot.is_compatible(data_id):
                    selected_plot.add_data(data_id, 'b')
                    print(f"Data {data_id} added to selected plot.")
                else:
                    print("Incompatible data for selected plot.")

            elif data_type in [Data_Type.FFTS, Data_Type.FREQ_LIMIT, Data_Type.TEMP_LIMIT]:
                # Trigger FFT playback setup if FFT data is selected
                # selected_plot.setup_fft_animation(data_object, 'b')
                selected_plot.add_data(data_id, 'b')
                print(f"FFT data {data_id} added with playback controls.")

            else:
                print(f"Data type {data_type} not supported for ploting.")
        else:
            print("No plot selected to add data to.")
