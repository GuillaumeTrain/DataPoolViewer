
# DataPoolViewer

DataPoolViewer is a Python library for visually displaying and manipulating DataPool registers 
(from the `PyDataCore` library) and plotting signals in real-time with a graphical interface based on PySide6 and PyQtGraph.

This library provides an intuitive interface to observe real-time changes in a DataPool. 
In addition to visualizing the relationships between data sources and subscribers, 
DataPoolViewer allows for the efficient plotting of large signals with optimized performance.

## Features

- **Real-time visualization of DataPool registers**: Display of `data_registry`, `source_to_data`, and `subscriber_to_data` registers in a tree view.
- **FFT Stream Animation**: Supports plotting FFT stream data, where frequency-domain signals are updated over time, creating an animated view.
- **Multi-signal display with multiple Y-axes**: Supports plotting multiple signals (temporal, frequency, and FFT streams) with independent Y-axes on the same plot.
- **Signal Simplification for Large Data**: Temporal (`TEMPORAL_SIGNAL`) and frequency (`FREQ_SIGNAL`) signals are simplified (min/max chunking) for performance when displaying large data.
- **Dynamic Zoom and Pan**: Manages zooming in on plots with automatic updates of displayed data based on zoom level to enhance performance.
- **Interactive Plot Control**: Includes controls for adding, grouping, ungrouping, and removing plots.
- **Modular Plot Management**: Detachable (QDockWidget) plot windows allow users to rearrange the interface as needed.
- **Automatic Register Refresh**: Tree view updates in real-time when changes occur in the DataPool, using signals.
- **Monkey Patching for Real-time Data Sync**: The `DataPoolNotifier` class injects signals into DataPool methods without modifying PyDataCore.
- **Interactive Player for FFT Streams**: Play, pause, and navigate through FFT stream data with a timeline and timestamped frequency data.

## Installation

Clone the Git repository:

```bash
git clone https://github.com/<your-username>/DataPoolViewer.git
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Main Dependencies:

- **PySide6**: For the graphical interface.
- **PyDataCore**: Core library managing DataPool functionality.
- **PyQtGraph**: For efficient signal plotting.

Run the example to test the project:

```bash
python examples/test_pool_viewer.py
```

## Usage

### Real-time DataPool Visualization

The `test_register.py` file demonstrates how to create a graphical interface for viewing DataPool registers. 
Each change in the DataPool is automatically reflected in the interface.

### Signal Plotting with Simplification

The `test_plot_widget.py` file demonstrates generating and plotting large signals, such as a high-sampling-rate square wave. 
The plot efficiently handles millions of points through min/max chunk simplification.

### FFT Stream Animation

To create an FFT stream animation, use the FFT data type (`FFTS`) with timestamped frequency-domain data. 
The player controls allow users to navigate the stream over time.

## Example Integration

Here is a code snippet showing how to visualize a stored signal in a DataPool and plot it in a graphical interface:

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from src.dataviewer.plot_widget import SignalPlotWidget
import numpy as np
from scipy import signal
from PyDataCore import DataPool, Data_Type
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Init the DataPool and register the square signal
        self.datapool = DataPool()

        # Square wave signal parameters
        sampling_interval = 0.0001
        duration = 50  # Duration in seconds
        frequency = 1  # Frequency in Hz
        duty_cycle = 0.999  # Duty cycle

        # Generate a square wave signal
        t = np.arange(0, duration, sampling_interval)
        # calculate the time step
        tstep = t[1] - t[0]
        square_signal = signal.square(2 * np.pi * frequency * t, duty=duty_cycle)

        # déclarer le signal carré dans le DataPool
        temporal_data_id = self.datapool.register_data(Data_Type.TEMPORAL_SIGNAL, "Square Signal 5Hz", "source1", False,
                                                       False, time_step=tstep, unit="V")
        # stocker le signal carré dans le DataPool
        self.datapool.store_data(temporal_data_id, square_signal, "source1")

        # Display the widget
        dock_widget = QDockWidget("Square Signal", self)
        signal_plot_widget = SignalPlotWidget(self.datapool, temporal_data_id)
        dock_widget.setWidget(signal_plot_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
```

## Project Structure

```plaintext
DataPoolViewer/
│
├── dataviewer/                    # Main package for data visualization and plotting
│   ├── __init__.py
│   ├── datapool_viewer.py         # Contains logic for QTreeView to visualize DataPool registers
│   ├── datapoolvisualizer.py      # Handles main DataPool viewing and control logic
│   ├── plot_widget.py             # Widget for plotting temporal, frequency, and FFT stream data
│   └── plotcontroler.py           # Manages plot interactions and controls (e.g., grouping, removal)
│
├── examples/                      # Usage examples
│   ├── test_pool_viewer.py        # Example demonstrating DataPool visualization with async updates
│   └── test_register.py           # Basic example of DataPool register visualization
│
├── tests/                         # Unit tests for the library
│   ├── test_plot_widget_ram_data.py  # Tests for RAM-based data plot
│   ├── test_plot_widget_file_data.py # Tests for file-based data plot
│   ├── test_plot_controler.py        # Tests for plot controller functionalities
│   └── testdatapoolvisualizer.py     # Tests for DataPoolVisualizer and FFT stream integration
│
├── LICENSE                        # Open-source license
├── README.md                      # Project documentation (this file)
└── setup.py                       # Installation script for packaging
```

## Contributing

Contributions are welcome! If you want to make improvements or add features, you can submit a pull request or create an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

