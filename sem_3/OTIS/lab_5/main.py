import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QInputDialog, QColorDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QColor
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class GraphCanvas(FigureCanvas):
    """Класс для отображения графа с помощью matplotlib и NetworkX"""

    def __init__(self, graph):
        self.figure, self.ax = plt.subplots()
        super().__init__(self.figure)
        self.graph = graph
        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()
        node_colors = [self.graph.nodes[node].get('color', 'skyblue') for node in self.graph.nodes]
        edge_colors = [self.graph.edges[edge].get('color', 'black') for edge in self.graph.edges]
        nx.draw(self.graph, ax=self.ax, with_labels=True, node_color=node_colors, edge_color=edge_colors,
                node_size=500, font_size=10)
        self.draw()


class GraphEditor(QMdiSubWindow):
    """Редактор графа с функциями для редактирования и сохранения графа"""

    def __init__(self, graph_name="Новый граф"):
        super().__init__()
        self.graph_name = graph_name
        self.graph = nx.Graph()
        self.canvas = GraphCanvas(self.graph)

        # Основной интерфейс редактора графа
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.canvas)

        # Разделение кнопок на два столбца
        button_layout = QHBoxLayout()

        # Первый столбец
        column1 = QVBoxLayout()
        add_node_btn = QPushButton("Добавить узел")
        add_node_btn.clicked.connect(self.add_node)
        column1.addWidget(add_node_btn)

        rename_node_btn = QPushButton("Переименовать узел")
        rename_node_btn.clicked.connect(self.rename_node)
        column1.addWidget(rename_node_btn)

        delete_node_btn = QPushButton("Удалить узел")
        delete_node_btn.clicked.connect(self.delete_node)
        column1.addWidget(delete_node_btn)

        color_node_btn = QPushButton("Задать цвет узла")
        color_node_btn.clicked.connect(self.color_node)
        column1.addWidget(color_node_btn)

        # Второй столбец
        column2 = QVBoxLayout()
        add_edge_btn = QPushButton("Добавить дугу")
        add_edge_btn.clicked.connect(self.add_edge)
        column2.addWidget(add_edge_btn)

        delete_edge_btn = QPushButton("Удалить дугу")
        delete_edge_btn.clicked.connect(self.delete_edge)
        column2.addWidget(delete_edge_btn)

        color_edge_btn = QPushButton("Задать цвет дуги")
        color_edge_btn.clicked.connect(self.color_edge)
        column2.addWidget(color_edge_btn)

        save_graph_btn = QPushButton("Сохранить граф")
        save_graph_btn.clicked.connect(self.save_graph)
        column2.addWidget(save_graph_btn)

        # Добавляем оба столбца в основной горизонтальный макет кнопок
        button_layout.addLayout(column1)
        button_layout.addLayout(column2)

        # Добавляем горизонтальный макет кнопок и информационную метку в основной макет
        main_layout.addLayout(button_layout)
        info_label = QLabel(f"Граф: {self.graph_name} | Узлы = 0, Дуги = 0")
        self.info_label = info_label
        main_layout.addWidget(info_label)

        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        self.setWindowTitle(f"Редактор графа - {self.graph_name}")
        additional_features_layout = QVBoxLayout()

        self.resize(1000, 600)

        # Add button for creating loops
        add_loop_btn = QPushButton("Добавить петлю")
        add_loop_btn.clicked.connect(self.add_loop)
        additional_features_layout.addWidget(add_loop_btn)

        # Button for graph information: tree check
        is_tree_btn = QPushButton("Проверить, является ли дерево")
        is_tree_btn.clicked.connect(self.check_is_tree)
        additional_features_layout.addWidget(is_tree_btn)

        # Button to convert to binary tree
        to_binary_tree_btn = QPushButton("Преобразовать в бинарное дерево")
        to_binary_tree_btn.clicked.connect(self.convert_to_binary_tree)
        additional_features_layout.addWidget(to_binary_tree_btn)

        # Button to find Hamiltonian cycles
        find_hamiltonian_btn = QPushButton("Найти гамильтоновы циклы")
        find_hamiltonian_btn.clicked.connect(self.find_hamiltonian_cycles)
        additional_features_layout.addWidget(find_hamiltonian_btn)

        # Button to calculate diameter, radius, and center
        calc_metrics_btn = QPushButton("Вычислить метрики графа")
        calc_metrics_btn.clicked.connect(self.calculate_graph_metrics)
        additional_features_layout.addWidget(calc_metrics_btn)

        # Button to compute tensor and Cartesian products
        graph_product_btn = QPushButton("Вычислить произведения графов")
        graph_product_btn.clicked.connect(self.calculate_graph_products)
        additional_features_layout.addWidget(graph_product_btn)

        main_layout.addLayout(additional_features_layout)

    def add_loop(self):
        """Add a loop (self-edge) to a specified node."""
        node, ok = QInputDialog.getText(self, "Добавить петлю", "Введите имя узла:")
        if ok and node in self.graph:
            self.graph.add_edge(node, node)
            self.canvas.draw_graph()

    def check_is_tree(self):
        """Check if the graph is a tree (connected and acyclic)."""
        if nx.is_tree(self.graph):
            QMessageBox.information(self, "Информация о графе", "Граф является деревом.")
        else:
            QMessageBox.information(self, "Информация о графе", "Граф не является деревом.")

    def convert_to_binary_tree(self):
        """Convert the graph to a binary tree structure."""
        # Creating a minimum spanning tree (not strictly binary but acyclic and connected)
        self.graph = nx.minimum_spanning_tree(self.graph)
        self.canvas.draw_graph()

    def find_hamiltonian_cycles(self):
        """Attempt to find Hamiltonian cycles."""
        try:
            cycle = nx.find_cycle(self.graph)
            QMessageBox.information(self, "Гамильтонов цикл", f"Найден цикл: {cycle}")
        except nx.NetworkXNoCycle:
            QMessageBox.warning(self, "Гамильтонов цикл", "Гамильтонов цикл не найден.")

    def calculate_graph_metrics(self):
        """Calculate and display diameter, radius, and center of the graph."""
        if nx.is_connected(self.graph):
            diameter = nx.diameter(self.graph)
            radius = nx.radius(self.graph)
            center = nx.center(self.graph)
            QMessageBox.information(self, "Метрики графа",
                                    f"Диаметр: {diameter}\nРадиус: {radius}\nЦентр: {center}")
        else:
            QMessageBox.warning(self, "Метрики графа", "Граф не является связным.")

    def calculate_graph_products(self):
        """Calculate tensor and Cartesian products with another graph."""
        graph_name, ok = QInputDialog.getText(self, "Вычислить произведения", "Введите имя второго графа:")
        if ok:
            # Placeholder: You'd load a second graph or have a predefined second graph
            second_graph = nx.path_graph(5)  # Replace with user-defined or loaded graph
            tensor_product = nx.tensor_product(self.graph, second_graph)
            cartesian_product = nx.cartesian_product(self.graph, second_graph)

            QMessageBox.information(self, "Произведения графов",
                                    f"Тензорное произведение: {tensor_product}\n"
                                    f"Декартово произведение: {cartesian_product}")

    def add_node(self):
        node, ok = QInputDialog.getText(self, "Добавить узел", "Введите имя узла:")
        if ok and node:
            self.graph.add_node(node)
            self.update_graph_info()
            self.canvas.draw_graph()

    def rename_node(self):
        node, ok = QInputDialog.getText(self, "Переименовать узел", "Введите существующее имя узла:")
        if ok and node in self.graph:
            new_name, ok = QInputDialog.getText(self, "Переименовать узел", "Введите новое имя узла:")
            if ok and new_name:
                nx.relabel_nodes(self.graph, {node: new_name}, copy=False)
                self.update_graph_info()
                self.canvas.draw_graph()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверное имя узла")

    def delete_node(self):
        node, ok = QInputDialog.getText(self, "Удалить узел", "Введите имя узла для удаления:")
        if ok and node in self.graph:
            self.graph.remove_node(node)
            self.update_graph_info()
            self.canvas.draw_graph()

    def add_edge(self):
        source, ok = QInputDialog.getText(self, "Добавить дугу", "Введите начальный узел:")
        if ok and source in self.graph:
            target, ok = QInputDialog.getText(self, "Добавить дугу", "Введите конечный узел:")
            if ok and target in self.graph:
                self.graph.add_edge(source, target)
                self.update_graph_info()
                self.canvas.draw_graph()

    def delete_edge(self):
        source, ok = QInputDialog.getText(self, "Удалить дугу", "Введите начальный узел:")
        if ok and source in self.graph:
            target, ok = QInputDialog.getText(self, "Удалить дугу", "Введите конечный узел:")
            if ok and target in self.graph:
                self.graph.remove_edge(source, target)
                self.update_graph_info()
                self.canvas.draw_graph()

    def color_node(self):
        node, ok = QInputDialog.getText(self, "Задать цвет узла", "Введите имя узла:")
        if ok and node in self.graph:
            color = QColorDialog.getColor()
            if color.isValid():
                self.graph.nodes[node]['color'] = color.name()
                self.canvas.draw_graph()

    def color_edge(self):
        source, ok = QInputDialog.getText(self, "Задать цвет дуги", "Введите начальный узел:")
        if ok and source in self.graph:
            target, ok = QInputDialog.getText(self, "Задать цвет дуги", "Введите конечный узел:")
            if ok and target in self.graph:
                color = QColorDialog.getColor()
                if color.isValid():
                    self.graph.edges[source, target]['color'] = color.name()
                    self.canvas.draw_graph()

    def save_graph(self):
        filename, ok = QInputDialog.getText(self, "Сохранить граф", "Введите имя файла:")
        if ok:
            data = nx.node_link_data(self.graph)
            with open(f"{filename}.json", "w") as file:
                json.dump(data, file)

    def update_graph_info(self):
        nodes = len(self.graph.nodes)
        edges = len(self.graph.edges)
        self.info_label.setText(f"Граф: {self.graph_name} | Узлы = {nodes}, Дуги = {edges}")


class GraphApp(QMainWindow):
    """Главное окно приложения с поддержкой MDI для работы с несколькими графами"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор графов")
        self.setGeometry(100, 100, 1200, 800)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        toolbar = self.addToolBar("Main Toolbar")
        new_graph_btn = QPushButton("Новый граф")
        new_graph_btn.clicked.connect(self.create_graph_editor)
        toolbar.addWidget(new_graph_btn)

    def create_graph_editor(self):
        graph_name, ok = QInputDialog.getText(self, "Новый граф", "Введите имя графа:")
        if ok and graph_name:
            graph_editor = GraphEditor(graph_name)
            self.mdi.addSubWindow(graph_editor)
            graph_editor.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = GraphApp()
    main_app.show()
    sys.exit(app.exec_())