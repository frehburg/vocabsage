import sqlite3
import os
#import pandas as pd

class VocabularyDatabase:
    def __init__(self):
        self.db_name = 'data/db.sql'
        db_existed_before = os.path.exists(self.db_name)
        self.conn = sqlite3.connect(self.db_name)

        if not db_existed_before:
            self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Books (
                Book_ID INTEGER PRIMARY KEY,
                name VARCHAR(25) UNIQUE,
                language1 VARCHAR(25),
                language2 VARCHAR(25),
                description VARCHAR(255) NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Vocabulary (
                Vocab_ID INTEGER PRIMARY KEY,
                Book_ID INTEGER,
                vocab_language1 VARCHAR(50),
                vocab_language2 VARCHAR(50),
                definition VARCHAR(255) NULL,
                FOREIGN KEY (Book_ID) REFERENCES Books (Book_ID)
            )
        ''')
        self.conn.commit()

    def add_book(self, name, language1, language2, description=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO Books (name, language1, language2, description) VALUES (?, ?, ?, ?)',
            (name, language1, language2, description))
        self.conn.commit()


    def get_book_id(self, book_name):
        # Get the Book_ID of the given book_name
        cursor = self.conn.cursor()
        cursor.execute('''SELECT Book_ID FROM Books WHERE name = ?''', (book_name,))
        book_id = cursor.fetchone()[0]
        print(f'Book ID for {book_name}: {book_id}')
        return book_id

    def add_vocab(self, book_name, vocab_language1, vocab_language2, definition=''):
        book_id = self.get_book_id(book_name)
        cursor = self.conn.cursor()

        if book_id:
            # Insert the vocabulary into the Vocabulary table
            cursor.execute('''
                INSERT INTO Vocabulary (Book_ID, vocab_language1, vocab_language2, definition)
                VALUES (?, ?, ?, ?)
            ''', (book_id, vocab_language1, vocab_language2, definition))
            self.conn.commit()
            print("Vocabulary added successfully.")
        else:
            print("Book not found.")

    def query_by_vocab(self, book_name, vocab_term):
        cursor = self.conn.cursor()
        book_id = self.get_book_id(book_name)
        cursor.execute('''
            SELECT vocab_language1, vocab_language2, definition
            FROM Vocabulary
            WHERE Book_ID = ? AND (vocab_language1 LIKE ? OR vocab_language2 LIKE ?)
        ''', (book_id, f'%{vocab_term}%', f'%{vocab_term}%'))

        results = cursor.fetchall()

        cursor.execute('''SELECT language1, language2, 'Definition' AS definition FROM Books WHERE Book_ID = ?''', (book_id,))
        column_names = cursor.fetchall()

        return self.results_to_df(column_names, results)


    def results_to_df(self, column_names, results):
        print(f'Column names: {list(column_names[0])}')
        return results


    def close(self):
        self.conn.close()

if __name__ == '__main__':
    db = VocabularyDatabase()

    db.add_book('ENSP', 'English', 'Spanish', 'Spanish Class Madrid B1')
    db.add_vocab('ENSP', 'apple', 'manzana')
    db.add_vocab('ENSP', 'thisiswrong', 'manzana')
    db.add_vocab('ENSP', 'penapple', 'bolimanzana')
    db.add_vocab('ENSP', 'applepen', 'manzanaboli')
    db.add_vocab('ENSP', 'banana apple', 'plátano manzana')
    db.add_vocab('ENSP', 'dog', 'perro')

    results = db.query_by_vocab('ENSP', 'man')
    if results:
        print(f'Results for "manzana":')
        for result in results:
            print(result)
    else:
        print(f'No results found for "manzana"')

    db.close()
