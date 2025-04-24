
import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB using Streamlit secrets
client = MongoClient(st.secrets["MONGO_URI"])
db = client["library_db"]

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")
st.title("📚 Library Management System")

menu = ["View Books", "Add Book", "Issue Book", "Return Book"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "View Books":
    st.subheader("Available Books")
    books = db.books.find()
    for book in books:
        st.markdown(f"**{book['_id']}** - {book['title']} by {book['author']} (Available: {'✅' if book['available'] else '❌'})")

elif choice == "Add Book":
    st.subheader("Add a New Book")
    with st.form("add_book_form"):
        book_id = st.text_input("Book ID")
        title = st.text_input("Title")
        author = st.text_input("Author")
        genre = st.text_input("Genre")
        submitted = st.form_submit_button("Add Book")
        if submitted:
            db.books.insert_one({
                "_id": book_id,
                "title": title,
                "author": author,
                "genre": genre,
                "available": True
            })
            st.success("✅ Book added successfully!")

elif choice == "Issue Book":
    st.subheader("Issue a Book")
    with st.form("issue_form"):
        book_id = st.text_input("Book ID to Issue")
        student_id = st.text_input("Student ID")
        submitted = st.form_submit_button("Issue")
        if submitted:
            db.books.update_one({"_id": book_id}, {"$set": {"available": False}})
            db.issued_books.insert_one({
                "book_id": book_id,
                "student_id": student_id,
                "issue_date": str(st.session_state.get("now", "2025-04-24")),
                "return_date": None
            })
            st.success("📘 Book issued successfully!")

elif choice == "Return Book":
    st.subheader("Return a Book")
    with st.form("return_form"):
        book_id = st.text_input("Book ID to Return")
        student_id = st.text_input("Student ID")
        submitted = st.form_submit_button("Return")
        if submitted:
            db.books.update_one({"_id": book_id}, {"$set": {"available": True}})
            db.issued_books.update_one(
                {"book_id": book_id, "student_id": student_id, "return_date": None},
                {"$set": {"return_date": str(st.session_state.get("now", "2025-04-24"))}}
            )
            st.success("📗 Book returned successfully!")
