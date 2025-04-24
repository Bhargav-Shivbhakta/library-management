import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB using secrets
client = MongoClient(st.secrets["MONGO_URI"])
db = client["library_db"]

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")
st.title("📚 Library Management System")

menu = ["View Books", "Add Book", "Issue Book", "Return Book", "Add Student", "View Students"]
choice = st.sidebar.selectbox("Navigation", menu)

# View Books
if choice == "View Books":
    st.subheader("Available Books")
    books = list(db.books.find())
    if not books:
        st.info("📭 No books available in the library.")
    else:
        for book in books:
            st.markdown(f"**{book['_id']}** - {book['title']} by {book['author']} (Available: {'✅' if book['available'] else '❌'})")

# Add Book
elif choice == "Add Book":
    st.subheader("Add a New Book")
    with st.form("add_book_form"):
        book_id = st.text_input("Book ID")
        title = st.text_input("Title")
        author = st.text_input("Author")
        genre = st.text_input("Genre")
        submitted = st.form_submit_button("Add Book")

        if submitted:
            if db.books.find_one({"_id": book_id}):
                st.warning("⚠️ Book with this ID already exists!")
            else:
                db.books.insert_one({
                    "_id": book_id,
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "available": True
                })
                st.success("✅ Book added successfully!")

# Add Student
elif choice == "Add Student":
    st.subheader("Register a New Student")
    with st.form("add_student_form"):
        student_id = st.text_input("Student ID")
        name = st.text_input("Student Name")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Register Student")

        if submitted:
            if db.students.find_one({"_id": student_id}):
                st.warning("⚠️ Student with this ID already exists!")
            else:
                db.students.insert_one({
                    "_id": student_id,
                    "name": name,
                    "email": email
                })
                st.success("✅ Student registered successfully!")

# View Students
elif choice == "View Students":
    st.subheader("Registered Students")
    students = list(db.students.find())
    if not students:
        st.info("👥 No students registered yet.")
    else:
        for student in students:
            st.markdown(f"**{student['_id']}** - {student['name']} ({student['email']})")

# Issue Book
elif choice == "Issue Book":
    st.subheader("Issue a Book")
    available_books = list(db.books.find({"available": True}))
    book_options = [f"{book['_id']} - {book['title']}" for book in available_books]
    student_options = [f"{student['_id']} - {student['name']}" for student in db.students.find()]

    with st.form("issue_form"):
        if not book_options:
            st.warning("📕 No available books to issue.")
        elif not student_options:
            st.warning("👥 No students available.")
        else:
            selected_book = st.selectbox("Select Book to Issue", book_options)
            selected_student = st.selectbox("Select Student", student_options)
            submitted = st.form_submit_button("Issue")

            if submitted:
                book_id = selected_book.split(" - ")[0]
                student_id = selected_student.split(" - ")[0]
                db.books.update_one({"_id": book_id}, {"$set": {"available": False}})
                db.issued_books.insert_one({
                    "book_id": book_id,
                    "student_id": student_id,
                    "issue_date": str(st.session_state.get("now", "2025-04-24")),
                    "return_date": None
                })
                st.success("📘 Book issued successfully!")

# Return Book
elif choice == "Return Book":
    st.subheader("Return a Book")
    issued = list(db.issued_books.find({"return_date": None}))
    issued_options = [f"{entry['book_id']} - {entry['student_id']}" for entry in issued]

    with st.form("return_form"):
        if not issued_options:
            st.info("📦 No books currently issued.")
        else:
            selected = st.selectbox("Select Issued Book to Return", issued_options)
            submitted = st.form_submit_button("Return")

            if submitted:
                book_id, student_id = selected.split(" - ")
                db.books.update_one({"_id": book_id}, {"$set": {"available": True}})
                db.issued_books.update_one(
                    {"book_id": book_id, "student_id": student_id, "return_date": None},
                    {"$set": {"return_date": str(st.session_state.get("now", "2025-04-24"))}}
                )
                st.success("📗 Book returned successfully!")
