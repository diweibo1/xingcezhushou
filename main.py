import sys
import csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate  # 添加 QDate 导入
from database import *

init_db()

class InputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.module = QComboBox()
        self.module.addItems(["言语理解", "数量关系", "判断推理", "资料分析", "常识判断"])
        
        self.source = QLineEdit()
        self.content = QTextEdit()
        self.answer = QLineEdit()
        self.analysis = QTextEdit()  # 新增错题解析字段
        self.question_type = QLineEdit()  # 新增题型字段
        self.entry_time = QDateEdit()  # 新增录入时间字段
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("题型模块:", self.module)
        form_layout.addRow("题目来源:", self.source)
        form_layout.addRow("题目内容:", self.content)
        form_layout.addRow("正确答案:", self.answer)
        form_layout.addRow("错题解析:", self.analysis)  # 新增错题解析字段
        form_layout.addRow("题型:", self.question_type)  # 新增题型字段
        form_layout.addRow("录入时间:", self.entry_time)  # 新增录入时间字段
        
        submit_btn = QPushButton("保存题目")
        submit_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(submit_btn)
        self.setLayout(layout)

    def save(self):
        try:
            new_id = add_question(
                self.module.currentText(),
                self.source.text(),
                self.content.toPlainText(),
                self.answer.text(),
                self.analysis.toPlainText(),  # 保存错题解析
                self.question_type.text(),  # 保存题型
                self.entry_time.date().toString("yyyy-MM-dd")  # 保存录入时间
            )
            QMessageBox.information(self, "成功", "题目已保存！")
            self.source.clear()
            self.content.clear()
            self.answer.clear()
            self.analysis.clear()  # 清空错题解析字段
            self.question_type.clear()  # 清空题型字段
            self.entry_time.setDate(QDate.currentDate())  # 重置录入时间字段
            self.parentWidget().parentWidget().parentWidget().review_tab.load_data()  # 确保正确调用 load_data
        except Exception as e:
            print(f"Error: {e}")  # 添加调试信息
            QMessageBox.critical(self, "错误", f"保存题目时出错: {e}")

class ReviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("输入关键词筛选题目")
        self.filter_input.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.module_filter = QComboBox()
        self.module_filter.addItems(["全部", "言语理解", "数量关系", "判断推理", "资料分析", "常识判断"])
        self.module_filter.currentIndexChanged.connect(self.load_data)  # 绑定筛选事件

        self.source_filter = QComboBox()
        self.source_filter.addItems(["全部"] + get_all_sources())
        self.source_filter.currentIndexChanged.connect(self.load_data)  # 绑定筛选事件

        self.question_type_filter = QLineEdit()
        self.question_type_filter.setPlaceholderText("输入题型筛选")
        self.question_type_filter.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.entry_time_filter = QComboBox()
        self.entry_time_filter.addItems(["全部时间", "选择日期"])
        self.entry_time_filter.currentIndexChanged.connect(self.toggle_date_filter)  # 绑定筛选事件

        self.entry_time_date = QDateEdit()
        self.entry_time_date.setCalendarPopup(True)
        self.entry_time_date.setDisplayFormat("yyyy-MM-dd")
        self.entry_time_date.setVisible(False)
        self.entry_time_date.dateChanged.connect(self.load_data)  # 绑定筛选事件

        self.reviews_filter = QLineEdit()
        self.reviews_filter.setPlaceholderText("输入复盘次数筛选")
        self.reviews_filter.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.sort_order = "asc"
        self.sort_button = QPushButton("ID排序: 正序")
        self.sort_button.clicked.connect(self.toggle_sort_order)

        filter_layout.addWidget(QLabel("关键词:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("题型模块:"))
        filter_layout.addWidget(self.module_filter)
        filter_layout.addWidget(QLabel("题目来源:"))
        filter_layout.addWidget(self.source_filter)
        filter_layout.addWidget(QLabel("题型:"))
        filter_layout.addWidget(self.question_type_filter)
        filter_layout.addWidget(QLabel("录入时间:"))
        filter_layout.addWidget(self.entry_time_filter)
        filter_layout.addWidget(self.entry_time_date)
        filter_layout.addWidget(QLabel("复盘次数:"))
        filter_layout.addWidget(self.reviews_filter)
        filter_layout.addWidget(self.sort_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # 修改列数为8
        self.table.setHorizontalHeaderLabels(["ID", "题型模块", "题目来源", "题目内容", "正确答案", "复盘次数", "题型", "录入时间"])  # 修改表头
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 设置选择行为为选择行
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 设置选择模式为单选
        self.table.cellDoubleClicked.connect(self.edit_question)

        delete_btn = QPushButton("删除题目")
        delete_btn.clicked.connect(self.delete_question)

        export_btn = QPushButton("导出题目")
        export_btn.clicked.connect(self.export_data)

        import_btn = QPushButton("导入题目")
        import_btn.clicked.connect(self.import_data)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(delete_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        self.setLayout(layout)

    def toggle_date_filter(self):
        if self.entry_time_filter.currentText() == "选择日期":
            self.entry_time_date.setVisible(True)
        else:
            self.entry_time_date.setVisible(False)
            self.load_data()

    def load_data(self):
        filter_text = self.filter_input.text()
        selected_module = self.module_filter.currentText()
        selected_source = self.source_filter.currentText()
        selected_question_type = self.question_type_filter.text()
        selected_entry_time = self.entry_time_date.date().toString("yyyy-MM-dd") if self.entry_time_filter.currentText() == "选择日期" else ""
        selected_reviews = self.reviews_filter.text()
        self.table.setRowCount(0)
        questions = get_all_questions()
        if self.sort_order == "asc":
            questions.sort(key=lambda x: x[0])
        elif self.sort_order == "desc":
            questions.sort(key=lambda x: x[0], reverse=True)
        elif self.sort_order == "random":
            import random
            random.shuffle(questions)
        for row in questions:
            if (selected_module == "全部" or row[1] == selected_module) and \
               (selected_source == "全部" or row[2] == selected_source) and \
               (selected_question_type == "" or row[6] == selected_question_type) and \
               (selected_entry_time == "" or row[7] == selected_entry_time) and \
               (selected_reviews == "" or str(row[5]) == selected_reviews) and \
               filter_text.lower() in str(row).lower():  # 根据关键词进行筛选
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                for col, item in enumerate(row):  # 确保处理所有字段，包括 entry_time
                    table_item = QTableWidgetItem(str(item))
                    if col == 4:  # 正确答案列
                        table_item.setForeground(Qt.red)
                    self.table.setItem(row_pos, col, table_item)

    def toggle_sort_order(self):
        if self.sort_order == "asc":
            self.sort_order = "desc"
            self.sort_button.setText("ID排序: 倒序")
        elif self.sort_order == "desc":
            self.sort_order = "random"
            self.sort_button.setText("ID排序: 随机")
        else:
            self.sort_order = "asc"
            self.sort_button.setText("ID排序: 正序")
        self.load_data()

    def edit_question(self, row):
        qid = int(self.table.item(row, 0).text())
        dialog = EditDialog(qid)
        if dialog.exec_():
            self.load_data()

    def delete_question(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            qid = int(selected_items[0].text())
            try:
                delete_question(qid)
                QMessageBox.information(self, "成功", "题目已删除！")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除题目时出错: {e}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出题目", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "题型模块", "题目来源", "题目内容", "正确答案", "复盘次数", "题型", "录入时间"])
                for row in get_all_questions():
                    writer.writerow(row)
            QMessageBox.information(self, "成功", "题目已导出！")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入题目", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过表头
                for row in reader:
                    add_question(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            self.load_data()
            QMessageBox.information(self, "成功", "题目已导入！")

class IdiomInputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.category = QLineEdit()
        self.name = QLineEdit()
        self.meaning = QTextEdit()
        self.context = QTextEdit()
        self.collocation = QTextEdit()
        self.example = QTextEdit()
        self.entry_time = QDateEdit()  # 新增录入时间字段
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("成语分类:", self.category)
        form_layout.addRow("成语名称:", self.name)
        form_layout.addRow("语义:", self.meaning)
        form_layout.addRow("常用语境:", self.context)
        form_layout.addRow("固定搭配:", self.collocation)
        form_layout.addRow("例句:", self.example)
        form_layout.addRow("录入时间:", self.entry_time)  # 新增录入时间字段
        
        submit_btn = QPushButton("保存成语")
        submit_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(submit_btn)
        self.setLayout(layout)

    def save(self):
        if check_duplicate_idiom(self.name.text()):
            QMessageBox.warning(self, "重复", "成语已存在！")
            return
        try:
            new_id = add_idiom(
                self.category.text(),
                self.name.text(),
                self.meaning.toPlainText(),
                self.context.toPlainText(),
                self.collocation.toPlainText(),
                self.example.toPlainText(),
                self.entry_time.date().toString("yyyy-MM-dd")  # 保存录入时间
            )
            QMessageBox.information(self, "成功", "成语已保存！")
            self.category.clear()
            self.name.clear()
            self.meaning.clear()
            self.context.clear()
            self.collocation.clear()
            self.example.clear()
            self.entry_time.setDate(QDate.currentDate())  # 重置录入时间字段
            self.parentWidget().parentWidget().parentWidget().idiom_review_tab.load_data()  # 确保正确调用 load_data
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存成语时出错: {e}")

class IdiomReviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("输入关键词筛选成语")
        self.filter_input.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("输入分类筛选成语")
        self.category_filter.textChanged.connect(self.load_data)  # 绑定筛选事件
        
        filter_layout.addWidget(QLabel("关键词:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("分类:"))
        filter_layout.addWidget(self.category_filter)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # 修改列数为8
        self.table.setHorizontalHeaderLabels(["ID", "分类", "名称", "语义", "常用语境", "固定搭配", "例句", "录入时间"])  # 修改表头
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 设置选择行为为选择行
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 设置选择模式为单选
        self.table.cellDoubleClicked.connect(self.edit_idiom)

        delete_btn = QPushButton("删除成语")
        delete_btn.clicked.connect(self.delete_idiom)

        export_btn = QPushButton("导出成语")
        export_btn.clicked.connect(self.export_data)

        import_btn = QPushButton("导入成语")
        import_btn.clicked.connect(self.import_data)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(delete_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        self.setLayout(layout)

    def load_data(self):
        filter_text = self.filter_input.text()
        selected_category = self.category_filter.text()
        self.table.setRowCount(0)
        for row in get_all_idioms():
            if (selected_category == "" or row[1] == selected_category) and \
               filter_text.lower() in str(row).lower():  # 根据关键词进行筛选
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                for col, item in enumerate(row[:8]):  # 修改列数为8
                    self.table.setItem(row_pos, col, QTableWidgetItem(str(item)))

    def edit_idiom(self, row):
        qid = int(self.table.item(row, 0).text())
        dialog = EditIdiomDialog(qid)
        if dialog.exec_():
            self.load_data()

    def delete_idiom(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            qid = int(selected_items[0].text())
            try:
                delete_idiom(qid)
                QMessageBox.information(self, "成功", "成语已删除！")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除成语时出错: {e}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出成语", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "分类", "名称", "语义", "常用语境", "固定搭配", "例句", "录入时间"])
                for row in get_all_idioms():
                    writer.writerow(row)
            QMessageBox.information(self, "成功", "成语已导出！")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入成语", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过表头
                for row in reader:
                    add_idiom(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            self.load_data()
            QMessageBox.information(self, "成功", "成语已导入！")

class ExamInputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.year = QLineEdit()
        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.paper_name = QLineEdit()
        self.politics_total = QLineEdit()  # 修改为 QLineEdit
        self.politics_correct = QLineEdit()  # 修改为 QLineEdit
        self.general_knowledge_total = QLineEdit()  # 修改为 QLineEdit
        self.general_knowledge_correct = QLineEdit()  # 修改为 QLineEdit
        self.logic_total = QLineEdit()  # 修改为 QLineEdit
        self.logic_correct = QLineEdit()  # 修改为 QLineEdit
        self.fragment_total = QLineEdit()  # 修改为 QLineEdit
        self.fragment_correct = QLineEdit()  # 修改为 QLineEdit
        self.quantitative_total = QLineEdit()  # 修改为 QLineEdit
        self.quantitative_correct = QLineEdit()  # 修改为 QLineEdit
        self.graphic_reasoning_total = QLineEdit()  # 修改为 QLineEdit
        self.graphic_reasoning_correct = QLineEdit()  # 修改为 QLineEdit
        self.definition_total = QLineEdit()  # 修改为 QLineEdit
        self.definition_correct = QLineEdit()  # 修改为 QLineEdit
        self.analogy_total = QLineEdit()  # 修改为 QLineEdit
        self.analogy_correct = QLineEdit()  # 修改为 QLineEdit
        self.data_analysis_total = QLineEdit()  # 修改为 QLineEdit
        self.data_analysis_correct = QLineEdit()  # 修改为 QLineEdit
        self.total_correct = QLineEdit()  # 修改为 QLineEdit
        self.total_questions = QLineEdit()  # 修改为 QLineEdit
        self.score = QLineEdit()  # 修改为 QLineEdit
        
        form_layout.addRow("年份:", self.year)
        form_layout.addRow("完成日期:", self.completion_date)
        form_layout.addRow("卷名:", self.paper_name)
        form_layout.addRow("政治总数:", self.politics_total)
        form_layout.addRow("政治正确数:", self.politics_correct)
        form_layout.addRow("常识总数:", self.general_knowledge_total)
        form_layout.addRow("常识正确数:", self.general_knowledge_correct)
        form_layout.addRow("逻辑总数:", self.logic_total)
        form_layout.addRow("逻辑正确数:", self.logic_correct)
        form_layout.addRow("片段总数:", self.fragment_total)
        form_layout.addRow("片段正确数:", self.fragment_correct)
        form_layout.addRow("数量关系总数:", self.quantitative_total)
        form_layout.addRow("数量关系正确数:", self.quantitative_correct)
        form_layout.addRow("图推总数:", self.graphic_reasoning_total)
        form_layout.addRow("图推正确数:", self.graphic_reasoning_correct)
        form_layout.addRow("定义总数:", self.definition_total)
        form_layout.addRow("定义正确数:", self.definition_correct)
        form_layout.addRow("类比总数:", self.analogy_total)
        form_layout.addRow("类比正确数:", self.analogy_correct)
        form_layout.addRow("资料分析总数:", self.data_analysis_total)
        form_layout.addRow("资料分析正确数:", self.data_analysis_correct)
        form_layout.addRow("总正确数:", self.total_correct)
        form_layout.addRow("总题量:", self.total_questions)
        form_layout.addRow("成绩:", self.score)
        
        submit_btn = QPushButton("保存套卷")
        submit_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(submit_btn)
        self.setLayout(layout)

    def save(self):
        try:
            new_id = add_exam_paper(
                int(self.year.text()),
                self.completion_date.date().toString("yyyy-MM-dd"),
                self.paper_name.text(),
                int(self.politics_total.text()),  # 转换为整数
                int(self.politics_correct.text()),  # 转换为整数
                int(self.general_knowledge_total.text()),  # 转换为整数
                int(self.general_knowledge_correct.text()),  # 转换为整数
                int(self.logic_total.text()),  # 转换为整数
                int(self.logic_correct.text()),  # 转换为整数
                int(self.fragment_total.text()),  # 转换为整数
                int(self.fragment_correct.text()),  # 转换为整数
                int(self.quantitative_total.text()),  # 转换为整数
                int(self.quantitative_correct.text()),  # 转换为整数
                int(self.graphic_reasoning_total.text()),  # 转换为整数
                int(self.graphic_reasoning_correct.text()),  # 转换为整数
                int(self.definition_total.text()),  # 转换为整数
                int(self.definition_correct.text()),  # 转换为整数
                int(self.analogy_total.text()),  # 转换为整数
                int(self.analogy_correct.text()),  # 转换为整数
                int(self.data_analysis_total.text()),  # 转换为整数
                int(self.data_analysis_correct.text()),  # 转换为整数
                int(self.total_correct.text()),  # 转换为整数
                int(self.total_questions.text()),  # 转换为整数
                float(self.score.text())  # 转换为浮点数
            )
            QMessageBox.information(self, "成功", "套卷已保存！")
            self.clear_fields()
            self.parentWidget().parentWidget().parentWidget().exam_review_tab.load_data()
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(self, "错误", f"保存套卷时出错: {e}")

    def clear_fields(self):
        self.year.clear()
        self.completion_date.setDate(QDate.currentDate())
        self.paper_name.clear()
        self.politics_total.clear()
        self.politics_correct.clear()
        self.general_knowledge_total.clear()
        self.general_knowledge_correct.clear()
        self.logic_total.clear()
        self.logic_correct.clear()
        self.fragment_total.clear()
        self.fragment_correct.clear()
        self.quantitative_total.clear()
        self.quantitative_correct.clear()
        self.graphic_reasoning_total.clear()
        self.graphic_reasoning_correct.clear()
        self.definition_total.clear()
        self.definition_correct.clear()
        self.analogy_total.clear()
        self.analogy_correct.clear()
        self.data_analysis_total.clear()
        self.data_analysis_correct.clear()
        self.total_correct.clear()
        self.total_questions.clear()
        self.score.clear()

class ExamReviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("输入关键词筛选套卷")
        self.filter_input.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.year_filter = QLineEdit()
        self.year_filter.setPlaceholderText("输入年份筛选")
        self.year_filter.textChanged.connect(self.load_data)  # 绑定筛选事件

        self.completion_date_filter = QComboBox()
        self.completion_date_filter.addItems(["全部时间", "选择日期"])
        self.completion_date_filter.currentIndexChanged.connect(self.toggle_date_filter)  # 绑定筛选事件

        self.completion_date_date = QDateEdit()
        self.completion_date_date.setCalendarPopup(True)
        self.completion_date_date.setDisplayFormat("yyyy-MM-dd")
        self.completion_date_date.setVisible(False)
        self.completion_date_date.dateChanged.connect(self.load_data)  # 绑定筛选事件
        
        filter_layout.addWidget(QLabel("关键词:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("年份:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("完成日期:"))
        filter_layout.addWidget(self.completion_date_filter)
        filter_layout.addWidget(self.completion_date_date)
        
        self.table = QTableWidget()
        self.table.setColumnCount(25)  # 修改列数为25
        self.table.setHorizontalHeaderLabels(["ID", "年份", "完成日期", "卷名", "政治总数", "政治正确数", "常识总数", "常识正确数", "逻辑总数", "逻辑正确数", "片段总数", "片段正确数", "数量关系总数", "数量关系正确数", "图推总数", "图推正确数", "定义总数", "定义正确数", "类比总数", "类比正确数", "资料分析总数", "资料分析正确数", "总正确数", "总题量", "成绩"])  # 修改表头
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 设置选择行为为选择行
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 设置选择模式为单选
        self.table.cellDoubleClicked.connect(self.edit_exam_paper)

        delete_btn = QPushButton("删除套卷")
        delete_btn.clicked.connect(self.delete_exam_paper)

        export_btn = QPushButton("导出套卷")
        export_btn.clicked.connect(self.export_data)

        import_btn = QPushButton("导入套卷")
        import_btn.clicked.connect(self.import_data)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(delete_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        self.setLayout(layout)

    def toggle_date_filter(self):
        if self.completion_date_filter.currentText() == "选择日期":
            self.completion_date_date.setVisible(True)
        else:
            self.completion_date_date.setVisible(False)
            self.load_data()

    def load_data(self):
        filter_text = self.filter_input.text()
        selected_year = self.year_filter.text()
        selected_completion_date = self.completion_date_date.date().toString("yyyy-MM-dd") if self.completion_date_filter.currentText() == "选择日期" else ""
        self.table.setRowCount(0)
        for row in get_all_exam_papers():
            if (selected_year == "" or str(row[1]) == selected_year) and \
               (selected_completion_date == "" or row[2] == selected_completion_date) and \
               filter_text.lower() in str(row).lower():  # 根据关键词进行筛选
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                for col, item in enumerate(row[:25]):  # 修改列数为25
                    table_item = QTableWidgetItem(str(item))
                    if col == 3:  # 卷名列
                        table_item.setForeground(Qt.red)
                    self.table.setItem(row_pos, col, table_item)

    def edit_exam_paper(self, row):
        qid = int(self.table.item(row, 0).text())
        dialog = EditExamPaperDialog(qid)
        if dialog.exec_():
            self.load_data()

    def delete_exam_paper(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            qid = int(selected_items[0].text())
            try:
                delete_exam_paper(qid)
                QMessageBox.information(self, "成功", "套卷已删除！")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除套卷时出错: {e}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出套卷", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "年份", "完成日期", "卷名", "政治总数", "政治正确数", "常识总数", "常识正确数", "逻辑总数", "逻辑正确数", "片段总数", "片段正确数", "数量关系总数", "数量关系正确数", "图推总数", "图推正确数", "定义总数", "定义正确数", "类比总数", "类比正确数", "资料分析总数", "资料分析正确数", "总正确数", "总题量", "成绩"])
                for row in get_all_exam_papers():
                    writer.writerow(row)
            QMessageBox.information(self, "成功", "套卷已导出！")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入套卷", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过表头
                for row in reader:
                    add_exam_paper(
                        int(row[1]), row[2], row[3], int(row[4]), int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]), int(row[10]), int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15]), int(row[16]), int(row[17]), int(row[18]), int(row[19]), int(row[20]), int(row[21]), int(row[22]), int(row[23]), float(row[24])
                    )
            self.load_data()
            QMessageBox.information(self, "成功", "套卷已导入！")

class EditDialog(QDialog):
    def __init__(self, qid):
        super().__init__()
        self.qid = qid
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("编辑题目")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.module = QComboBox()
        self.module.addItems(["言语理解", "数量关系", "判断推理", "资料分析", "常识判断"])
        
        self.source = QLineEdit()
        self.content = QTextEdit()
        self.answer = QLineEdit()
        self.analysis = QTextEdit()
        self.question_type = QLineEdit()
        self.entry_time = QDateEdit()
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("题型模块:", self.module)
        form_layout.addRow("题目来源:", self.source)
        form_layout.addRow("题目内容:", self.content)
        form_layout.addRow("正确答案:", self.answer)
        form_layout.addRow("错题解析:", self.analysis)
        form_layout.addRow("题型:", self.question_type)
        form_layout.addRow("录入时间:", self.entry_time)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_data(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT module, source, content, answer, analysis, question_type, entry_time FROM questions WHERE id=?', (self.qid,))
            data = c.fetchone()
            self.module.setCurrentText(data[0])
            self.source.setText(data[1])
            self.content.setText(data[2])
            self.answer.setText(data[3])
            self.analysis.setText(data[4])
            self.question_type.setText(data[5])
            self.entry_time.setDate(QDate.fromString(data[6], "yyyy-MM-dd"))

    def save(self):
        try:
            update_question(
                self.qid,
                self.module.currentText(),
                self.source.text(),
                self.content.toPlainText(),
                self.answer.text(),
                self.analysis.toPlainText(),
                self.question_type.text(),
                self.entry_time.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "成功", "题目已更新！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新题目时出错: {e}")

class DetailDialog(QDialog):
    def __init__(self, qid):
        super().__init__()
        self.qid = qid
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("题目详情")
        layout = QVBoxLayout()
        
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        
        self.review_btn = QPushButton("标记复盘")
        self.review_btn.clicked.connect(self.mark_review)

        layout.addWidget(QLabel("题目内容:"))
        layout.addWidget(self.content)
        layout.addWidget(self.review_btn)
        self.setLayout(layout)

    def load_data(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT content FROM questions WHERE id=?', (self.qid,))
            self.content.setText(c.fetchone()[0])

    def mark_review(self):
        update_review(self.qid)
        QMessageBox.information(self, "成功", "已记录复盘！")
        self.accept()

class EditIdiomDialog(QDialog):
    def __init__(self, qid):
        super().__init__()
        self.qid = qid
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("编辑成语")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.category = QLineEdit()
        self.name = QLineEdit()
        self.meaning = QTextEdit()
        self.context = QTextEdit()
        self.collocation = QTextEdit()
        self.example = QTextEdit()
        self.entry_time = QDateEdit()
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("成语分类:", self.category)
        form_layout.addRow("成语名称:", self.name)
        form_layout.addRow("语义:", self.meaning)
        form_layout.addRow("常用语境:", self.context)
        form_layout.addRow("固定搭配:", self.collocation)
        form_layout.addRow("例句:", self.example)
        form_layout.addRow("录入时间:", self.entry_time)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_data(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT category, name, meaning, context, collocation, example, entry_time FROM idioms WHERE id=?', (self.qid,))
            data = c.fetchone()
            self.category.setText(data[0])
            self.name.setText(data[1])
            self.meaning.setText(data[2])
            self.context.setText(data[3])
            self.collocation.setText(data[4])
            self.example.setText(data[5])
            self.entry_time.setDate(QDate.fromString(data[6], "yyyy-MM-dd"))

    def save(self):
        try:
            update_idiom(
                self.qid,
                self.category.text(),
                self.name.text(),
                self.meaning.toPlainText(),
                self.context.toPlainText(),
                self.collocation.toPlainText(),
                self.example.toPlainText(),
                self.entry_time.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "成功", "成语已更新！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新成语时出错: {e}")

class ExamInputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.year = QLineEdit()
        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.paper_name = QLineEdit()
        self.politics_total = QLineEdit()  # 修改为 QLineEdit
        self.politics_correct = QLineEdit()  # 修改为 QLineEdit
        self.general_knowledge_total = QLineEdit()  # 修改为 QLineEdit
        self.general_knowledge_correct = QLineEdit()  # 修改为 QLineEdit
        self.logic_total = QLineEdit()  # 修改为 QLineEdit
        self.logic_correct = QLineEdit()  # 修改为 QLineEdit
        self.fragment_total = QLineEdit()  # 修改为 QLineEdit
        self.fragment_correct = QLineEdit()  # 修改为 QLineEdit
        self.quantitative_total = QLineEdit()  # 修改为 QLineEdit
        self.quantitative_correct = QLineEdit()  # 修改为 QLineEdit
        self.graphic_reasoning_total = QLineEdit()  # 修改为 QLineEdit
        self.graphic_reasoning_correct = QLineEdit()  # 修改为 QLineEdit
        self.definition_total = QLineEdit()  # 修改为 QLineEdit
        self.definition_correct = QLineEdit()  # 修改为 QLineEdit
        self.analogy_total = QLineEdit()  # 修改为 QLineEdit
        self.analogy_correct = QLineEdit()  # 修改为 QLineEdit
        self.data_analysis_total = QLineEdit()  # 修改为 QLineEdit
        self.data_analysis_correct = QLineEdit()  # 修改为 QLineEdit
        self.total_correct = QLineEdit()  # 修改为 QLineEdit
        self.total_questions = QLineEdit()  # 修改为 QLineEdit
        self.score = QLineEdit()  # 修改为 QLineEdit
        
        form_layout.addRow("年份:", self.year)
        form_layout.addRow("完成日期:", self.completion_date)
        form_layout.addRow("卷名:", self.paper_name)
        form_layout.addRow("政治总数:", self.politics_total)
        form_layout.addRow("政治正确数:", self.politics_correct)
        form_layout.addRow("常识总数:", self.general_knowledge_total)
        form_layout.addRow("常识正确数:", self.general_knowledge_correct)
        form_layout.addRow("逻辑总数:", self.logic_total)
        form_layout.addRow("逻辑正确数:", self.logic_correct)
        form_layout.addRow("片段总数:", self.fragment_total)
        form_layout.addRow("片段正确数:", self.fragment_correct)
        form_layout.addRow("数量关系总数:", self.quantitative_total)
        form_layout.addRow("数量关系正确数:", self.quantitative_correct)
        form_layout.addRow("图推总数:", self.graphic_reasoning_total)
        form_layout.addRow("图推正确数:", self.graphic_reasoning_correct)
        form_layout.addRow("定义总数:", self.definition_total)
        form_layout.addRow("定义正确数:", self.definition_correct)
        form_layout.addRow("类比总数:", self.analogy_total)
        form_layout.addRow("类比正确数:", self.analogy_correct)
        form_layout.addRow("资料分析总数:", self.data_analysis_total)
        form_layout.addRow("资料分析正确数:", self.data_analysis_correct)
        form_layout.addRow("总正确数:", self.total_correct)
        form_layout.addRow("总题量:", self.total_questions)
        form_layout.addRow("成绩:", self.score)
        
        submit_btn = QPushButton("保存套卷")
        submit_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(submit_btn)
        self.setLayout(layout)

    def save(self):
        try:
            new_id = add_exam_paper(
                int(self.year.text()),
                self.completion_date.date().toString("yyyy-MM-dd"),
                self.paper_name.text(),
                int(self.politics_total.text()),  # 转换为整数
                int(self.politics_correct.text()),  # 转换为整数
                int(self.general_knowledge_total.text()),  # 转换为整数
                int(self.general_knowledge_correct.text()),  # 转换为整数
                int(self.logic_total.text()),  # 转换为整数
                int(self.logic_correct.text()),  # 转换为整数
                int(self.fragment_total.text()),  # 转换为整数
                int(self.fragment_correct.text()),  # 转换为整数
                int(self.quantitative_total.text()),  # 转换为整数
                int(self.quantitative_correct.text()),  # 转换为整数
                int(self.graphic_reasoning_total.text()),  # 转换为整数
                int(self.graphic_reasoning_correct.text()),  # 转换为整数
                int(self.definition_total.text()),  # 转换为整数
                int(self.definition_correct.text()),  # 转换为整数
                int(self.analogy_total.text()),  # 转换为整数
                int(self.analogy_correct.text()),  # 转换为整数
                int(self.data_analysis_total.text()),  # 转换为整数
                int(self.data_analysis_correct.text()),  # 转换为整数
                int(self.total_correct.text()),  # 转换为整数
                int(self.total_questions.text()),  # 转换为整数
                float(self.score.text())  # 转换为浮点数
            )
            QMessageBox.information(self, "成功", "套卷已保存！")
            self.clear_fields()
            self.parentWidget().parentWidget().parentWidget().exam_review_tab.load_data()
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.critical(self, "错误", f"保存套卷时出错: {e}")

    def clear_fields(self):
        self.year.clear()
        self.completion_date.setDate(QDate.currentDate())
        self.paper_name.clear()
        self.politics_total.clear()
        self.politics_correct.clear()
        self.general_knowledge_total.clear()
        self.general_knowledge_correct.clear()
        self.logic_total.clear()
        self.logic_correct.clear()
        self.fragment_total.clear()
        self.fragment_correct.clear()
        self.quantitative_total.clear()
        self.quantitative_correct.clear()
        self.graphic_reasoning_total.clear()
        self.graphic_reasoning_correct.clear()
        self.definition_total.clear()
        self.definition_correct.clear()
        self.analogy_total.clear()
        self.analogy_correct.clear()
        self.data_analysis_total.clear()
        self.data_analysis_correct.clear()
        self.total_correct.clear()
        self.total_questions.clear()
        self.score.clear()

class EditExamPaperDialog(QDialog):
    def __init__(self, qid):
        super().__init__()
        self.qid = qid
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("编辑套卷")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.year = QLineEdit()
        self.completion_date = QDateEdit()
        self.completion_date.setCalendarPopup(True)
        self.paper_name = QLineEdit()
        self.politics_total = QSpinBox()
        self.politics_correct = QSpinBox()
        self.general_knowledge_total = QSpinBox()
        self.general_knowledge_correct = QSpinBox()
        self.logic_total = QSpinBox()
        self.logic_correct = QSpinBox()
        self.fragment_total = QSpinBox()
        self.fragment_correct = QSpinBox()
        self.quantitative_total = QSpinBox()
        self.quantitative_correct = QSpinBox()
        self.graphic_reasoning_total = QSpinBox()
        self.graphic_reasoning_correct = QSpinBox()
        self.definition_total = QSpinBox()
        self.definition_correct = QSpinBox()
        self.analogy_total = QSpinBox()
        self.analogy_correct = QSpinBox()
        self.data_analysis_total = QSpinBox()
        self.data_analysis_correct = QSpinBox()
        self.total_correct = QSpinBox()
        self.total_questions = QSpinBox()
        self.score = QDoubleSpinBox()
        
        form_layout.addRow("年份:", self.year)
        form_layout.addRow("完成日期:", self.completion_date)
        form_layout.addRow("卷名:", self.paper_name)
        form_layout.addRow("政治总数:", self.politics_total)
        form_layout.addRow("政治正确数:", self.politics_correct)
        form_layout.addRow("常识总数:", self.general_knowledge_total)
        form_layout.addRow("常识正确数:", self.general_knowledge_correct)
        form_layout.addRow("逻辑总数:", self.logic_total)
        form_layout.addRow("逻辑正确数:", self.logic_correct)
        form_layout.addRow("片段总数:", self.fragment_total)
        form_layout.addRow("片段正确数:", self.fragment_correct)
        form_layout.addRow("数量关系总数:", self.quantitative_total)
        form_layout.addRow("数量关系正确数:", self.quantitative_correct)
        form_layout.addRow("图推总数:", self.graphic_reasoning_total)
        form_layout.addRow("图推正确数:", self.graphic_reasoning_correct)
        form_layout.addRow("定义总数:", self.definition_total)
        form_layout.addRow("定义正确数:", self.definition_correct)
        form_layout.addRow("类比总数:", self.analogy_total)
        form_layout.addRow("类比正确数:", self.analogy_correct)
        form_layout.addRow("资料分析总数:", self.data_analysis_total)
        form_layout.addRow("资料分析正确数:", self.data_analysis_correct)
        form_layout.addRow("总正确数:", self.total_correct)
        form_layout.addRow("总题量:", self.total_questions)
        form_layout.addRow("成绩:", self.score)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_data(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''SELECT year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score 
                         FROM exam_papers WHERE id=?''', (self.qid,))
            data = c.fetchone()
            self.year.setText(str(data[0]))
            self.completion_date.setDate(QDate.fromString(data[1], "yyyy-MM-dd"))
            self.paper_name.setText(data[2])
            self.politics_total.setValue(data[3])
            self.politics_correct.setValue(data[4])
            self.general_knowledge_total.setValue(data[5])
            self.general_knowledge_correct.setValue(data[6])
            self.logic_total.setValue(data[7])
            self.logic_correct.setValue(data[8])
            self.fragment_total.setValue(data[9])
            self.fragment_correct.setValue(data[10])
            self.quantitative_total.setValue(data[11])
            self.quantitative_correct.setValue(data[12])
            self.graphic_reasoning_total.setValue(data[13])
            self.graphic_reasoning_correct.setValue(data[14])
            self.definition_total.setValue(data[15])
            self.definition_correct.setValue(data[16])
            self.analogy_total.setValue(data[17])
            self.analogy_correct.setValue(data[18])
            self.data_analysis_total.setValue(data[19])
            self.data_analysis_correct.setValue(data[20])
            self.total_correct.setValue(data[21])
            self.total_questions.setValue(data[22])
            self.score.setValue(data[23])

    def save(self):
        try:
            update_exam_paper(
                self.qid,
                int(self.year.text()),
                self.completion_date.date().toString("yyyy-MM-dd"),
                self.paper_name.text(),
                self.politics_total.value(),
                self.politics_correct.value(),
                self.general_knowledge_total.value(),
                self.general_knowledge_correct.value(),
                self.logic_total.value(),
                self.logic_correct.value(),
                self.fragment_total.value(),
                self.fragment_correct.value(),
                self.quantitative_total.value(),
                self.quantitative_correct.value(),
                self.graphic_reasoning_total.value(),
                self.graphic_reasoning_correct.value(),
                self.definition_total.value(),
                self.definition_correct.value(),
                self.analogy_total.value(),
                self.analogy_correct.value(),
                self.data_analysis_total.value(),
                self.data_analysis_correct.value(),
                self.total_correct.value(),
                self.total_questions.value(),
                self.score.value()
            )
            QMessageBox.information(self, "成功", "套卷已更新！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新套卷时出错: {e}")

class EssayInputTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.year = QLineEdit()
        self.province = QLineEdit()
        self.question_type = QLineEdit()
        self.source = QLineEdit()
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.content = QTextEdit()
        self.completion_status = QLineEdit()
        self.entry_time = QDateEdit()
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("年份:", self.year)
        form_layout.addRow("省份:", self.province)
        form_layout.addRow("题型:", self.question_type)
        form_layout.addRow("来源:", self.source)
        form_layout.addRow("日期:", self.date)
        form_layout.addRow("题目:", self.content)
        form_layout.addRow("完成情况:", self.completion_status)
        form_layout.addRow("录入时间:", self.entry_time)
        
        submit_btn = QPushButton("保存申论")
        submit_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(submit_btn)
        self.setLayout(layout)

    def save(self):
        try:
            new_id = add_essay_paper(
                int(self.year.text()),
                self.province.text(),
                self.question_type.text(),
                self.source.text(),
                self.date.date().toString("yyyy-MM-dd"),
                self.content.toPlainText(),
                self.completion_status.text(),
                self.entry_time.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "成功", "申论已保存！")
            self.year.clear()
            self.province.clear()
            self.question_type.clear()
            self.source.clear()
            self.date.setDate(QDate.currentDate())
            self.content.clear()
            self.completion_status.clear()
            self.entry_time.setDate(QDate.currentDate())
            self.parentWidget().parentWidget().parentWidget().essay_review_tab.load_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存申论时出错: {e}")

class EssayReviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("输入关键词筛选申论")
        self.filter_input.textChanged.connect(self.load_data)
        
        self.year_filter = QLineEdit()
        self.year_filter.setPlaceholderText("输入年份筛选")
        self.year_filter.textChanged.connect(self.load_data)
        
        self.province_filter = QLineEdit()
        self.province_filter.setPlaceholderText("输入省份筛选")
        self.province_filter.textChanged.connect(self.load_data)
        
        self.question_type_filter = QLineEdit()
        self.question_type_filter.setPlaceholderText("输入题型筛选")
        self.question_type_filter.textChanged.connect(self.load_data)
        
        self.source_filter = QLineEdit()
        self.source_filter.setPlaceholderText("输入来源筛选")
        self.source_filter.textChanged.connect(self.load_data)
        
        self.date_filter = QComboBox()
        self.date_filter.addItems(["全部时间", "选择日期"])
        self.date_filter.currentIndexChanged.connect(self.toggle_date_filter)  # 绑定筛选事件

        self.date_date = QDateEdit()
        self.date_date.setCalendarPopup(True)
        self.date_date.setDisplayFormat("yyyy-MM-dd")
        self.date_date.setVisible(False)
        self.date_date.dateChanged.connect(self.load_data)  # 绑定筛选事件
        
        filter_layout.addWidget(QLabel("关键词:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("年份:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("省份:"))
        filter_layout.addWidget(self.province_filter)
        filter_layout.addWidget(QLabel("题型:"))
        filter_layout.addWidget(self.question_type_filter)
        filter_layout.addWidget(QLabel("来源:"))
        filter_layout.addWidget(self.source_filter)
        filter_layout.addWidget(QLabel("日期:"))
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(self.date_date)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "年份", "省份", "题型", "来源", "日期", "题目", "完成情况", "录入时间"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.edit_essay_paper)
        
        delete_btn = QPushButton("删除申论")
        delete_btn.clicked.connect(self.delete_essay_paper)

        export_btn = QPushButton("导出申论")
        export_btn.clicked.connect(self.export_data)

        import_btn = QPushButton("导入申论")
        import_btn.clicked.connect(self.import_data)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(delete_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        self.setLayout(layout)

    def toggle_date_filter(self):
        if self.date_filter.currentText() == "选择日期":
            self.date_date.setVisible(True)
        else:
            self.date_date.setVisible(False)
            self.load_data()

    def load_data(self):
        filter_text = self.filter_input.text()
        selected_year = self.year_filter.text()
        selected_province = self.province_filter.text()
        selected_question_type = self.question_type_filter.text()
        selected_source = self.source_filter.text()
        selected_date = self.date_date.date().toString("yyyy-MM-dd") if self.date_filter.currentText() == "选择日期" else ""
        self.table.setRowCount(0)
        for row in get_all_essay_papers():
            if (selected_year == "" or str(row[1]) == selected_year) and \
               (selected_province == "" or row[2] == selected_province) and \
               (selected_question_type == "" or row[3] == selected_question_type) and \
               (selected_source == "" or row[4] == selected_source) and \
               (selected_date == "" or row[5] == selected_date) and \
               filter_text.lower() in str(row).lower():
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                for col, item in enumerate(row):
                    table_item = QTableWidgetItem(str(item))
                    if col == 6:  # 题目列
                        table_item.setForeground(Qt.red)
                    self.table.setItem(row_pos, col, table_item)

    def edit_essay_paper(self, row):
        qid = int(self.table.item(row, 0).text())
        dialog = EditEssayPaperDialog(qid)
        if dialog.exec_():
            self.load_data()

    def delete_essay_paper(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            qid = int(selected_items[0].text())
            try:
                delete_essay_paper(qid)
                QMessageBox.information(self, "成功", "申论已删除！")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除申论时出错: {e}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出申论", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "年份", "省份", "题型", "来源", "日期", "题目", "完成情况", "录入时间"])
                for row in get_all_essay_papers():
                    writer.writerow(row)
            QMessageBox.information(self, "成功", "申论已导出！")

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入申论", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过表头
                for row in reader:
                    add_essay_paper(
                        int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    )
            self.load_data()
            QMessageBox.information(self, "成功", "申论已导入！")

class EditEssayPaperDialog(QDialog):
    def __init__(self, qid):
        super().__init__()
        self.qid = qid
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("编辑申论")
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.year = QLineEdit()
        self.province = QLineEdit()
        self.question_type = QLineEdit()
        self.source = QLineEdit()
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.content = QTextEdit()
        self.completion_status = QLineEdit()
        self.entry_time = QDateEdit()
        self.entry_time.setCalendarPopup(True)
        
        form_layout.addRow("年份:", self.year)
        form_layout.addRow("省份:", self.province)
        form_layout.addRow("题型:", self.question_type)
        form_layout.addRow("来源:", self.source)
        form_layout.addRow("日期:", self.date)
        form_layout.addRow("题目:", self.content)
        form_layout.addRow("完成情况:", self.completion_status)
        form_layout.addRow("录入时间:", self.entry_time)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        
        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_data(self):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT year, province, question_type, source, date, content, completion_status, entry_time FROM essay_papers WHERE id=?', (self.qid,))
            data = c.fetchone()
            self.year.setText(str(data[0]))
            self.province.setText(data[1])
            self.question_type.setText(data[2])
            self.source.setText(data[3])
            self.date.setDate(QDate.fromString(data[4], "yyyy-MM-dd"))
            self.content.setText(data[5])
            self.completion_status.setText(data[6])
            self.entry_time.setDate(QDate.fromString(data[7], "yyyy-MM-dd"))

    def save(self):
        try:
            update_essay_paper(
                self.qid,
                int(self.year.text()),
                self.province.text(),
                self.question_type.text(),
                self.source.text(),
                self.date.date().toString("yyyy-MM-dd"),
                self.content.toPlainText(),
                self.completion_status.text(),
                self.entry_time.date().toString("yyyy-MM-dd")
            )
            QMessageBox.information(self, "成功", "申论已更新！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新申论时出错: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("行测错题管理系统")
        self.setGeometry(300, 300, 800, 600)
        
        self.tabs = QTabWidget()
        self.input_tab = InputTab()
        self.review_tab = ReviewTab()
        self.idiom_input_tab = IdiomInputTab()
        self.idiom_review_tab = IdiomReviewTab()
        self.exam_input_tab = ExamInputTab()
        self.exam_review_tab = ExamReviewTab()
        self.essay_input_tab = EssayInputTab()
        self.essay_review_tab = EssayReviewTab()
        self.tabs.addTab(self.input_tab, "题目录入")
        self.tabs.addTab(self.review_tab, "题目回顾")
        self.tabs.addTab(self.idiom_input_tab, "成语录入")
        self.tabs.addTab(self.idiom_review_tab, "成语回顾")
        self.tabs.addTab(self.exam_input_tab, "行测套卷录入")
        self.tabs.addTab(self.exam_review_tab, "行测套题回顾")
        self.tabs.addTab(self.essay_input_tab, "申论录入")
        self.tabs.addTab(self.essay_review_tab, "申论回顾")
        
        self.setCentralWidget(self.tabs)

        # 将 review_tab 和 idiom_review_tab 作为属性添加到 MainWindow
        self.review_tab = self.tabs.widget(1)
        self.idiom_review_tab = self.tabs.widget(3)
        self.exam_review_tab = self.tabs.widget(5)
        self.essay_review_tab = self.tabs.widget(7)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
