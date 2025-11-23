#!/usr/bin/env python3
"""
library_inventory_single.py

Single-file implementation of the "Library Inventory Manager" mini-project.
Contains:
 - Book class (dataclass) with issue/return/is_available/to_dict/from_dict
 - LibraryInventory class (manages Book objects, JSON persistence, logging)
 - Menu-driven CLI (Add, Issue, Return, View All, Search by title/ISBN, Exit)
 - Robust file handling (creates data folder, handles corrupted JSON)
 - Basic logging to library_manager/logs/library.log

Usage:
    python library_inventory_single.py

This file is self-contained and requires only Python 3.8+ standard library.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
import logging
import sys
import traceback

# -------------------------
# Book class
# -------------------------
@dataclass
class Book:
    title: str
    author: str
    isbn: str
    status: str = "available"  # "available" or "issued"

    def __post_init__(self):
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.isbn = self.isbn.strip()
        if self.status not in ("available", "issued"):
            self.status = "available"

    def __str__(self) -> str:
        return f"{self.title} — {self.author} (ISBN: {self.isbn}) [{self.status}]"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Book":
        return cls(
            title=d.get("title", "").strip(),
            author=d.get("author", "").strip(),
            isbn=d.get("isbn", "").strip(),
            status=d.get("status", "available").strip()
        )

    def issue(self) -> None:
        if self.status == "issued":
            raise ValueError("Book already issued.")
        self.status = "issued"

    def return_book(self) -> None:
        if self.status == "available":
            raise ValueError("Book is not issued.")
        self.status = "available"

    def is_available(self) -> bool:
        return self.status == "available"


# -------------------------
# LibraryInventory class
# -------------------------
class LibraryInventory:
    def __init__(self, json_path: Optional[Path] = None):
        # Determine json_path
        if json_path:
            self.json_path = Path(json_path)
        else:
            self.json_path = Path.cwd() / "data" / "books.json"

        # Ensure directories exist
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        # Logging setup
        self._setup_logging()
        self.books: List[Book] = []
        try:
            self.load()
            logging.getLogger(__name__).info(f"Loaded inventory from {self.json_path}")
        except Exception as e:
            logging.getLogger(__name__).exception(f"Failed to load inventory: {e}")
            # Continue with empty inventory

    def _setup_logging(self):
        log_dir = Path(__file__).parent / "library_manager" / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # fallback to local logs folder
            log_dir = Path.cwd() / "library_manager" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "library.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s"
        )
        # also configure a console handler for stderr (only warnings/errors)
        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)

    # --- CRUD operations ---
    def add_book(self, book: Book) -> None:
        if any(b.isbn == book.isbn for b in self.books):
            logging.getLogger(__name__).error(f"Attempted to add duplicate ISBN {book.isbn}")
            raise ValueError("Book with same ISBN already exists.")
        self.books.append(book)
        logging.getLogger(__name__).info(f"Added book: {book}")

    def search_by_title(self, title_substr: str) -> List[Book]:
        s = title_substr.strip().lower()
        results = [b for b in self.books if s in b.title.lower()]
        logging.getLogger(__name__).info(f"Searched by title '{title_substr}' -> {len(results)} results")
        return results

    def search_by_isbn(self, isbn: str) -> Optional[Book]:
        isbn = isbn.strip()
        for b in self.books:
            if b.isbn == isbn:
                logging.getLogger(__name__).info(f"Found book by ISBN {isbn}")
                return b
        logging.getLogger(__name__).info(f"No book found with ISBN {isbn}")
        return None

    def display_all(self) -> List[str]:
        reprs = [str(b) for b in self.books]
        logging.getLogger(__name__).info("Displayed all books")
        return reprs

    def issue_book_by_isbn(self, isbn: str) -> None:
        book = self.search_by_isbn(isbn)
        if not book:
            logging.getLogger(__name__).error(f"Attempted to issue nonexistent ISBN {isbn}")
            raise ValueError("Book not found.")
        if not book.is_available():
            logging.getLogger(__name__).error(f"Attempted to issue already issued book ISBN {isbn}")
            raise ValueError("Book already issued.")
        book.issue()
        self.save()
        logging.getLogger(__name__).info(f"Issued book ISBN {isbn}")

    def return_book_by_isbn(self, isbn: str) -> None:
        book = self.search_by_isbn(isbn)
        if not book:
            logging.getLogger(__name__).error(f"Attempted to return nonexistent ISBN {isbn}")
            raise ValueError("Book not found.")
        if book.is_available():
            logging.getLogger(__name__).error(f"Attempted to return available book ISBN {isbn}")
            raise ValueError("Book is not issued.")
        book.return_book()
        self.save()
        logging.getLogger(__name__).info(f"Returned book ISBN {isbn}")

    # --- Persistence ---
    def save(self) -> None:
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, indent=2, ensure_ascii=False)
            logging.getLogger(__name__).info(f"Saved inventory to {self.json_path}")
        except Exception:
            logging.getLogger(__name__).exception("Failed to save inventory.")
            raise

    def load(self) -> None:
        try:
            if not self.json_path.exists():
                # Create empty file
                self.books = []
                self.save()
                return
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Invalid JSON structure for books (expected list).")
            self.books = [Book.from_dict(item) for item in data]
            logging.getLogger(__name__).info(f"Loaded {len(self.books)} books from {self.json_path}")
        except json.JSONDecodeError:
            logging.getLogger(__name__).exception("JSON decoding error when loading inventory.")
            # Back up corrupted file
            corrupt_path = self.json_path.with_suffix(self.json_path.suffix + ".corrupt")
            try:
                self.json_path.rename(corrupt_path)
                logging.getLogger(__name__).error(f"Corrupted JSON moved to {corrupt_path}. Starting with empty inventory.")
            except Exception:
                logging.getLogger(__name__).exception("Failed to rename corrupted JSON file.")
            self.books = []
            try:
                self.save()
            except Exception:
                pass
        except FileNotFoundError:
            logging.getLogger(__name__).warning("books.json not found; starting with empty inventory.")
            self.books = []
            try:
                self.save()
            except Exception:
                pass
        except Exception:
            logging.getLogger(__name__).exception("Unexpected error while loading inventory.")
            raise


# -------------------------
# CLI utilities
# -------------------------
def prompt_nonempty(prompt_text: str) -> str:
    while True:
        try:
            s = input(prompt_text).strip()
        except EOFError:
            print()  # newline
            raise KeyboardInterrupt
        if s:
            return s
        print("Input cannot be empty. Please try again.")

def print_header():
    print("=" * 60)
    print("Library Inventory Manager (Single-file CLI)".center(60))
    print("=" * 60)

def cli_main():
    print_header()
    inv = LibraryInventory()
    MENU = """
