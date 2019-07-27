from PySide2 import QtCore, QtGui, QtWidgets

from reader.data_version_handler import VersionContainer


class App(QtWidgets.QApplication):
	"""This is the main application that contains the file tree."""
	def __init__(self):
		QtWidgets.QApplication.__init__(self)

		self.mappings = VersionContainer(r'..\mappings')

		# set up main window
		self.main_window = QtWidgets.QMainWindow()
		self.main_window.setObjectName("MainWindow")
		self.main_window.resize(809, 698)

		self.central_widget = QtWidgets.QWidget(self.main_window)
		self.main_window.setCentralWidget(self.central_widget)

		self.horizontal_layout = QtWidgets.QHBoxLayout(self.central_widget)

		# convert from
		self.convert_from_layout = QtWidgets.QVBoxLayout()
		self.horizontal_layout.addLayout(self.convert_from_layout)

		self.convert_from_ver_select_layout = QtWidgets.QHBoxLayout()
		self.horizontal_layout.addLayout(self.convert_from_ver_select_layout)

		self.mapping_platforms = self.mappings.platforms

		self.input_platform = QtWidgets.QComboBox()
		self.input_platform.addItems(self.mapping_platforms)
		self.input_platform.setCurrentIndex(0)
		self.input_platform.currentIndexChanged.connect(self.input_platform_changed)
		self.convert_from_ver_select_layout.addWidget(self.input_platform)

		self.input_version = QtWidgets.QComboBox()
		self.input_versions = self.mappings.version_numbers(self.mapping_platforms[self.input_platform.currentIndex()])
		self.input_version.addItems([str(ver) for ver in self.input_versions])
		self.input_version.setCurrentIndex(0)
		self.input_version.currentIndexChanged.connect(self.input_version_changed)
		self.convert_from_ver_select_layout.addWidget(self.input_version)

		self.input_sub_version = QtWidgets.QComboBox()
		self.input_sub_versions = list(self.mappings.get(self.mapping_platforms[self.input_platform.currentIndex()], self.input_versions[self.input_version.currentIndex()])._subversions.keys()) # I need to add an actual API entry for this
		self.input_sub_version.addItems(self.input_sub_versions)
		self.input_sub_version.setCurrentIndex(0)
		self.input_sub_version.currentIndexChanged.connect(self.input_sub_version_changed)
		self.convert_from_ver_select_layout.addWidget(self.input_sub_version)


		# convert to
		self.convert_to_layout = QtWidgets.QHBoxLayout()
		self.horizontal_layout.addLayout(self.convert_to_layout)

		self.convert_to_ver_select_layout = QtWidgets.QHBoxLayout()
		self.horizontal_layout.addLayout(self.convert_to_ver_select_layout)

		self.output_platform = QtWidgets.QComboBox()
		self.output_platform.addItems(self.mapping_platforms)
		self.output_platform.setCurrentIndex(0)
		self.output_platform.currentIndexChanged.connect(self.output_platform_changed)
		self.convert_to_ver_select_layout.addWidget(self.output_platform)

		self.output_version = QtWidgets.QComboBox()
		self.output_versions = self.mappings.version_numbers(self.mapping_platforms[self.output_platform.currentIndex()])
		self.output_version.addItems([str(ver) for ver in self.output_versions])
		self.output_version.setCurrentIndex(0)
		self.output_version.currentIndexChanged.connect(self.output_version_changed)
		self.convert_to_ver_select_layout.addWidget(self.output_version)

		self.output_sub_version = QtWidgets.QComboBox()
		self.output_sub_versions = list(self.mappings.get(self.mapping_platforms[self.output_platform.currentIndex()], self.output_versions[self.output_version.currentIndex()])._subversions.keys()) # I need to add an actual API entry for this
		self.output_sub_version.addItems(self.output_sub_versions)
		self.output_sub_version.setCurrentIndex(0)
		self.output_sub_version.currentIndexChanged.connect(self.output_sub_version_changed())
		self.convert_to_ver_select_layout.addWidget(self.output_sub_version)

		self.main_window.show()
		self.exec_()

	def input_platform_changed(self):
		self.input_versions = self.mappings.version_numbers(self.mapping_platforms[self.input_platform.currentIndex()])
		self.input_version.clear()
		self.input_version.addItems([str(ver) for ver in self.input_versions])
		self.input_version.setCurrentIndex(0)
		self.input_version_changed()

	def input_version_changed(self):
		self.input_sub_versions = list(self.mappings.get(self.mapping_platforms[self.input_platform.currentIndex()], self.input_versions[self.input_version.currentIndex()])._subversions.keys())  # I need to add an actual API entry for this
		self.input_sub_version.clear()
		self.input_sub_version.addItems(self.input_sub_versions)
		self.input_sub_version.setCurrentIndex(0)
		self.input_sub_version_changed()

	def input_sub_version_changed(self):
		self.convert()

	def output_platform_changed(self):
		self.output_versions = self.mappings.version_numbers(self.mapping_platforms[self.output_platform.currentIndex()])
		self.output_version.clear()
		self.output_version.addItems([str(ver) for ver in self.output_versions])
		self.output_version.setCurrentIndex(0)
		self.output_version_changed()

	def output_version_changed(self):
		self.output_sub_versions = list(self.mappings.get(self.mapping_platforms[self.output_platform.currentIndex()], self.output_versions[self.output_version.currentIndex()])._subversions.keys())  # I need to add an actual API entry for this
		self.output_sub_version.clear()
		self.output_sub_version.addItems(self.output_sub_versions)
		self.output_sub_version.setCurrentIndex(0)
		self.output_sub_version_changed()

	def output_sub_version_changed(self):
		self.convert()

	def convert(self):
		pass


if __name__ == '__main__':
	App()
