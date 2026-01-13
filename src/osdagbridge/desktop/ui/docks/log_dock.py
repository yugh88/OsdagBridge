"""
Log dock widget for Osdag GUI.
Displays log messages and status updates.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt, QDateTime, QEvent
from PySide6.QtGui import QCursor


class LogDock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.is_visible = True
        self.setObjectName("logs_dock")

        self._resizing = False
        self._resize_start_y = 0
        self._start_height = 0
        self._resize_margin = 6

        self.init_ui()
        self.adjust_size()

    # -------------------- EVENT FILTER --------------------
    def eventFilter(self, obj, event):
        if obj is self.log_window_title:
            if event.type() == QEvent.MouseMove:
                y = event.position().y()

                if y <= self._resize_margin and not self._resizing:
                    self.setCursor(Qt.SizeVerCursor)
                elif not self._resizing:
                    self.unsetCursor()

                if self._resizing:
                    delta = self._resize_start_y - event.globalPosition().y()
                    new_height = self._start_height + delta
                    
                    parent = self.parent()
                    if parent:
                        max_height = parent.height() - 20
                        new_height = max(0, min(max_height, new_height))
                        parent_height = parent.height()
                        self.setFixedHeight(new_height)
                        self.move(self.x(), parent_height - new_height)
                    return True

            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton and event.position().y() <= self._resize_margin:
                    self._resizing = True
                    self._resize_start_y = event.globalPosition().y()
                    self._start_height = self.height()
                    return True

            elif event.type() == QEvent.MouseButtonRelease:
                if self._resizing:
                    self._resizing = False
                    self.unsetCursor()
                    return True

        return super().eventFilter(obj, event)

    # -------------------- UI --------------------
    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Border frame (resize handle lives here)
        self.border_frame = QFrame(self)
        self.border_frame.setObjectName("logBorderFrame")
        self.border_frame.setStyleSheet("""
            QFrame#logBorderFrame {
                border: 1px solid #000000;
                background-color: white;
            }
        """)
        outer_layout.addWidget(self.border_frame)

        layout = QVBoxLayout(self.border_frame)
        layout.setContentsMargins(2, 2, 2, 0)
        layout.setSpacing(0)

        self.log_window_title = QLabel("Log Window")
        self.log_window_title.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.log_window_title)

        self.log_display = QTextEdit()
        self.log_display.setObjectName("textEdit")
        self.log_display.setReadOnly(True)
        self.log_display.setOverwriteMode(True)
        layout.addWidget(self.log_display)

        # Install resize event filter
        self.log_window_title.installEventFilter(self)
        self.log_window_title.setMouseTracking(True)


        self.append_log(
            f"[{QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}] Log initialized",
            "info"
        )

        self.show()

    # -------------------- LOG API --------------------
    def append_log(self, message, log_level="info"):
        if log_level == "error":
            color = "#FF0000"
        elif log_level == "success":
            color = "#008000"
        else:
            color = "#A6A6A6"

        formatted_message = f'<span style="color: {color};">{message}</span>'
        self.log_display.append(formatted_message)
        self.log_display.ensureCursorVisible()

    # -------------------- VISIBILITY --------------------
    def toggle_log_dock(self):
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.show()
            self.adjust_size()
            self.move(0, self.parent().height() - self.height())
        else:
            self.hide()

    # -------------------- SIZE --------------------
    def adjust_size(self):
        parent = self.parent()
        if not parent or parent.input_dock is None or parent.output_dock is None:
            return

        input_dock_width = parent.input_dock.width() if parent.input_dock.isVisible() else 0
        output_dock_width = parent.output_dock.width() if parent.output_dock.isVisible() else 0

        available_width = parent.width() - input_dock_width - output_dock_width

        self.setMinimumHeight(0)
        self.setFixedWidth(available_width)
