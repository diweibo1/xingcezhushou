import sqlite3
import os
from datetime import datetime

DB_PATH = 'question_data.db'

# 删除现有的数据库文件
# if os.path.exists(DB_PATH):
#     os.remove(DB_PATH)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      module TEXT NOT NULL,
                      source TEXT NOT NULL,
                      content TEXT NOT NULL,
                      answer TEXT NOT NULL,
                      analysis TEXT,
                      question_type TEXT,
                      reviews INTEGER DEFAULT 0,
                      create_time DATETIME,
                      entry_time DATETIME)''')  # 添加 entry_time 字段
        c.execute('''CREATE TABLE IF NOT EXISTS idioms
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      category TEXT NOT NULL,
                      name TEXT NOT NULL UNIQUE,
                      meaning TEXT NOT NULL,
                      context TEXT,
                      collocation TEXT,
                      example TEXT,
                      create_time DATETIME,
                      entry_time DATETIME)''')  # 添加 entry_time 字段
        c.execute('''CREATE TABLE IF NOT EXISTS exam_papers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      year INTEGER NOT NULL,
                      completion_date DATETIME NOT NULL,
                      paper_name TEXT NOT NULL,
                      politics_total INTEGER,
                      politics_correct INTEGER,
                      general_knowledge_total INTEGER,
                      general_knowledge_correct INTEGER,
                      logic_total INTEGER,
                      logic_correct INTEGER,
                      fragment_total INTEGER,
                      fragment_correct INTEGER,
                      quantitative_total INTEGER,
                      quantitative_correct INTEGER,
                      graphic_reasoning_total INTEGER,
                      graphic_reasoning_correct INTEGER,
                      definition_total INTEGER,
                      definition_correct INTEGER,
                      analogy_total INTEGER,
                      analogy_correct INTEGER,
                      data_analysis_total INTEGER,
                      data_analysis_correct INTEGER,
                      total_correct INTEGER,
                      total_questions INTEGER,
                      score REAL,
                      create_time DATETIME)''')
        c.execute('''CREATE TABLE IF NOT EXISTS essay_papers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      year INTEGER NOT NULL,
                      province TEXT NOT NULL,
                      question_type TEXT NOT NULL,
                      source TEXT NOT NULL,
                      date DATETIME NOT NULL,
                      content TEXT NOT NULL,
                      completion_status TEXT NOT NULL,
                      entry_time DATETIME)''')
        conn.commit()

def get_all_questions():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, module, source, content, answer, reviews, question_type, entry_time FROM questions ORDER BY create_time DESC')  # 确保返回 entry_time 字段
        return c.fetchall()

def add_question(module, source, content, answer, analysis, question_type, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO questions 
                     (module, source, content, answer, analysis, question_type, create_time, entry_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (module, source, content, answer, analysis, question_type, datetime.now(), entry_time))  # 添加 entry_time
        conn.commit()  # 确保提交事务
        return c.lastrowid  # 返回新插入记录的ID

def update_question(qid, module, source, content, answer, analysis, question_type, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''UPDATE questions 
                     SET module = ?, source = ?, content = ?, answer = ?, analysis = ?, question_type = ?, entry_time = ?
                     WHERE id = ?''',
                  (module, source, content, answer, analysis, question_type, entry_time, qid))
        conn.commit()

def update_review(qid):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('UPDATE questions SET reviews = reviews + 1 WHERE id = ?', (qid,))
        conn.commit()

def delete_question(qid):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM questions WHERE id = ?', (qid,))
        conn.commit()

def get_all_sources():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT source FROM questions')
        return [row[0] for row in c.fetchall()]

def add_idiom(category, name, meaning, context, collocation, example, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO idioms 
                     (category, name, meaning, context, collocation, example, create_time, entry_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (category, name, meaning, context, collocation, example, datetime.now(), entry_time))  # 添加 entry_time
        conn.commit()  # 确保提交事务
        return c.lastrowid  # 返回新插入记录的ID

def update_idiom(qid, category, name, meaning, context, collocation, example, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''UPDATE idioms 
                     SET category = ?, name = ?, meaning = ?, context = ?, collocation = ?, example = ?, entry_time = ?
                     WHERE id = ?''',
                  (category, name, meaning, context, collocation, example, entry_time, qid))
        conn.commit()

def get_all_idioms():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM idioms ORDER BY create_time DESC')
        return c.fetchall()

def delete_idiom(qid):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM idioms WHERE id = ?', (qid,))
        conn.commit()

def check_duplicate_idiom(name):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM idioms WHERE name = ?', (name,))
        return c.fetchone()[0] > 0

def add_exam_paper(year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO exam_papers 
                     (year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score, create_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score, datetime.now()))
        conn.commit()
        return c.lastrowid  # 返回新插入记录的ID

def update_exam_paper(qid, year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''UPDATE exam_papers 
                     SET year = ?, completion_date = ?, paper_name = ?, politics_total = ?, politics_correct = ?, general_knowledge_total = ?, general_knowledge_correct = ?, logic_total = ?, logic_correct = ?, fragment_total = ?, fragment_correct = ?, quantitative_total = ?, quantitative_correct = ?, graphic_reasoning_total = ?, graphic_reasoning_correct = ?, definition_total = ?, definition_correct = ?, analogy_total = ?, analogy_correct = ?, data_analysis_total = ?, data_analysis_correct = ?, total_correct = ?, total_questions = ?, score = ?
                     WHERE id = ?''',
                  (year, completion_date, paper_name, politics_total, politics_correct, general_knowledge_total, general_knowledge_correct, logic_total, logic_correct, fragment_total, fragment_correct, quantitative_total, quantitative_correct, graphic_reasoning_total, graphic_reasoning_correct, definition_total, definition_correct, analogy_total, analogy_correct, data_analysis_total, data_analysis_correct, total_correct, total_questions, score, qid))
        conn.commit()

def get_all_exam_papers():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM exam_papers ORDER BY create_time DESC')
        return c.fetchall()

def delete_exam_paper(qid):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM exam_papers WHERE id = ?', (qid,))
        conn.commit()

def add_essay_paper(year, province, question_type, source, date, content, completion_status, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO essay_papers 
                     (year, province, question_type, source, date, content, completion_status, entry_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (year, province, question_type, source, date, content, completion_status, entry_time))
        conn.commit()
        return c.lastrowid

def update_essay_paper(qid, year, province, question_type, source, date, content, completion_status, entry_time):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''UPDATE essay_papers 
                     SET year = ?, province = ?, question_type = ?, source = ?, date = ?, content = ?, completion_status = ?, entry_time = ?
                     WHERE id = ?''',
                  (year, province, question_type, source, date, content, completion_status, entry_time, qid))
        conn.commit()

def get_all_essay_papers():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM essay_papers ORDER BY entry_time DESC')
        return c.fetchall()

def delete_essay_paper(qid):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM essay_papers WHERE id = ?', (qid,))
        conn.commit()
