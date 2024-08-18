import sys
import os
import json
import yfinance as yf
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QGridLayout, QHeaderView
from PyQt5.QtCore import Qt

# 현재 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))

# QSS 파일 경로
qss_path = os.path.join(current_dir, "style.qss")

# JSON 파일 경로
json_path = os.path.join(current_dir, "stock_data.json")


class StockApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 윈도우 설정
        self.setWindowTitle('한국주식 현재주가')
        self.setGeometry(100, 100, 800, 800)

        # 창을 중앙에 위치시키기
        self.center()

    def center(self):
        """윈도우를 화면 중앙에 위치시키는 함수"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # 입력폼 타이틀 설정
        title_label = QLabel('한국주식 현재주가', self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")

        # 그리드 레이아웃 설정 (필드명과 입력 필드를 함께 배치)
        grid_layout = QGridLayout()

        # 틱커명 필드
        ticker_label = QLabel('틱커명:', self)
        self.ticker_input = QLineEdit(self)
        self.ticker_input.setPlaceholderText("6자리 숫자 입력")
        self.ticker_input.textChanged.connect(self.load_stock_data)

        grid_layout.addWidget(ticker_label, 0, 0)
        grid_layout.addWidget(self.ticker_input, 0, 1)

        # 종목명 필드
        name_label = QLabel('종목명:', self)
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("종목명")

        grid_layout.addWidget(name_label, 1, 0)
        grid_layout.addWidget(self.name_input, 1, 1)

        # 1년전가격 필드
        price_1yr_label = QLabel('1년전가격:', self)
        self.price_1yr_input = QLineEdit(self)
        self.price_1yr_input.setPlaceholderText("1년전가격")

        grid_layout.addWidget(price_1yr_label, 2, 0)
        grid_layout.addWidget(self.price_1yr_input, 2, 1)

        # 6개월전가격 필드
        price_6mo_label = QLabel('6개월전가격:', self)
        self.price_6mo_input = QLineEdit(self)
        self.price_6mo_input.setPlaceholderText("6개월전가격")

        grid_layout.addWidget(price_6mo_label, 3, 0)
        grid_layout.addWidget(self.price_6mo_input, 3, 1)

        # 현재가격 필드
        current_price_label = QLabel('현재가격:', self)
        self.current_price_input = QLineEdit(self)
        self.current_price_input.setPlaceholderText("현재가격")

        grid_layout.addWidget(current_price_label, 4, 0)
        grid_layout.addWidget(self.current_price_input, 4, 1)

        # 버튼 생성
        add_button = QPushButton('추가', self)
        update_button = QPushButton('수정', self)
        delete_button = QPushButton('삭제', self)
        reset_button = QPushButton('초기화', self)

        # 테이블 생성
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["틱커명", "종목명", "1년전가격", "6개월전가격", "현재가격"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.load_row_data)

        # 버튼 레이아웃 설정
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(reset_button)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        # 인용구 레이아웃
        quote_label = QLabel('made by 나종춘(2024)', self)
        quote_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        quote_label.setStyleSheet("font-size: 10pt;")

        main_layout.addWidget(quote_label)

        self.setLayout(main_layout)

        # QSS 스타일 적용
        self.apply_stylesheet()

        # 데이터 로드
        self.load_data()

        # 버튼 연결
        add_button.clicked.connect(self.add_data)
        update_button.clicked.connect(self.update_data)
        delete_button.clicked.connect(self.delete_data)
        reset_button.clicked.connect(self.reset_fields)

    def apply_stylesheet(self):
        """QSS 스타일 시트를 적용하는 함수"""
        with open(qss_path, "r", encoding="utf-8") as file:
            self.setStyleSheet(file.read())

    def load_stock_data(self):
        """틱커명을 입력하면 종목명과 가격 데이터를 로드하는 함수"""
        ticker = self.ticker_input.text()
        if len(ticker) == 6 and ticker.isdigit():
            ticker_code = f'{ticker}.KS'  # 한국 주식 코드 형식
            try:
                stock = yf.Ticker(ticker_code)
                info = stock.info
                hist = stock.history(period="1y")

                self.name_input.setText(info['longName'])

                price_1yr = int(hist['Close'][0])
                price_6mo = int(hist['Close'][-int(len(hist)/2)])
                current_price = int(hist['Close'][-1])

                self.price_1yr_input.setText(f"{price_1yr:,} 원")
                self.price_6mo_input.setText(f"{price_6mo:,} 원")
                self.current_price_input.setText(f"{current_price:,} 원")
            except Exception as e:
                print(f"Error loading stock data: {e}")

    def load_data(self):
        """JSON 파일에서 데이터를 불러오는 함수"""
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding="utf-8") as file:
                    data = json.load(file)
                    for row_data in data:
                        self.add_table_row(row_data)
            except (json.JSONDecodeError, ValueError):
                # JSON 파일이 비어있거나 포맷이 잘못된 경우
                print("JSON 파일을 불러오는 중 오류가 발생했습니다. 데이터를 초기화합니다.")
                self.save_data()  # 빈 리스트를 저장하여 초기화

    def save_data(self):
        """데이터를 JSON 파일로 저장하는 함수"""
        data = []
        for row in range(self.table.rowCount()):
            ticker_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            price_1yr_item = self.table.item(row, 2)
            price_6mo_item = self.table.item(row, 3)
            current_price_item = self.table.item(row, 4)

            # NoneType 체크를 추가하여 데이터가 없는 경우를 방지
            ticker = ticker_item.text() if ticker_item else ""
            name = name_item.text() if name_item else ""
            price_1yr = price_1yr_item.text() if price_1yr_item else ""
            price_6mo = price_6mo_item.text() if price_6mo_item else ""
            current_price = current_price_item.text() if current_price_item else ""

            data.append([ticker, name, price_1yr, price_6mo, current_price])

        # 파일을 UTF-8 인코딩으로 저장
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add_table_row(self, row_data):
        """테이블에 행을 추가하는 함수"""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for column, data in enumerate(row_data):
            self.table.setItem(row_position, column, QTableWidgetItem(data))

        # 틱커명(첫 번째 열) 중앙 정렬
        item = QTableWidgetItem(row_data[0])
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_position, 0, item)

        # 종목명(두 번째 열) 기본 정렬
        self.table.setItem(row_position, 1, QTableWidgetItem(row_data[1]))

        # 1년전가격(세 번째 열), 6개월전가격(네 번째 열), 현재가격(다섯 번째 열) 오른쪽 및 수직 중앙 정렬
        for i in range(2, 5):
            item = QTableWidgetItem(row_data[i])
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight |
                                  Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_position, i, item)

    def add_data(self):
        """입력된 데이터를 테이블에 추가하고 저장하는 함수"""
        row_data = [
            self.ticker_input.text(),
            self.name_input.text(),
            self.price_1yr_input.text(),
            self.price_6mo_input.text(),
            self.current_price_input.text()
        ]
        self.add_table_row(row_data)
        self.save_data()
        self.reset_fields()  # 데이터 추가 후 필드 초기화

    def load_row_data(self, row, column):
        """테이블의 데이터를 클릭하면 입력 필드에 로드하는 함수"""
        self.ticker_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.price_1yr_input.setText(self.table.item(row, 2).text())
        self.price_6mo_input.setText(self.table.item(row, 3).text())
        self.current_price_input.setText(self.table.item(row, 4).text())

    def update_data(self):
        """선택된 행의 데이터를 수정하고 저장하는 함수"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.setItem(current_row, 0, QTableWidgetItem(
                self.ticker_input.text()))
            self.table.setItem(
                current_row, 1, QTableWidgetItem(self.name_input.text()))
            self.table.setItem(current_row, 2, QTableWidgetItem(
                self.price_1yr_input.text()))
            self.table.setItem(current_row, 3, QTableWidgetItem(
                self.price_6mo_input.text()))
            self.table.setItem(current_row, 4, QTableWidgetItem(
                self.current_price_input.text()))
            self.save_data()
            self.reset_fields()  # 수정 후 필드 초기화

    def delete_data(self):
        """선택된 행을 삭제하고 저장하는 함수"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.save_data()
            self.reset_fields()  # 삭제 후 필드 초기화

    def reset_fields(self):
        """입력 필드를 초기화하는 함수"""
        self.ticker_input.clear()
        self.name_input.clear()
        self.price_1yr_input.clear()
        self.price_6mo_input.clear()
        self.current_price_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StockApp()
    ex.show()
    sys.exit(app.exec_())
