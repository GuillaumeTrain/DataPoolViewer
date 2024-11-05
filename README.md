
# DataPoolViewer

**DataPoolViewer** is a Python visualization tool that integrates with **PyDataCore** to visualize temporal, frequency, and FFT data from a central data pool. It offers a GUI for exploring, grouping, and plotting data, allowing users to inspect multiple data sources, add limits, and manage subscribers.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Example Code](#example-code)
- [Class Descriptions](#class-descriptions)
  - [DatapoolVisualizer](#datapoolvisualizer)
  - [DataPoolViewerWidget](#datapoolviewerwidget)
  - [PlotController](#plotcontroller)
  - [SignalPlotWidget](#signalplotwidget)
  - [DataPoolNotifier](#datapoolnotifier)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Data Management**: Display, organize, and manage data sources, data types, and subscribers.
- **Plotting**: Visualize temporal, frequency, and FFT data with customizable plots.
- **Dynamic Limit Visualization**: Add and display both temporal and frequency limits.
- **Interactivity**: Group and ungroup plots, synchronize axes, and change plot colors.
- **Live FFT Animation**: Display animated frequency-domain data in real-time.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/DataPoolViewer.git
    cd DataPoolViewer
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use **DataPoolViewer** in your application, follow the example below. It sets up a basic **QMainWindow** with a `DatapoolVisualizer` that displays and manages data from the **DataPool**.

### Example Code

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PyDataCore import DataPool, Data_Type
from scipy import signal
import numpy as np
from src.DatapoolVisualizer.datapool_visualizer import DatapoolVisualizer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datapool = DataPool()

        t = np.linspace(0, 1, 500)
        tstep = t[1] - t[0]

        square_signal = signal.square(2 * np.pi * 5 * t)
        temporal_data_id = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 5Hz", "source1", False,
                                                       False, time_step=tstep, unit="V")
        self.datapool.store_data(temporal_data_id, square_signal, "source1")

        self.visualizer = DatapoolVisualizer(self.datapool, parent=self)
        self.setCentralWidget(self.visualizer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## Class Descriptions

### DatapoolVisualizer
Main widget for visualizing data from the `DataPool`. Integrates `DataPoolViewerWidget` and `PlotController`.

#### Methods:
- `__init__(self, data_pool, parent=None)`: Initializes the visualizer with the specified data pool.
- `handle_data_selection(self, index)`: Handles data selection events and updates plots accordingly.

### DataPoolViewerWidget
Displays the `DataPool` structure in a tree view format.

#### Methods:
- `__init__(self, data_registry, source_to_data, subscriber_to_data, parent=None)`: Initializes the viewer widget.
- `populate_tree_view(self, data_registry, source_to_data, subscriber_to_data)`: Populates the tree view.

### PlotController
Manages multiple `SignalPlotWidget` instances and provides controls for grouping, ungrouping, and managing plots.

#### Methods:
- `add_plot(self)`: Adds a new plot.
- `remove_selected_plots(self)`: Removes selected plots.
- `add_data_to_selected_plot(self, data_id)`: Adds data to the selected plot.

### SignalPlotWidget
Handles the display of individual plots.

#### Methods:
- `add_data(self, data_id, color='b')`: Adds data to the plot.
- `display_signal(self, data_id, curve=None)`: Displays the data with simplified visualization.
- `handle_zoom(self, _, range)`: Adjusts the display based on zoom.

### DataPoolNotifier
A utility class that triggers signals on `DataPool` updates.

#### Methods:
- `attach_to_pool(self, pool)`: Attaches to a `DataPool` instance.

## Testing

Test scripts are located in the `tests` folder and include checks for core functionality.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
