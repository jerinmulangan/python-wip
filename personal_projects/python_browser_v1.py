import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QPushButton,
    QVBoxLayout, QWidget, QTabWidget, QCompleter
)
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QStringListModel
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://www.google.com'))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)
        self.parent = parent  # Reference to main window for updating suggestions

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt6 Web Browser with Autocomplete and Tabs')

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)

        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        back_btn = QPushButton("<")
        back_btn.clicked.connect(self.go_back)
        self.toolbar.addWidget(back_btn)

        forward_btn = QPushButton(">")
        forward_btn.clicked.connect(self.go_forward)
        self.toolbar.addWidget(forward_btn)

        reload_btn = QPushButton("⟳")
        reload_btn.clicked.connect(self.reload_page)
        self.toolbar.addWidget(reload_btn)

        home_btn = QPushButton("⌂")
        home_btn.clicked.connect(self.go_home)
        self.toolbar.addWidget(home_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.urlbar)

        # --- Autocomplete Setup ---
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.urlbar.setCompleter(self.completer)

        self.urlbar.textChanged.connect(self.fetch_suggestions)

        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_suggestions)

        new_tab_btn = QPushButton('New Tab')
        new_tab_btn.clicked.connect(self.add_new_tab)
        self.toolbar.addWidget(new_tab_btn)

        self.add_new_tab()

    def add_new_tab(self, url=None):
        new_tab = BrowserTab()
        idx = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(idx)
        if url:
            new_tab.browser.setUrl(QUrl(url))
        new_tab.browser.urlChanged.connect(self.update_urlbar)

    def close_current_tab(self, index):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def navigate_to_url(self):
        url_text = self.urlbar.text()
        if not url_text.startswith(('http://', 'https://')):
            url_text = 'http://' + url_text
        current_tab = self.tabs.currentWidget()
        current_tab.browser.setUrl(QUrl(url_text))

    def update_urlbar(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            url = current_tab.browser.url().toString()
            self.urlbar.setText(url)

    def go_back(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.back()

    def go_forward(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.forward()

    def reload_page(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.reload()

    def go_home(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.browser.setUrl(QUrl('https://www.google.com'))

    # --- Autocomplete methods ---
    def fetch_suggestions(self, text):
        if text.strip() == "":
            return
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={text}"
        request = QNetworkRequest(QUrl(url))
        self.manager.get(request)

    def handle_suggestions(self, reply):
        if reply.error():
            return
        data = reply.readAll().data()
        suggestions = []
        try:
            result = json.loads(data.decode())
            if isinstance(result, list) and len(result) > 1:
                suggestions = result[1]
        except Exception as e:
            print("Failed to parse suggestions:", e)

        self.completer.setModel(QStringListModel(suggestions))

def main():
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())
    add = 9/2
    mult = 4 * 2
    print(add)
    print(mult)

if __name__ == '__main__':
    main()

