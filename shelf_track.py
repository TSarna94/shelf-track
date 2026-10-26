# Academic Honesty Statement:
# I confirm that this code is my own work. I received guidance on concepts,
# debugging, and best practices, but all writing, structuring, and implementation
# decisions were done by me. I understand the academic integrity policies and
# take full responsibility for this submission.

# Shelf Track - Bookstore Inventory System
# Features:
# - Full CRUD for books and authors
# - Relational database using SQLite
# - INNER JOIN reporting and enhanced search
# - Menu-driven CLI application

import sqlite3

DB_NAME = "ebookstore.db"


# --- Database helper functions ---


def get_connection():
    """Return a SQLite connection with foreign key support enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create the book table if it does not already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                authorID INTEGER NOT NULL,
                qty INTEGER NOT NULL
            )
        ''')


def populate_books():
    """Insert initial sample book records into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        books = [
            (3001, "A Tale of Two Cities", 1290, 30),
            (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
            (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
            (3004, "The Lord of the Rings", 6380, 37),
            (3005, "Alice's Adventures in Wonderland", 5620, 12)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO book VALUES (?, ?, ?, ?)",
            books
        )


def create_author_table():
    """Create the author table if it does not already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS author (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL
            )
        ''')


def populate_authors():
    """Insert initial sample author records into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        authors = [
            (1290, "Charles Dickens", "England"),
            (8937, "J.K. Rowling", "England"),
            (2356, "C.S. Lewis", "Ireland"),
            (6380, "J.R.R. Tolkien", "South Africa"),
            (5620, "Lewis Carroll", "England")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO author VALUES (?, ?, ?)",
            authors
        )


# --- CRUD functions ---


def enter_book():
    """Add a new book to the database."""
    book_id = input("Enter the 4-digit book ID: ").strip()

    if not (book_id.isdigit() and len(book_id) == 4):
        print("Book ID must be a 4-digit number.")
        return

    title = input("Enter book title: ").strip()
    author_id = input("Enter the 4-digit author ID: ").strip()

    if not (author_id.isdigit() and len(author_id) == 4):
        print("Author ID must be a 4-digit number.")
        return

    qty = input("Enter quantity: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM author WHERE id = ?", (author_id,))
        author_exists = cursor.fetchone()

        if not author_exists:
            print("Author ID does not exist. Please add the author first.")
            return

        cursor.execute(
            "INSERT INTO book (id, title, authorID, qty) VALUES (?, ?, ?, ?)",
            (book_id, title, author_id, qty)
        )
        print("\nBook added successfully.")


def update_book():
    """Update an existing book's details in the database."""
    print("\n--- Update Book ---")
    book_id = input("Enter book ID to update: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found.")
            return

        print(f"Current title: {book[1]}")
        print(f"Current author ID: {book[2]}")
        print(f"Current quantity: {book[3]}")

        print("\nWhat would you like to update?")
        print("1. Title")
        print("2. Author Details")
        print("3. Quantity")
        print("4. Assign a new Author ID")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            new_title = input("Enter new title: ").strip()
            cursor.execute(
                "UPDATE book SET title = ? WHERE id = ?",
                (new_title, book_id)
            )
            print("Title updated successfully.")

        elif choice == "2":
            cursor.execute("""
                SELECT author.id, author.name, author.country
                FROM author
                INNER JOIN book ON author.id = book.authorID
                WHERE book.id = ?
            """, (book_id,))
            author = cursor.fetchone()

            if not author:
                print("Author not found for this book.")
                return

            author_id, current_name, current_country = author

            print("\nCurrent Author Details:")
            print(f"Name: {current_name}")
            print(f"Country: {current_country}")

            new_name = input("Enter new author name (leave blank to keep current): ").strip()
            new_country = input("Enter new author country (leave blank to keep current): ").strip()

            if new_name == "":
                new_name = current_name
            if new_country == "":
                new_country = current_country

            cursor.execute("""
                UPDATE author
                SET name = ?, country = ?
                WHERE id = ?
            """, (new_name, new_country, author_id))

            conn.commit()
            print("\nAuthor details updated successfully.")

        elif choice == "3":
            new_qty = input("Enter new quantity: ").strip()
            cursor.execute(
                "UPDATE book SET qty = ? WHERE id = ?",
                (new_qty, book_id)
            )
            print("Quantity updated successfully.")

        elif choice == "4":
            new_author_id = input("Enter the new 4-digit author ID: ").strip()

            if not (new_author_id.isdigit() and len(new_author_id) == 4):
                print("Author ID must be a 4-digit number.")
                return

            cursor.execute("SELECT * FROM author WHERE id = ?", (new_author_id,))
            author_exists = cursor.fetchone()

            if not author_exists:
                print("Author ID does not exist. Please add the author first.")
                return

            cursor.execute(
                "UPDATE book SET authorID = ? WHERE id = ?",
                (new_author_id, book_id)
            )

            conn.commit()
            print("Author ID updated successfully.")

        else:
            print("Invalid choice.")


def delete_book():
    """Delete a book from the database."""
    print("\n--- Delete Book ---")
    book_id = input("Enter book ID to delete: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found.")
            return

        print(
            f"\nBook found: {book[1]} by (Author ID {book[2]}, "
            f"Qty: {book[3]})"
        )
        confirm = input("Are you sure you want to delete this book? (y/n): ").strip().lower()

        if confirm == "y":
            cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
            print("Book deleted successfully.")
        else:
            print("Deletion cancelled.")


def search_books():
    """Search for books in the database by ID, title, or author ID."""
    print("\n--- Search Books ---")
    print("Search by:")
    print("1. Book ID")
    print("2. Title")
    print("3. Author ID")

    choice = input("Enter choice: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()

        if choice == "1":
            book_id = input("Enter book ID: ").strip()
            cursor.execute("SELECT * FROM book WHERE id = ?", (book_id,))
            results = cursor.fetchall()

        elif choice == "2":
            title = input("Enter title (or part of it): ").strip()
            cursor.execute(
                "SELECT * FROM book WHERE title LIKE ?",
                ('%' + title + '%',)
            )
            results = cursor.fetchall()

        elif choice == "3":
            author_id = input("Enter author ID: ").strip()
            cursor.execute("SELECT * FROM book WHERE authorID = ?", (author_id,))
            results = cursor.fetchall()

        else:
            print("Invalid choice.")
            return

        if results:
            print("\nSearch Results:")
            for book in results:
                print(
                    f"ID: {book[0]}, Title: {book[1]}, "
                    f"Author ID: {book[2]}, Quantity: {book[3]}"
                )
        else:
            print("No books found matching the criteria.")


def add_author():
    """Add a new author to the database."""
    print("\n--- Add Author ---")
    author_id = input("Enter new author ID: ").strip()
    name = input("Enter author name: ").strip()
    country = input("Enter author country: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
            (author_id, name, country)
        )
        print("Author added successfully.")


def update_author():
    """Update an existing author's details in the database."""
    print("\n--- Update Author ---")
    author_id = input("Enter author ID to update: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM author WHERE id = ?", (author_id,))
        author = cursor.fetchone()

        if not author:
            print("Author not found.")
            return

        print(f"Current name: {author[1]}")
        print(f"Current country: {author[2]}")

        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. Country")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            new_name = input("Enter new name: ").strip()
            cursor.execute(
                "UPDATE author SET name = ? WHERE id = ?",
                (new_name, author_id)
            )
            print("Name updated successfully.")

        elif choice == "2":
            new_country = input("Enter new country: ").strip()
            cursor.execute(
                "UPDATE author SET country = ? WHERE id = ?",
                (new_country, author_id)
            )
            print("Country updated successfully.")

        else:
            print("Invalid choice.")


def delete_author():
    """Delete an author from the database."""
    print("\n--- Delete Author ---")
    author_id = input("Enter author ID to delete: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM author WHERE id = ?", (author_id,))
        author = cursor.fetchone()

        if not author:
            print("Author not found.")
            return

        print(f"\nAuthor found: {author[1]} ({author[2]})")
        confirm = input("Delete this author? (y/n): ").strip().lower()

        if confirm == "y":
            cursor.execute("DELETE FROM author WHERE id = ?", (author_id,))
            print("Author deleted successfully.")
        else:
            print("Deletion cancelled.")


# --- REPORTING functions ---


def view_inventory_report():
    """View a full inventory report of books along with their authors."""
    print("\n--- Full Inventory Report (Books + Authors) ---")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                book.id,
                book.title,
                author.name,
                author.country,
                book.qty
            FROM book
            INNER JOIN author
            ON book.authorID = author.id
            ORDER BY book.id;
        ''')
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"\nID: {row[0]}")
                print(f"Title: {row[1]}")
                print(f"Author: {row[2]}")
                print(f"Country: {row[3]}")
                print(f"Quantity: {row[4]}")
        else:
            print("No inventory data found.")


def search_books_with_author():
    """Search for books and display their author information."""
    print("\n--- Search Books (With Author Info) ---")
    print("Search by:")
    print("1. Book ID")
    print("2. Title")
    print("3. Author Name")

    choice = input("Enter choice: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()

        if choice == "1":
            book_id = input("Enter book ID: ").strip()
            cursor.execute('''
                SELECT book.id, book.title, author.name, author.country, book.qty
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE book.id = ?
            ''', (book_id,))
            results = cursor.fetchall()

        elif choice == "2":
            title = input("Enter title (or part of it): ").strip()
            cursor.execute('''
                SELECT book.id, book.title, author.name, author.country, book.qty
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE book.title LIKE ?
            ''', ('%' + title + '%',))
            results = cursor.fetchall()

        elif choice == "3":
            author_name = input("Enter author name (or part of it): ").strip()
            cursor.execute('''
                SELECT book.id, book.title, author.name, author.country, book.qty
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE author.name LIKE ?
            ''', ('%' + author_name + '%',))
            results = cursor.fetchall()

        else:
            print("Invalid choice.")
            return

        if results:
            print("\nSearch Results:")
            for row in results:
                print(f"\nID: {row[0]}")
                print(f"Title: {row[1]}")
                print(f"Author: {row[2]}")
                print(f"Country: {row[3]}")
                print(f"Quantity: {row[4]}")
        else:
            print("No matching books found.")


def view_all_authors():
    """View all authors in the database."""
    print("\n--- All Authors ---")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, country FROM author ORDER BY id")
        results = cursor.fetchall()

        if results:
            for author in results:
                print(f"\nAuthor ID: {author[0]}")
                print(f"Name: {author[1]}")
                print(f"Country: {author[2]}")
        else:
            print("No authors found.")


# --- Menu printing ---


def print_menu():
    """Print the main menu options."""
    print("\nShelf Track - Bookstore Inventory")
    print("1. Enter book")
    print("2. Update book")
    print("3. Delete book")
    print("4. Search books")
    print("5. View full inventory report")
    print("6. Search books (with author info)")
    print("7. View all authors")
    print("8. Add author")
    print("9. Update author")
    print("10. Delete author")
    print("0. Exit")


# --- Main loop ---


def main():
    """Main function to run the Shelf Track application."""
    create_tables()
    populate_books()
    create_author_table()
    populate_authors()

    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            enter_book()

        elif choice == "2":
            update_book()

        elif choice == "3":
            delete_book()

        elif choice == "4":
            search_books()

        elif choice == "5":
            view_inventory_report()

        elif choice == "6":
            search_books_with_author()

        elif choice == "7":
            view_all_authors()

        elif choice == "8":
            add_author()

        elif choice == "9":
            update_author()

        elif choice == "10":
            delete_author()

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

# End of program
