import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDesktopWidget, QTextEdit, QScrollArea, QFrame, QGridLayout
from PyQt5.QtCore import Qt, QDate
import sqlite3

# 신규로 작성된 데이터베이스 파일명
DB_NAME = "stock_management.db"

# 데이터 입력 인터페이스 클래스


class StockEntrySystem(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_item_id = None  # 선택된 항목의 ID 저장
        self.init_ui()

    # GUI 초기화
    def init_ui(self):
        self.setWindowTitle('주식 데이터 입력 시스템')
        self.setGeometry(100, 100, 1000, 700)  # 전체 창 크기 (세로 700으로 조정)

        # 모니터 중앙에 창 배치
        self.center()

        # QSS 스타일 적용
        self.setStyleSheet(STYLE_SHEET)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 주식 데이터 입력 시스템 섹션 라벨
        title_label = QLabel('주식 데이터 입력 시스템')
        title_label.setObjectName('titleLabel')  # QSS에서 스타일을 지정하기 위한 ID 설정
        main_layout.addWidget(title_label)

        # 상단 레이아웃: 입력필드 (600x300) + Total View (400x300)
        top_layout = QHBoxLayout()
        input_layout = QVBoxLayout()
        view_layout = QVBoxLayout()

        # 항목 관리 데이터 로드
        self.load_managed_data()

        # 첫 번째 단: 거래일자, 국가, 증권사
        first_row_layout = QHBoxLayout()

        date_label = QLabel('거래일자:')
        first_row_layout.addWidget(date_label)
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        first_row_layout.addWidget(self.date_input)

        country_label = QLabel('국가:')
        first_row_layout.addWidget(country_label)
        self.country_combo = QComboBox()
        self.country_combo.addItems(self.countries)
        self.country_combo.currentTextChanged.connect(
            self.update_currency_fields)  # 국가 선택 변경 시 실행
        first_row_layout.addWidget(self.country_combo)

        broker_label = QLabel('증권사:')
        first_row_layout.addWidget(broker_label)
        self.broker_combo = QComboBox()
        self.broker_combo.addItems(self.brokers)
        first_row_layout.addWidget(self.broker_combo)

        input_layout.addLayout(first_row_layout)

        # 두 번째 단: 계좌번호, 종목명, 틱커명
        second_row_layout = QHBoxLayout()

        account_label = QLabel('계좌번호:')
        second_row_layout.addWidget(account_label)
        self.account_combo = QComboBox()
        self.account_combo.addItems(self.accounts)
        second_row_layout.addWidget(self.account_combo)

        stock_label = QLabel('종목명:')
        second_row_layout.addWidget(stock_label)
        self.stock_combo = QComboBox()
        self.stock_combo.addItems(self.stocks)
        second_row_layout.addWidget(self.stock_combo)

        ticker_label = QLabel('틱커명:')
        second_row_layout.addWidget(ticker_label)
        self.ticker_combo = QComboBox()
        self.ticker_combo.addItems(self.tickers)  # 틱커명 리스트 추가
        second_row_layout.addWidget(self.ticker_combo)

        input_layout.addLayout(second_row_layout)

        # 세 번째 단: 매수단가, 매수수량, 달러 매수금, 원화 매수금
        third_row_layout = QHBoxLayout()

        price_label = QLabel('매수단가:')
        third_row_layout.addWidget(price_label)
        self.price_input = QLineEdit()
        self.price_input.returnPressed.connect(
            self.focus_quantity_input)  # 엔터 치면 매수수량으로 이동
        third_row_layout.addWidget(self.price_input)

        quantity_label = QLabel('매수수량:')
        third_row_layout.addWidget(quantity_label)
        self.quantity_input = QLineEdit()
        self.quantity_input.returnPressed.connect(self.save_data)  # 엔터 치면 저장
        self.quantity_input.textChanged.connect(
            self.update_amounts)  # 매수수량 변경 시 자동 계산
        third_row_layout.addWidget(self.quantity_input)

        dollar_label = QLabel('달러 매수금:')
        third_row_layout.addWidget(dollar_label)
        self.dollar_input = QLineEdit()
        self.dollar_input.setReadOnly(True)  # 편집 불가
        third_row_layout.addWidget(self.dollar_input)

        won_label = QLabel('원화 매수금:')
        third_row_layout.addWidget(won_label)
        self.won_input = QLineEdit()
        self.won_input.setReadOnly(True)  # 편집 불가
        third_row_layout.addWidget(self.won_input)

        input_layout.addLayout(third_row_layout)

        # 버튼 레이아웃 (저장, 수정, 삭제, 초기화)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('저장')
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)

        self.update_button = QPushButton('수정')
        self.update_button.clicked.connect(self.update_data)
        self.update_button.setEnabled(False)  # 데이터 선택 시 활성화
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton('삭제')
        self.delete_button.clicked.connect(self.delete_data)
        self.delete_button.setEnabled(False)  # 데이터 선택 시 활성화
        button_layout.addWidget(self.delete_button)

        self.clear_button = QPushButton('초기화')
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)

        input_layout.addLayout(button_layout)

        # Total View 섹션 구성
        total_view_title = QLabel('주식매수현황')
        total_view_title.setObjectName('totalViewTitle')
        view_layout.addWidget(total_view_title)

        # 중앙 박스: 틱커명별 매수수량 리스트 표시
        total_view_content = QScrollArea()
        total_view_content.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(
            content_widget)  # self.content_layout으로 변경

        # 틱커명 결과를 담을 그리드 레이아웃
        self.grid_layout = QGridLayout()
        self.content_layout.addLayout(self.grid_layout)

        total_view_content.setWidget(content_widget)
        total_view_content.setObjectName('totalViewContent')

        view_layout.addWidget(total_view_content)

        # 상단 레이아웃 조합
        top_layout.addLayout(input_layout, 6)
        top_layout.addLayout(view_layout, 4)

        main_layout.addLayout(top_layout)

        # 하단 레이아웃: 리스트 테이블 (1000x300)
        self.table = QTableWidget()
        self.table.setColumnCount(11)  # 총 11개의 열 (ID 포함)
        self.table.setHorizontalHeaderLabels(
            ['ID', '거래일자', '국가', '증권사', '계좌번호', '종목명', '틱커명', '매수단가', '매수수량', '달러 매수금', '원화 매수금'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 테이블 셀 수정 금지
        self.table.cellClicked.connect(self.table_item_clicked)

        # 테이블 크기 조절
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        main_layout.addWidget(self.table)

        # 하단 레이아웃: bottom box
        bottom_box = QLabel("by Najongchoon, 2024")
        bottom_box.setObjectName('bottomBox')  # QSS에서 스타일을 지정하기 위한 ID 설정
        # 텍스트 오른쪽 정렬 및 수직 가운데 정렬
        bottom_box.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(bottom_box)
        main_layout.addLayout(bottom_layout)

        # 데이터 로드 및 Total View 업데이트
        self.load_table_data()
        self.update_total_view()

    # 모니터 중앙에 창 배치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 항목 관리 데이터를 로드하는 메서드
    def load_managed_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        self.countries = [row[0]
                          for row in cursor.execute('SELECT name FROM 국가')]
        self.brokers = [row[0]
                        for row in cursor.execute('SELECT name FROM 증권사')]
        self.accounts = [row[0]
                         for row in cursor.execute('SELECT number FROM 계좌번호')]
        self.stocks = [row[0]
                       for row in cursor.execute('SELECT name FROM 종목명')]
        self.tickers = [row[0] for row in cursor.execute(
            'SELECT ticker FROM 틱커명')]  # 틱커명 리스트 로드

        conn.close()

    # 입력 필드를 초기화하는 메서드
    def clear_fields(self):
        self.price_input.clear()
        self.quantity_input.clear()
        self.dollar_input.clear()
        self.won_input.clear()
        self.selected_item_id = None
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    # 매수단가 입력 후 엔터 치면 매수수량 필드로 포커스 이동
    def focus_quantity_input(self):
        self.quantity_input.setFocus()

    # 국가 선택에 따라 달러/원화 필드 상태 업데이트
    def update_currency_fields(self):
        if self.country_combo.currentText() == "대한민국":
            self.dollar_input.setText("$0")
            self.dollar_input.setReadOnly(True)
            self.won_input.setReadOnly(False)
        else:
            self.won_input.setText("₩0")
            self.won_input.setReadOnly(True)
            self.dollar_input.setReadOnly(False)

    # 매수수량 입력 시 달러매수금 및 원화매수금 자동 계산
    def update_amounts(self):
        try:
            price = float(self.price_input.text().replace(',', ''))
            quantity = int(self.quantity_input.text().replace(',', ''))
            if self.country_combo.currentText() == "대한민국":
                self.won_input.setText(f"₩{price * quantity:,.0f}")
            else:
                self.dollar_input.setText(f"${price * quantity:,.0f}")
        except ValueError:
            # 잘못된 입력이 들어올 경우 예외 처리
            self.won_input.clear()
            self.dollar_input.clear()

    # 데이터를 데이터베이스와 테이블에 저장하는 메서드
    def save_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        data = (
            self.date_input.text(),
            self.country_combo.currentText(),
            self.broker_combo.currentText(),
            self.account_combo.currentText(),
            self.stock_combo.currentText(),
            self.ticker_combo.currentText(),
            self.price_input.text().replace(',', ''),  # 저장 시 콤마 제거
            self.quantity_input.text().replace(',', ''),  # 저장 시 콤마 제거
            self.dollar_input.text(),
            self.won_input.text()
        )

        cursor.execute('''
            INSERT INTO stock_data (date, country, broker, account, stock, ticker, price, quantity, dollar_amount, won_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

        conn.commit()
        conn.close()
        self.load_table_data()
        self.clear_fields()
        self.update_total_view()  # 데이터 저장 후 Total View 업데이트

    # 데이터를 수정하는 메서드
    def update_data(self):
        if self.selected_item_id is None:
            QMessageBox.warning(self, "선택 오류", "수정할 데이터를 선택하세요.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        data = (
            self.date_input.text(),
            self.country_combo.currentText(),
            self.broker_combo.currentText(),
            self.account_combo.currentText(),
            self.stock_combo.currentText(),
            self.ticker_combo.currentText(),
            self.price_input.text().replace(',', ''),  # 저장 시 콤마 제거
            self.quantity_input.text().replace(',', ''),  # 저장 시 콤마 제거
            self.dollar_input.text(),
            self.won_input.text(),
            self.selected_item_id
        )

        cursor.execute('''
            UPDATE stock_data
            SET date = ?, country = ?, broker = ?, account = ?, stock = ?, ticker = ?, price = ?, quantity = ?, dollar_amount = ?, won_amount = ?
            WHERE id = ?
        ''', data)

        conn.commit()
        conn.close()
        self.load_table_data()
        self.clear_fields()
        self.update_total_view()  # 데이터 수정 후 Total View 업데이트

    # 데이터를 삭제하는 메서드
    def delete_data(self):
        if self.selected_item_id is None:
            QMessageBox.warning(self, "선택 오류", "삭제할 데이터를 선택하세요.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM stock_data WHERE id = ?',
                       (self.selected_item_id,))

        conn.commit()
        conn.close()
        self.load_table_data()
        self.clear_fields()
        self.update_total_view()  # 데이터 삭제 후 Total View 업데이트

    # 테이블 항목 클릭 시 입력필드에 데이터 로드
    def table_item_clicked(self, row, column):
        self.selected_item_id = int(self.table.item(row, 0).text())
        self.date_input.setDate(QDate.fromString(
            self.table.item(row, 1).text(), 'yyyy-MM-dd'))
        self.country_combo.setCurrentText(self.table.item(row, 2).text())
        self.broker_combo.setCurrentText(self.table.item(row, 3).text())
        self.account_combo.setCurrentText(self.table.item(row, 4).text())
        self.stock_combo.setCurrentText(self.table.item(row, 5).text())
        self.ticker_combo.setCurrentText(self.table.item(row, 6).text())
        self.price_input.setText(
            f"{int(self.table.item(row, 7).text().replace(',', '')):,.0f}")
        self.quantity_input.setText(
            f"{int(self.table.item(row, 8).text().replace(',', '')):,.0f}")
        self.dollar_input.setText(self.table.item(row, 9).text())
        # NoneType 오류 방지: 테이블의 셀이 비어있는 경우 빈 문자열 처리
        won_value = self.table.item(row, 10).text(
        ) if self.table.item(row, 10) else ''
        self.won_input.setText(won_value)
        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    # 테이블 데이터를 로드하는 메서드
    def load_table_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM stock_data')
        rows = cursor.fetchall()

        self.table.setRowCount(0)
        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, data in enumerate(row):
                item = QTableWidgetItem(str(data))
                if column == 0:  # ID 열
                    item.setTextAlignment(Qt.AlignCenter)
                elif column in [6, 7, 8, 9, 10]:  # 오른쪽 정렬 항목
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if column in [7, 8]:  # 천 단위 콤마 적용
                    item.setText(f"{int(data):,}")
                self.table.setItem(row_position, column, item)

        conn.close()

    # Total View를 업데이트하는 메서드
    def update_total_view(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT ticker, SUM(quantity) FROM stock_data GROUP BY ticker')
        rows = cursor.fetchall()

        # 그리드 레이아웃 초기화
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        total_quantity = 0
        row = 0
        col = 0
        for data in rows:
            ticker, quantity = data
            total_quantity += quantity
            label = QLabel(f"• {ticker}: {quantity:,} 주")
            label.setObjectName('tickerLabel')
            self.grid_layout.addWidget(label, row, col)
            col += 1
            if col > 1:  # 2열을 채우면 다음 행으로
                col = 0
                row += 1

        # 구분선 추가
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("border: 1px solid grey;")
        self.content_layout.addWidget(separator)

        # 주식 총 매수량 추가
        total_summary_label = QLabel(f"• 주식 총 매수: {total_quantity:,} 주")
        total_summary_label.setAlignment(Qt.AlignCenter)
        total_summary_label.setObjectName('totalSummaryLabel')
        self.content_layout.addWidget(total_summary_label)

        conn.close()


if __name__ == '__main__':
    # 데이터베이스 초기 설정: stock_data 테이블 생성
    def initialize_database():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                country TEXT NOT NULL,
                broker TEXT NOT NULL,
                account TEXT NOT NULL,
                stock TEXT NOT NULL,
                ticker TEXT NOT NULL,
                price TEXT NOT NULL,
                quantity TEXT NOT NULL,
                dollar_amount TEXT NOT NULL,
                won_amount TEXT
            )
        ''')
        conn.commit()
        conn.close()

    initialize_database()

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    STYLE_SHEET = """
    QLabel {
        font-family: '맑은 고딕';
        font-weight: bold;
    }

    #titleLabel {
        background-color: #000000;
        color: white;
        font-size: 18px;
        padding: 10px;
        text-align: center;
    }

    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border: none;
        border-radius: 4px;
        font-size: 14px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QTableWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }

    QHeaderView::section {
        background-color: lightgray;
        font-weight: bold;
    }

    #bottomBox {
        background-color: #c3c1c5;
        font-style: italic;
        padding: 5px;
        font-size: 14px;
    }

    #totalViewTitle, #totalViewContent {
        font-family: '맑은 고딕';
        font-size: 10pt;
        border: 1px solid grey;
        border-radius: 5px;
        padding: 10px;
        background-color: #f9f9f9;
    }

    #totalViewTitle {
        color: #333333;
        font-size: 10pt;
        background-color: #e6e6e6;
    }

    #totalViewContent {
        color: #555555;
        font-size: 10pt;
        background-color: #ffffff;
    }

    #tickerLabel {
        font-size: 10pt;
        color: #333333;
        padding: 5px;
    }

    #totalSummaryLabel {
        font-size: 10pt;
        color: #111111;
        padding: 10px;
    }
    """
    window = StockEntrySystem()
    window.show()
    sys.exit(app.exec_())
