import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
import sqlite3

# 신규로 작성된 데이터베이스 파일명
DB_NAME = "stock_management.db"

# CSS 스타일시트 로드
with open("css_control.qss", "r", encoding="utf-8") as stylesheet:
    STYLE_SHEET = stylesheet.read()

# 데이터베이스 연결 및 테이블 생성


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # '국가', '증권사', '계좌번호', '종목명', '틱커명' 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 국가 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 증권사 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 계좌번호 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 종목명 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 틱커명 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE
    )
    ''')

    conn.commit()
    conn.close()

# 항목 관리 시스템 GUI 클래스


class ItemManagementSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_item_id = None  # 선택된 항목의 ID 저장
        self.init_ui()

    # GUI 초기화
    def init_ui(self):
        self.setWindowTitle('항목 관리 시스템')
        self.setGeometry(100, 100, 600, 400)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 항목 선택 콤보박스
        combo_layout = QHBoxLayout()
        self.combo_label = QLabel('항목 선택:')
        combo_layout.addWidget(self.combo_label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['국가', '증권사', '계좌번호', '종목명', '틱커명'])
        self.combo_box.currentTextChanged.connect(self.load_data)
        combo_layout.addWidget(self.combo_box)

        main_layout.addLayout(combo_layout)

        # 입력 폼 레이아웃
        form_layout = QHBoxLayout()

        self.label = QLabel('항목명:')
        form_layout.addWidget(self.label)

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.add_item)  # 엔터 키로 추가 기능
        self.input_field.textChanged.connect(self.to_uppercase)  # 입력 시 대문자로 변환
        form_layout.addWidget(self.input_field)

        self.add_button = QPushButton('추가')
        self.add_button.clicked.connect(self.add_item)
        form_layout.addWidget(self.add_button)

        self.update_button = QPushButton('수정')
        self.update_button.clicked.connect(self.update_item)
        form_layout.addWidget(self.update_button)
        self.update_button.setEnabled(False)  # 항목 선택 후에만 수정 버튼 활성화

        main_layout.addLayout(form_layout)

        # 테이블 설정
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['ID', '항목명'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 테이블 셀 수정 금지
        self.table.cellClicked.connect(self.table_item_clicked)
        main_layout.addWidget(self.table)

        # 삭제 버튼
        self.delete_button = QPushButton('삭제')
        self.delete_button.clicked.connect(self.delete_item)
        main_layout.addWidget(self.delete_button)

        # CSS 스타일 적용
        self.setStyleSheet(STYLE_SHEET)

        # 초기 데이터 로드
        self.load_data()

    # 입력 필드를 대문자로 변환하는 함수
    def to_uppercase(self):
        self.input_field.setText(self.input_field.text().upper())

    # 데이터 로드하여 테이블에 표시
    def load_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        selected_item = self.combo_box.currentText()

        query = f'SELECT * FROM {selected_item}'
        cursor.execute(query)
        rows = cursor.fetchall()

        self.table.setRowCount(0)  # 테이블 초기화

        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_position, 1, QTableWidgetItem(row[1]))

        conn.close()

    # 항목 추가 기능
    def add_item(self):
        item_name = self.input_field.text().strip()

        if item_name == "":
            QMessageBox.warning(self, "입력 오류", "항목명을 입력하세요.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        selected_item = self.combo_box.currentText()

        column_name = "name" if selected_item in [
            '국가', '증권사', '종목명'] else "number" if selected_item == '계좌번호' else "ticker"

        try:
            cursor.execute(f'INSERT INTO {selected_item} ({
                           column_name}) VALUES (?)', (item_name,))
            conn.commit()
            self.load_data()
            self.input_field.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "중복 오류", "이미 존재하는 항목입니다.")
        finally:
            conn.close()

    # 항목 수정 기능
    def update_item(self):
        if self.selected_item_id is None:
            QMessageBox.warning(self, "선택 오류", "수정할 항목을 선택하세요.")
            return

        updated_name = self.input_field.text().strip()

        if updated_name == "":
            QMessageBox.warning(self, "입력 오류", "수정할 항목명을 입력하세요.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        selected_item = self.combo_box.currentText()

        column_name = "name" if selected_item in [
            '국가', '증권사', '종목명'] else "number" if selected_item == '계좌번호' else "ticker"

        try:
            cursor.execute(f'UPDATE {selected_item} SET {
                           column_name} = ? WHERE id = ?', (updated_name, self.selected_item_id))
            conn.commit()
            self.load_data()
            self.input_field.clear()
            self.selected_item_id = None
            self.update_button.setEnabled(False)  # 수정 완료 후 수정 버튼 비활성화
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "중복 오류", "이미 존재하는 항목명입니다.")
        finally:
            conn.close()

    # 테이블 항목 클릭 시 항목명 입력박스로 올리기
    def table_item_clicked(self, row, column):
        self.selected_item_id = int(self.table.item(row, 0).text())
        selected_name = self.table.item(row, 1).text()
        self.input_field.setText(selected_name)
        self.update_button.setEnabled(True)  # 항목 선택 후 수정 버튼 활성화

    # 항목 삭제 기능
    def delete_item(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "선택 오류", "삭제할 항목을 선택하세요.")
            return

        item_id = int(self.table.item(selected_row, 0).text())

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        selected_item = self.combo_box.currentText()

        cursor.execute(f'DELETE FROM {selected_item} WHERE id = ?', (item_id,))
        conn.commit()

        self.load_data()
        conn.close()


if __name__ == '__main__':
    # 데이터베이스 테이블 생성
    create_table()

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = ItemManagementSystem()
    window.show()
    sys.exit(app.exec_())
