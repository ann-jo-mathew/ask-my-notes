import os
import chromadb
from pypdf import PdfReader

# The notes box, saved in a folder called notes_db
client = chromadb.PersistentClient(path="notes_db")#create db
collection = client.get_or_create_collection("my_notes") #impo get_or_create to create inside the chroma_db

def cut_into_pieces(text, size=800, overlap=100): #for saving as chunks
    pieces = []
    start = 0
    while start < len(text):
        pieces.append(text[start:start + size])
        start = start + size - overlap
    return pieces

def add_pdf(path):
    name = os.path.basename(path)
    reader = PdfReader(path)
    count = 0
    for page_number, page in enumerate(reader.pages, start=1): #page wise read and pass the page content into cut to pieces
        text = page.extract_text() or ""
        for i, piece in enumerate(cut_into_pieces(text)):#chunks are looped and made into embeddings 
            if piece.strip():
                collection.upsert(
                    ids=[f"{name}-page{page_number}-{i}"],
                    documents=[piece],
                    metadatas=[{"source": name, "page": page_number}],
                )
                count = count + 1
    print(f"Added {name}: {count} pieces")
    return count

if __name__ == "__main__":
    for file in os.listdir("docs"):
        if file.lower().endswith(".pdf"):
            add_pdf(os.path.join("docs", file))
    print("Total pieces in the notes box:", collection.count())