Choose an option:
1. Add Book
2. Issue Book
3. Return Book
4. View All Books
5. Search by Title
6. Search by ISBN
7. Exit
"""
    while True:
        try:
            print(MENU)
            choice = input("Enter choice (1-7): ").strip()
            if choice == "1":
                title = prompt_nonempty("Title: ")
                author = prompt_nonempty("Author: ")
                isbn = prompt_nonempty("ISBN: ")
                try:
                    inv.add_book(Book(title=title, author=author, isbn=isbn))
                    inv.save()
                    print("Book added successfully.")
                except ValueError as ve:
                    print(f"Error: {ve}")

            elif choice == "2":
                isbn = prompt_nonempty("Enter ISBN to issue: ")
                try:
                    inv.issue_book_by_isbn(isbn)
                    print("Book issued.")
                except ValueError as ve:
                    print(f"Error: {ve}")

            elif choice == "3":
                isbn = prompt_nonempty("Enter ISBN to return: ")
                try:
                    inv.return_book_by_isbn(isbn)
                    print("Book returned.")
                except ValueError as ve:
                    print(f"Error: {ve}")

            elif choice == "4":
                entries = inv.display_all()
                if not entries:
                    print("No books in inventory.")
                else:
                    print("\nAll books:")
                    for e in entries:
                        print(" -", e)

            elif choice == "5":
                q = prompt_nonempty("Enter title (or part of it) to search: ")
                res = inv.search_by_title(q)
                if not res:
                    print("No matching books.")
                else:
                    print(f"{len(res)} result(s):")
                    for b in res:
                        print(" -", b)

            elif choice == "6":
                isbn = prompt_nonempty("Enter ISBN to search: ")
                b = inv.search_by_isbn(isbn)
                if b:
                    print(b)
                else:
                    print("Book not found.")

            elif choice == "7":
                print("Exiting. Goodbye!")
                break

            else:
                print("Invalid choice. Enter a number from 1 to 7.")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Exiting.")
            sys.exit(0)
        except Exception as e:
            # general safety net
            logging.getLogger(__name__).exception("Unhandled exception in CLI loop.")
            print(f"An unexpected error occurred: {e}")
            # Optionally show traceback for debug (comment out to be user-friendly)
            print(traceback.format_exc())

# -------------------------
# If run as script
# -------------------------
if __name__ == "__main__":
    try:
        cli_main()
    except Exception as e:
        # Ensure any top-level exception is logged
        logging.getLogger(__name__).exception("Fatal error in application.")
        print("A fatal error occurred. Check the log file for details.")
        sys.exit(1)