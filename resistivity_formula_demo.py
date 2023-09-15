import sys
import vtk
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import numpy as np
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


def create_cylinder(radius, height):
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(radius)
    cylinder.SetHeight(height)
    cylinder.SetResolution(100)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cylinder.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor, cylinder


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.materials = {
            "Copper": 1.68e-8,
            "Aluminum": 2.82e-8,
            "Iron": 9.71e-8,
            "Silver": 1.59e-8,
            "Air": 1.3e16,
            "Glass": 1e12,  # Taking a mid-range value
            "Rubber": 1e13,
            "Porcelain": 1e12,
            "Silicon": 6.4e2,
            "Teflon (PTFE)": 1e14,  # Taking a mid-range value
            "PVC": 1e13,  # Taking a mid-range value
            "Paper (Dry)": 1e12,
            "Bakelite": 1e10,
            "Quartz": 7.5e17,
            "Clay (Dry)": 5e5,  # Taking an average between the provided range
            "Clay (Saturated)": 55,
            "Sand (Dry)": 5e5,  # Taking an average between the provided range
            "Sand (Saturated)": 300,  # Taking an average between the provided range
            "Topsoil (Dry)": 2.5e5,  # Taking an average between the provided range
            "Topsoil (Saturated)": 550,  # Taking an average between the provided range
            "Gravel and Rock": 1e6,  # Given the higher end of the resistivity
            "Loam (Dry)": 5e5,  # Taking an average between the provided range
            "Loam (Saturated)": 175,  # Taking an average between the provided range
            "Peat": 255,  # Taking an average between the provided range
        }

        # Frame to hold the VTK render window and Qt controls
        frame = QtWidgets.QFrame()
        vbox = QtWidgets.QVBoxLayout()

        # VTK setup
        self.vtk_widget = QVTKRenderWindowInteractor(frame)
        vbox.addWidget(self.vtk_widget)

        self.ren = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Add cylinder to the renderer
        self.cylinder, self.cylinder_source = create_cylinder(0.1, 1)
        self.ren.AddActor(self.cylinder)
        self.cylinder.RotateY(70)
        self.cylinder.RotateX(45)

        camera = self.ren.GetActiveCamera()
        r = 2  # Adjust this value as needed to zoom in/out
        angle_rad = np.radians(30)  # Convert angle to radians
        camera.SetPosition(0, r * np.sin(angle_rad), r * np.cos(angle_rad))
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(
            0, 0, 1
        )  # This makes sure the "top" of the view is along the Z-axis
        self.ren.ResetCamera()

        #self.resistance_label = QtWidgets.QLabel("Resistance: N/A")
        #vbox.addWidget(self.resistance_label)

        self.formula_display = QtWidgets.QLabel()
        vbox.addWidget(self.formula_display)

        # Add Qt controls under the VTK render window
        self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radius_slider.setMinimum(1)
        self.radius_slider.setMaximum(100)
        self.radius_slider.setValue(10)  # Initial value for radius = 0.1
        self.radius_slider.valueChanged.connect(self.update_cylinder)
        vbox.addWidget(QtWidgets.QLabel("Cylinder Radius:"))
        vbox.addWidget(self.radius_slider)

        # Length Slider
        self.length_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(10)  # Example minimum length: 0.1
        self.length_slider.setMaximum(200)  # Example maximum length: 2.0
        self.length_slider.setValue(100)  # Initial value for length = 1.0
        self.length_slider.valueChanged.connect(self.update_cylinder)
        vbox.addWidget(QtWidgets.QLabel("Cylinder Length:"))
        vbox.addWidget(self.length_slider)

        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(self.materials.keys())
        self.material_combo.currentIndexChanged.connect(self.update_resistance)
        vbox.addWidget(QtWidgets.QLabel("Material:"))
        vbox.addWidget(self.material_combo)

        self.update_resistance()
        frame.setLayout(vbox)
        self.setCentralWidget(frame)
        self.setWindowTitle("Cylinder Visualization")
        self.vtk_widget.GetRenderWindow().Render()

    def update_cylinder(self, value):
        radius = self.radius_slider.value() / 100.0
        length = self.length_slider.value() / 100.0

        self.cylinder_source.SetRadius(radius)
        self.cylinder_source.SetHeight(length)
        self.vtk_widget.GetRenderWindow().Render()
        self.update_resistance()

    def calculate_resistance(self):
        radius = self.radius_slider.value() / 100.0
        length = self.length_slider.value() / 100.0
        resistivity = self.materials[self.material_combo.currentText()]

        area = np.pi * radius**2
        resistance = resistivity * (length / area)

        return resistance

    def update_resistance(self):
        resistance = self.calculate_resistance()
        radius = self.radius_slider.value() / 100.0
        length = self.length_slider.value() / 100.0
        resistivity = self.materials[self.material_combo.currentText()]

        formula_html = f"""
        <html>
        <body>
        <p><b>Resistivity Formula:</b></p>
        <p>R = ρ × (L/A)</p>
        <p>Where,</p>
        <p>R = {resistance:.2e} ohms (Resistance)</p>
        <p>ρ = {resistivity:.2e} ohm·m (Resistivity of {self.material_combo.currentText()})</p>
        <p>L = {length:.2f} m (Length)</p>
        <p>A = π × {radius:.2f}² = {np.pi * radius**2:.2e} m² (Cross-sectional Area)</p>
        </body>
        </html>
        """

        self.formula_display.setText(formula_html)
        #self.resistance_label.setText(f"Resistance: {resistance:.2e} ohms")

    # def update_resistance(self):
    #    resistance = self.calculate_resistance()
    #   self.resistance_label.setText(f"Resistance: {resistance:.2e} ohms")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
