import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QDateEdit, QComboBox, QPushButton,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor


class StockManagementApp(QWidget):
    def __init__(self):
        super().__init__()

        # 최초 프로그램 실행 시 'data_list.xlsx' 파일 생성
        self.initialize_excel_file()

        # 창 제목 설정
        self.setWindowTitle('주식 매수 관리')

        # 창 배경색과 폰트 컬러 설정
        self.setStyleSheet("background-color: #4a5569; color: white;")

        # 폰트 설정
        label_font = QFont("맑은 고딕", weight=QFont.Bold)

        # 첫 번째 섹션 (입력 폼과 버튼)
        first_section = QGroupBox('First Section')
        first_section.setStyleSheet(
            "QGroupBox { font: bold 12pt '맑은 고딕'; color: white; }")
        first_section_layout = QGridLayout()

        # 첫 번째 줄 항목
        trade_date_label = QLabel('거래일자')
        trade_date_label.setFont(label_font)
        first_section_layout.addWidget(trade_date_label, 0, 0)

        self.trade_date = QDateEdit(self)
        self.trade_date.setCalendarPopup(True)
        self.trade_date.setDisplayFormat("yyyy-MM-dd")  # 날짜 형식 지정
        self.trade_date.setDate(QDate.currentDate())  # 현재 날짜로 설정
        first_section_layout.addWidget(self.trade_date, 0, 1)

        country_label = QLabel('국가')
        country_label.setFont(label_font)
        first_section_layout.addWidget(country_label, 0, 2)

        self.country = QComboBox(self)
        self.country.addItems(['대한민국', '미국', '일본', '중국'])  # 필요에 따라 항목 추가
        self.country.currentTextChanged.connect(
            self.update_currency_mode)  # 국가 변경 시 편집 모드 갱신
        first_section_layout.addWidget(self.country, 0, 3)

        broker_label = QLabel('증권사')
        broker_label.setFont(label_font)
        first_section_layout.addWidget(broker_label, 0, 4)

        self.broker = QComboBox(self)
        self.broker.addItems(['삼성증권', '미래에셋', '키움증권'])  # 필요에 따라 항목 추가
        first_section_layout.addWidget(self.broker, 0, 5)

        account_number_label = QLabel('계좌번호')
        account_number_label.setFont(label_font)
        first_section_layout.addWidget(account_number_label, 0, 6)

        self.account_number = QComboBox(self)
        self.account_number.addItems(
            ['123-456-789', '987-654-321', '555-666-777'])  # 예시 항목
        first_section_layout.addWidget(self.account_number, 0, 7)

        stock_name_label = QLabel('종목명')
        stock_name_label.setFont(label_font)
        first_section_layout.addWidget(stock_name_label, 0, 8)

        self.stock_name = QComboBox(self)
        self.stock_name.addItems(['삼성전자', '애플', '테슬라'])  # 예시 항목
        first_section_layout.addWidget(self.stock_name, 0, 9)

        # 두 번째 줄 항목
        ticker_label = QLabel('틱커명')
        ticker_label.setFont(label_font)
        first_section_layout.addWidget(ticker_label, 1, 0)

        self.ticker = QComboBox(self)
        self.ticker.addItems(['005930', 'AAPL', 'TSLA'])  # 예시 항목
        first_section_layout.addWidget(self.ticker, 1, 1)

        purchase_price_label = QLabel('매수단가')
        purchase_price_label.setFont(label_font)
        first_section_layout.addWidget(purchase_price_label, 1, 2)

        self.purchase_price = QLineEdit(self)
        self.purchase_price.returnPressed.connect(
            self.move_to_quantity)  # 엔터 누르면 다음 항목으로 이동
        self.purchase_price.textChanged.connect(self.calculate_amount)
        first_section_layout.addWidget(self.purchase_price, 1, 3)

        purchase_quantity_label = QLabel('매수수량')
        purchase_quantity_label.setFont(label_font)
        first_section_layout.addWidget(purchase_quantity_label, 1, 4)

        self.purchase_quantity = QLineEdit(self)
        self.purchase_quantity.textChanged.connect(self.calculate_amount)
        first_section_layout.addWidget(self.purchase_quantity, 1, 5)

        purchase_amount_usd_label = QLabel('달러매수금')
        purchase_amount_usd_label.setFont(label_font)
        first_section_layout.addWidget(purchase_amount_usd_label, 1, 6)

        self.purchase_amount_usd = QLineEdit(self)
        first_section_layout.addWidget(self.purchase_amount_usd, 1, 7)

        purchase_amount_krw_label = QLabel('원화매수금')
        purchase_amount_krw_label.setFont(label_font)
        first_section_layout.addWidget(purchase_amount_krw_label, 1, 8)

        self.purchase_amount_krw = QLineEdit(self)
        first_section_layout.addWidget(self.purchase_amount_krw, 1, 9)

        # 세 번째 줄 버튼들
        btn_layout = QHBoxLayout()

        button_style = """
        QPushButton {
            background-color: #2c333e;
            color: white;
            font: bold "맑은 고딕";
        }
        QPushButton:pressed {
            background-color: #1c1f26;
        }
        """

        self.add_button = QPushButton('추가', self)
        self.add_button.setFixedSize(170, 25)
        self.add_button.setStyleSheet(button_style)
        self.add_button.clicked.connect(self.add_entry)  # 버튼 클릭 시 데이터 추가
        btn_layout.addWidget(self.add_button)

        self.update_button = QPushButton('수정', self)
        self.update_button.setFixedSize(170, 25)
        self.update_button.setStyleSheet(button_style)
        self.update_button.clicked.connect(self.update_entry)  # 버튼 클릭 시 데이터 수정
        btn_layout.addWidget(self.update_button)

        self.delete_button = QPushButton('삭제', self)
        self.delete_button.setFixedSize(170, 25)
        self.delete_button.setStyleSheet(button_style)
        self.delete_button.clicked.connect(self.delete_entry)  # 버튼 클릭 시 데이터 삭제
        btn_layout.addWidget(self.delete_button)

        self.reset_button = QPushButton('초기화', self)
        self.reset_button.setFixedSize(170, 25)
        self.reset_button.setStyleSheet(button_style)
        self.reset_button.clicked.connect(self.reset_form)  # 초기화 버튼 기능
        btn_layout.addWidget(self.reset_button)

        # 첫 번째 섹션에 버튼 레이아웃 추가
        first_section_layout.addLayout(btn_layout, 2, 0, 1, 10)

        first_section.setLayout(first_section_layout)

        # 두 번째 섹션 (테이블 리스트)
        second_section = QGroupBox('Second Section')
        second_section.setStyleSheet(
            "QGroupBox { font: bold 12pt '맑은 고딕'; color: white; }")
        second_section_layout = QVBoxLayout()

        # 테이블 생성
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['거래일자', '국가', '증권사', '계좌번호', '종목명',
                                              '틱커명', '매수단가', '매수수량', '달러매수금', '원화매수금'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.load_entry)  # 행 선택 시 데이터 불러오기
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 열 크기 조정
        second_section_layout.addWidget(self.table)

        # 테이블 헤더 스타일 설정
        header = self.table.horizontalHeader()
        header.setStyleSheet("""
        QHeaderView::section {
            background-color: #2c333e;
            color: white;
            font: bold "맑은 고딕";
        }
        """)

        second_section.setLayout(second_section_layout)

        # 전체 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.addWidget(first_section)
        main_layout.addWidget(second_section)

        self.setLayout(main_layout)

        # 창 크기 조정 및 화면 중앙 배치
        self.resize(850, 850)
        self.setMinimumSize(600, 600)  # 최소 창 크기 설정
        self.center()

        # 초기 데이터 로드
        self.load_data()

        # 초기 상태 설정
        self.update_currency_mode()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initialize_excel_file(self):
        file_path = 'data_list.xlsx'
        if not os.path.exists(file_path):
            df = pd.DataFrame(columns=['거래일자', '국가', '증권사', '계좌번호', '종목명', '틱커명',
                                       '매수단가', '매수수량', '달러매수금', '원화매수금'])
            df.to_excel(file_path, index=False)

    def load_data(self):
        file_path = 'data_list.xlsx'
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            self.table.setRowCount(len(df))
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def add_entry(self):
        # 입력된 데이터를 읽어옴
        data = {
            '거래일자': self.trade_date.date().toString('yyyy-MM-dd'),
            '국가': self.country.currentText(),
            '증권사': self.broker.currentText(),
            '계좌번호': self.account_number.currentText(),
            '종목명': self.stock_name.currentText(),
            '틱커명': self.ticker.currentText(),
            '매수단가': self.purchase_price.text().replace(',', ''),
            '매수수량': self.purchase_quantity.text().replace(',', ''),
            '달러매수금': self.format_currency(self.purchase_amount_usd.text(), "$"),
            '원화매수금': self.format_currency(self.purchase_amount_krw.text(), "₩"),
        }

        # 테이블에 데이터 추가
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for i, (key, value) in enumerate(data.items()):
            self.table.setItem(row_position, i, QTableWidgetItem(value))

        # 엑셀 파일에 저장
        self.save_to_excel()

        QMessageBox.information(self, "성공", "데이터가 저장되었습니다.")
        self.reset_form()

    def update_entry(self):
        row = self.table.currentRow()
        if row >= 0:
            # 테이블 업데이트
            self.table.setItem(row, 0, QTableWidgetItem(
                self.trade_date.date().toString('yyyy-MM-dd')))
            self.table.setItem(row, 1, QTableWidgetItem(
                self.country.currentText()))
            self.table.setItem(row, 2, QTableWidgetItem(
                self.broker.currentText()))
            self.table.setItem(row, 3, QTableWidgetItem(
                self.account_number.currentText()))
            self.table.setItem(row, 4, QTableWidgetItem(
                self.stock_name.currentText()))
            self.table.setItem(row, 5, QTableWidgetItem(
                self.ticker.currentText()))
            self.table.setItem(row, 6, QTableWidgetItem(
                self.purchase_price.text().replace(',', '')))
            self.table.setItem(row, 7, QTableWidgetItem(
                self.purchase_quantity.text().replace(',', '')))
            self.table.setItem(row, 8, QTableWidgetItem(
                self.format_currency(self.purchase_amount_usd.text(), "$")))
            self.table.setItem(row, 9, QTableWidgetItem(
                self.format_currency(self.purchase_amount_krw.text(), "₩")))

            # 엑셀 파일에 저장
            self.save_to_excel()

            QMessageBox.information(self, "성공", "데이터가 수정되었습니다.")
            self.reset_form()
        else:
            QMessageBox.warning(self, "오류", "수정할 데이터를 선택하세요.")

    def delete_entry(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

            # 엑셀 파일에 저장
            self.save_to_excel()

            QMessageBox.information(self, "성공", "데이터가 삭제되었습니다.")
            self.reset_form()
        else:
            QMessageBox.warning(self, "오류", "삭제할 데이터를 선택하세요.")

    def load_entry(self, row, column):
        self.trade_date.setDate(QDate.fromString(
            self.table.item(row, 0).text(), 'yyyy-MM-dd'))
        self.country.setCurrentText(self.table.item(row, 1).text())
        self.broker.setCurrentText(self.table.item(row, 2).text())
        self.account_number.setCurrentText(self.table.item(row, 3).text())
        self.stock_name.setCurrentText(self.table.item(row, 4).text())
        self.ticker.setCurrentText(self.table.item(row, 5).text())
        self.purchase_price.setText(
            self.format_for_display(self.table.item(row, 6).text()))
        self.purchase_quantity.setText(
            self.format_for_display(self.table.item(row, 7).text()))
        self.purchase_amount_usd.setText(self.table.item(
            row, 8).text().replace("$", "").replace(",", ""))
        self.purchase_amount_krw.setText(self.table.item(
            row, 9).text().replace("₩", "").replace(",", ""))
        self.update_currency_mode()

    def save_to_excel(self):
        file_path = 'data_list.xlsx'
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        df = pd.DataFrame(data, columns=['거래일자', '국가', '증권사', '계좌번호', '종목명',
                                         '틱커명', '매수단가', '매수수량', '달러매수금', '원화매수금'])
        df.to_excel(file_path, index=False)

    def reset_form(self):
        self.purchase_price.clear()
        self.purchase_quantity.clear()
        self.purchase_amount_usd.clear()
        self.purchase_amount_krw.clear()

    def move_to_quantity(self):
        self.purchase_quantity.setFocus()

    def format_number(self, line_edit):
        text = line_edit.text().replace(',', '')  # 기존 콤마 제거
        if text.isdigit():
            formatted_text = "{:,}".format(int(text))  # 천 단위로 콤마 추가
            line_edit.setText(formatted_text)

    def format_for_display(self, value):
        return "{:,}".format(int(value)) if value.isdigit() else value

    def format_currency(self, value, symbol):
        if value.isdigit():
            return f"{symbol}{int(value):,}"
        return value

    def update_currency_mode(self):
        if self.country.currentText() == "대한민국":
            self.purchase_amount_usd.setReadOnly(True)
            self.purchase_amount_krw.setReadOnly(False)
            self.purchase_amount_usd.clear()
        else:
            self.purchase_amount_krw.setReadOnly(True)
            self.purchase_amount_usd.setReadOnly(False)
            self.purchase_amount_krw.clear()

    def calculate_amount(self):
        try:
            price = int(self.purchase_price.text().replace(',', ''))
            quantity = int(self.purchase_quantity.text().replace(',', ''))
            amount = price * quantity
            if self.country.currentText() == "대한민국":
                self.purchase_amount_krw.setText("{:,}".format(amount))
            else:
                self.purchase_amount_usd.setText("{:,}".format(amount))
        except ValueError:
            pass


if __name__ == '__main__':
    # 필요한 라이브러리 설치 안내
    try:
        import pandas as pd
    except ImportError:
        print("pandas 라이브러리가 필요합니다. 설치하려면 'pip install pandas' 명령어를 사용하세요.")

    app = QApplication(sys.argv)
    window = StockManagementApp()
    window.show()
    sys.exit(app.exec_())
