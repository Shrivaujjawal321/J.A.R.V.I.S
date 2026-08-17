"""
Library Management System
==========================
Ek simple terminal-based library jisme aap books aur members manage kar sakte ho.
Data ek JSON file me save hota hai, isliye program band karke dobara kholne par
bhi sab kuch yaad rehta hai.
"""

import json
import os
from datetime import datetime

# Jis file me data save hoga (program ke saath hi ban jaati hai)
DATA_FILE = os.path.join(os.path.dirname(__file__), "library_data.json")


# ----------------------------------------------------------------------
# 1. BOOK  --> ek kitaab ka blueprint
# ----------------------------------------------------------------------
class Book:
    def __init__(self, book_id, title, author, total_copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.available_copies = total_copies  # shuru me sab copies available

    def to_dict(self):
        """Object ko dictionary me badalta hai taaki JSON me save ho sake."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    @staticmethod
    def from_dict(data):
        """Dictionary se wapas Book object banata hai (file se load karte waqt)."""
        book = Book(data["book_id"], data["title"], data["author"], data["total_copies"])
        book.available_copies = data["available_copies"]
        return book


# ----------------------------------------------------------------------
# 2. MEMBER  --> ek member ka blueprint
# ----------------------------------------------------------------------
class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self.borrowed_books = []  # is member ne kaun si book_id li hui hai

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "borrowed_books": self.borrowed_books,
        }

    @staticmethod
    def from_dict(data):
        member = Member(data["member_id"], data["name"])
        member.borrowed_books = data["borrowed_books"]
        return member


# ----------------------------------------------------------------------
# 3. LIBRARY  --> dimaag (saara logic yahin hai)
# ----------------------------------------------------------------------
class Library:
    def __init__(self):
        self.books = {}    # { book_id : Book }
        self.members = {}  # { member_id : Member }
        self.transactions = []  # issue/return ka history
        self.load()

    # ---------- File save / load ----------
    def save(self):
        data = {
            "books": [b.to_dict() for b in self.books.values()],
            "members": [m.to_dict() for m in self.members.values()],
            "transactions": self.transactions,
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(DATA_FILE):
            return  # pehli baar chalaya hai, kuch save nahi hai
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        self.books = {b["book_id"]: Book.from_dict(b) for b in data.get("books", [])}
        self.members = {m["member_id"]: Member.from_dict(m) for m in data.get("members", [])}
        self.transactions = data.get("transactions", [])

    # ---------- Book operations ----------
    def add_book(self, book_id, title, author, copies):
        if book_id in self.books:
            # Pehle se hai to sirf copies badha do
            self.books[book_id].total_copies += copies
            self.books[book_id].available_copies += copies
            print(f"✓ '{title}' ki {copies} aur copies add ho gayi.")
        else:
            self.books[book_id] = Book(book_id, title, author, copies)
            print(f"✓ Nayi book add ho gayi: '{title}' by {author}.")
        self.save()

    def remove_book(self, book_id):
        if book_id in self.books:
            removed = self.books.pop(book_id)
            print(f"✓ Book hata di: '{removed.title}'.")
            self.save()
        else:
            print("✗ Aisi koi book ID nahi mili.")

    # ---------- Member operations ----------
    def add_member(self, member_id, name):
        if member_id in self.members:
            print("✗ Ye member ID pehle se exist karti hai.")
            return
        self.members[member_id] = Member(member_id, name)
        print(f"✓ Member add ho gaya: {name}.")
        self.save()

    # ---------- Issue / Return ----------
    def issue_book(self, book_id, member_id):
        if book_id not in self.books:
            print("✗ Book nahi mili.")
            return
        if member_id not in self.members:
            print("✗ Member nahi mila.")
            return

        book = self.books[book_id]
        member = self.members[member_id]

        if book.available_copies <= 0:
            print(f"✗ '{book.title}' ki koi copy available nahi hai abhi.")
            return

        book.available_copies -= 1
        member.borrowed_books.append(book_id)
        self.transactions.append({
            "type": "issue",
            "book_id": book_id,
            "member_id": member_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        print(f"✓ '{book.title}' issue ho gayi {member.name} ko.")
        self.save()

    def return_book(self, book_id, member_id):
        if member_id not in self.members:
            print("✗ Member nahi mila.")
            return
        member = self.members[member_id]
        if book_id not in member.borrowed_books:
            print("✗ Is member ne ye book nahi li thi.")
            return

        member.borrowed_books.remove(book_id)
        self.books[book_id].available_copies += 1
        self.transactions.append({
            "type": "return",
            "book_id": book_id,
            "member_id": member_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        print(f"✓ '{self.books[book_id].title}' wapas ho gayi.")
        self.save()

    # ---------- Views ----------
    def list_books(self):
        if not self.books:
            print("(Library khaali hai — koi book nahi.)")
            return
        print(f"\n{'ID':<6}{'Title':<30}{'Author':<20}{'Avail/Total'}")
        print("-" * 70)
        for b in self.books.values():
            print(f"{b.book_id:<6}{b.title:<30}{b.author:<20}{b.available_copies}/{b.total_copies}")

    def list_members(self):
        if not self.members:
            print("(Koi member nahi.)")
            return
        print(f"\n{'ID':<6}{'Name':<25}{'Books Borrowed'}")
        print("-" * 50)
        for m in self.members.values():
            print(f"{m.member_id:<6}{m.name:<25}{len(m.borrowed_books)}")

    def search_books(self, keyword):
        keyword = keyword.lower()
        found = [b for b in self.books.values()
                 if keyword in b.title.lower() or keyword in b.author.lower()]
        if not found:
            print("Kuch nahi mila.")
            return
        for b in found:
            print(f"  [{b.book_id}] {b.title} — {b.author} ({b.available_copies} available)")


# ----------------------------------------------------------------------
# 4. MENU  --> user se baat-cheet (CLI)
# ----------------------------------------------------------------------
def menu():
    lib = Library()
    actions = """
========= LIBRARY MANAGEMENT =========
1. Add book
2. Remove book
3. List all books
4. Search book
5. Add member
6. List members
7. Issue book
8. Return book
9. Exit
======================================"""

    while True:
        print(actions)
        choice = input("Choose (1-9): ").strip()

        if choice == "1":
            bid = input("Book ID: ").strip()
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            copies = int(input("Copies: ").strip() or "1")
            lib.add_book(bid, title, author, copies)

        elif choice == "2":
            lib.remove_book(input("Book ID to remove: ").strip())

        elif choice == "3":
            lib.list_books()

        elif choice == "4":
            lib.search_books(input("Keyword (title/author): ").strip())

        elif choice == "5":
            mid = input("Member ID: ").strip()
            name = input("Name: ").strip()
            lib.add_member(mid, name)

        elif choice == "6":
            lib.list_members()

        elif choice == "7":
            lib.issue_book(input("Book ID: ").strip(), input("Member ID: ").strip())

        elif choice == "8":
            lib.return_book(input("Book ID: ").strip(), input("Member ID: ").strip())

        elif choice == "9":
            print("Bye! Data save ho gaya hai. 👋")
            break

        else:
            print("✗ Galat option. 1 se 9 ke beech choose kariye.")


if __name__ == "__main__":
    menu()
