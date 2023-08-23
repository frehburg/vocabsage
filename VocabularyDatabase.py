import sqlite3
import os
import pandas as pd

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
        print(f'Book {name} added successfully.')


    def get_book_id(self, book_name):
        # Get the Book_ID of the given book_name
        cursor = self.conn.cursor()
        cursor.execute('''SELECT Book_ID FROM Books WHERE name = ?''', (book_name,))
        book_id = cursor.fetchone()[0]
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
            print(f'Vocabulary ({vocab_language1} - {vocab_language2}) added successfully to {book_name}.')
        else:
            print('Book not found.')

    def query_by_vocab(self, book_name, vocab_term):
        cursor = self.conn.cursor()
        book_id = self.get_book_id(book_name)
        cursor.execute('''
            SELECT Vocab_ID, vocab_language1, vocab_language2, definition
            FROM Vocabulary
            WHERE Book_ID = ? AND (vocab_language1 LIKE ? OR vocab_language2 LIKE ?)
        ''', (book_id, f'%{vocab_term}%', f'%{vocab_term}%'))

        results = cursor.fetchall()

        cursor.execute('''SELECT 'Vocab_ID', language1, language2, 'Definition' FROM Books WHERE Book_ID = ?''', (book_id,))
        column_names = cursor.fetchall()

        return self.results_to_df(column_names, results)


    def results_to_df(self, column_names=[], results=[], verbose=True):
        if not len(column_names) == 0:
            column_names = column_names[0]
        else:
            column_names = [f'Column {i}' for i in range(len(results[0]))]

        df = pd.DataFrame(results, columns=column_names)
        if verbose:
            if results:
                print(df.to_string(index=False))
            else:
                print("No results found.")
        return results


    def get_books(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT Book_ID, name, language1, language2 FROM Books''')
        books = cursor.fetchall()
        return self.results_to_df(results=books)


    def close(self):
        self.conn.close()

def main():
    last_book_name = ''

    db = VocabularyDatabase()

    commands = '\n - ADD - [vocab_language1] - [vocab_language2] - [definition] {Puts into last used book}' \
               '\n - ADDD - [BookName] - [vocab_language1] - [vocab_language2] - [definition] \n - Q [BookName] [vocab] ' \
               '\n - QBOOKS \n - ADDBOOK [BookName] [language1] [language2] [description] \n - EXIT \n - HELP '
    first = True
    while True:
        if first:
            command = input(
                '\nEnter one of the following commands: ' + commands + '\n').strip()
            first = False
        else:
            command = input('\nEnter a command, or type HELP for a list of commands. \n').strip()
        parts = command.split()

        if parts[0] == 'ADD' and len(parts) >= 4:
            input_data = ' '.join(parts[1:])  # Combine all parts except the command
            parts = [p.strip() for p in input_data.split('-')]

            book_name = last_book_name
            vocab_language1 = parts[1]
            vocab_language2 = parts[2]
            definition = ' '.join(parts[3:])
            db.add_vocab(book_name, vocab_language1, vocab_language2, definition)

        elif parts[0] == 'ADDD' and len(parts) >= 5:
            input_data = ' '.join(parts[1:])  # Combine all parts except the command
            parts = [p.strip() for p in input_data.split('-')]

            book_name = parts[1]
            vocab_language1 = parts[2]
            vocab_language2 = parts[3]
            definition = ' '.join(parts[4:])
            db.add_vocab(book_name, vocab_language1, vocab_language2, definition)
            last_book_name = book_name

        elif parts[0] == 'QBOOKS':
            db.get_books()

        elif parts[0] == 'Q' and len(parts) >= 3:
            book_name = parts[1]
            vocab = parts[2]
            db.query_by_vocab(book_name, vocab)

        elif parts[0] == 'ADDBOOK' and len(parts) >= 5:
            book_name = parts[1]
            language1 = parts[2]
            language2 = parts[3]
            description = ' '.join(parts[4:])
            db.add_book(book_name, language1, language2, description)

        elif parts[0] == 'HELP':
            print(commands)

        elif parts[0] == 'EXIT':
            db.close()
            print('Exiting...')
            break

        else:
            print('Invalid command. Type HELP for a list of commands. \n')


if __name__ == "__main__":
    main()
