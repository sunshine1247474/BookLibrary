import tkinter as tk
from tkinter import ttk, messagebox
import json
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

# Load data from JSON files
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Save data to JSON file
def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize data
books = load_data('data/books.json')
favorites = []  # Initialize favorites as an empty list

# Define genre information
genre_info = {
    "Personal finance, Self-help": "Covers managing money, investing, and financial planning.",
    "Finance": "Focuses on the study of investments, money, and revenue management.",
    "Self-help": "Includes books that are intended to help readers solve personal problems.",
    "Sociology": "Deals with the study of society, patterns of social relationships, and culture.",
    "Psychology": "Involves the scientific study of the human mind and its functions."
}

# Create the main application window
root = tk.Tk()
root.title("BookLibrary")
root.geometry("800x600")  # Set the size of the window

# Styling for buttons and listboxes
style = ttk.Style(root)
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TListbox', font=('Helvetica', 12))

# Function to handle genre selection
def on_genre_select(event):
    widget = event.widget
    if widget.curselection():
        index = int(widget.curselection()[0])
        genre = widget.get(index)
        display_books(genre)
        # Update the genre description label
        genre_description.config(text=genre_info.get(genre, "No description available."))

# Function to update the books listbox based on the selected genre
def display_books(genre):
    books_listbox.delete(0, tk.END)
    for book in books:
        if book['genre'] == genre:
            books_listbox.insert(tk.END, book['title'])
    # Display genre description
    genre_description.config(text=genre_info[genre])

# Function to show book details with a "Read More" option
def show_book_details(book_title):
    for book in books:
        if book['title'] == book_title:
            details_text = f"Title: {book['title']}\n"
            details_text += f"Author: {book['author']}\n"
            details_text += f"Year: {book['year']}\n"
            details_text += f"Genre: {book['genre']}\n\n"
            details_text += f"Description: {book['description']}\n"
            book_details.config(text=details_text, wraplength=root.winfo_width() // 2)

# Function to toggle the 'like' status of a book
def toggle_like(book_title, from_favorites=False):
    for book in books:
        if book['title'] == book_title:
            book['liked'] = not book.get('liked', False)
            if book['liked']:
                favorites.append(book_title)
            else:
                # Check if the book title is in the favorites list before removing it
                if book_title in favorites:
                    favorites.remove(book_title)
            update_favorites_listbox()
            save_data('data/books.json', books)
            break
    update_favorite_button(book_title)

# Function to update the favorites listbox
def update_favorites_listbox():
    favorites_listbox.delete(0, tk.END)
    for title in favorites:
        favorites_listbox.insert(tk.END, title)

# Function to handle book selection
def on_book_select(event):
    widget = event.widget
    if widget.curselection():
        index = int(widget.curselection()[0])
        book_title = widget.get(index)
        show_book_details(book_title)
        update_favorite_button(book_title)

# Function to handle favorite book selection
def on_favorite_select(event):
    widget = event.widget
    if widget.curselection():
        index = int(widget.curselection()[0])
        book_title = widget.get(index)
        show_book_details(book_title)
        update_favorite_button(book_title, from_favorites=True)

# Function to update the favorite button based on the context
def update_favorite_button(book_title, from_favorites=False):
    if from_favorites or book_title in favorites:
        favorite_button.config(text="Remove from Favorites", command=lambda: toggle_like(book_title, True))
    else:
        favorite_button.config(text="Add to Favorites", command=lambda: toggle_like(book_title))
    favorite_button.pack()

# Extract unique genres from the books data
genres = list(set(book['genre'] for book in books))

# PanedWindow for resizable columns
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Search entry and button
search_frame = ttk.LabelFrame(paned_window, text='Search')
search_entry = ttk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Function to handle book search
def search_books(query):
    # Tokenize the query
    tokens = word_tokenize(query)
    
    # Initialize an empty list to store matches
    matches = []
    
    # Check each token against the genres and book titles
    for token in tokens:
        for book in books:
            if token.lower() in book['title'].lower():
                matches.append(book)
    
    # Return the matches
    return matches

# Function to display search results
def display_search_results(results):
    if results:
        # Get the genre of the first result
        genre = results[0]['genre']
        
        # Display books of the same genre
        display_books(genre)
        
        # Highlight the found book(s) in the list
        for i, title in enumerate(books_listbox.get(0, tk.END)):
            for book in results:
                if title == book['title']:
                    books_listbox.selection_set(i)
                    break
    else:
        # Clear the listbox
        books_listbox.delete(0, tk.END)
        
        # Display a message to the user
        books_listbox.insert(tk.END, "Book not found. Please check back soon for updates.")

# Define the search_button here
search_button = ttk.Button(search_frame, text="Search")
search_button.pack(side=tk.LEFT)
search_frame.pack(fill=tk.X)
paned_window.add(search_frame, weight=1)

# Now you can configure the search_button
search_button.config(command=lambda: display_search_results(search_books(search_entry.get())))

# Bind the <Return> key to the search button command
root.bind('<Return>', lambda event: display_search_results(search_books(search_entry.get())))

# Bind the <KeyRelease> event to the search entry to show search suggestions
search_entry.bind('<KeyRelease>', lambda event: display_search_suggestions(search_books(search_entry.get())))

# Function to display search suggestions
def display_search_suggestions(suggestions):
    # Clear the listbox
    books_listbox.delete(0, tk.END)
    
    # Add the suggestions to the listbox
    for suggestion in suggestions:
        books_listbox.insert(tk.END, suggestion['title'])

# Genre listbox with title
genre_frame = ttk.LabelFrame(paned_window, text='Genres')
genres_listbox = tk.Listbox(genre_frame)
genres_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
for genre in genres:
    genres_listbox.insert(tk.END, genre)
genres_listbox.bind('<<ListboxSelect>>', on_genre_select)
genre_frame.pack(fill=tk.BOTH, expand=True)
paned_window.add(genre_frame, weight=1)

# Books listbox with title
books_frame = ttk.LabelFrame(paned_window, text='Books')
books_listbox = tk.Listbox(books_frame)
books_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
books_listbox.bind('<<ListboxSelect>>', on_book_select)
books_frame.pack(fill=tk.BOTH, expand=True)
paned_window.add(books_frame, weight=2)

# Favorites listbox with title
favorites_frame = ttk.LabelFrame(paned_window, text='Favorites')
favorites_listbox = tk.Listbox(favorites_frame)
favorites_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
favorites_listbox.bind('<<ListboxSelect>>', on_favorite_select)
favorites_frame.pack(fill=tk.BOTH, expand=True)
paned_window.add(favorites_frame, weight=1)

# Book details label
book_details = tk.Label(root, text="", justify=tk.LEFT, anchor="nw")
book_details.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Genre description label
genre_description = tk.Label(root, text="", justify=tk.CENTER)
genre_description.pack(side=tk.TOP, fill=tk.X)

# Dynamic favorite button
favorite_button = ttk.Button(root, text="")

# Start the application
root.mainloop()
