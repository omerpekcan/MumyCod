import json
import os

TODO_FILE = "todos.json"

def load_todos():
    """
    todos.json dosyasından görevleri yükler. Dosya yoksa boş bir liste döndürür.
    """
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_todos(todos):
    """
    Görev listesini todos.json dosyasına kaydeder.
    """
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=4)

def add_todo(description):
    """
    Yeni bir görev ekler.
    """
    todos = load_todos()
    todos.append({"id": len(todos) + 1, "description": description, "done": False})
    save_todos(todos)
    print(f"Görev eklendi: '{description}'")

def list_todos():
    """
    Tüm görevleri listeler.
    """
    todos = load_todos()
    if not todos:
        print("Henüz hiç görev yok.")
        return
    print("Yapılacaklar Listesi:")
    for todo in todos:
        status = "[x]" if todo["done"] else "[ ]"
        print(f"{todo['id']}. {status} {todo['description']}")

def delete_todo(todo_id):
    """
    Belirtilen ID'ye sahip görevi siler.
    """
    todos = load_todos()
    initial_length = len(todos)
    todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(todos) < initial_length:
        # ID'leri yeniden düzenle
        for i, todo in enumerate(todos):
            todo["id"] = i + 1
        save_todos(todos)
        print(f"Görev {todo_id} silindi.")
    else:
        print(f"Görev {todo_id} bulunamadı.")

def main():
    """
    Uygulamanın ana fonksiyonu, komut satırı argümanlarını işler.
    """
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python todo_app.py <komut> [argümanlar]")
        print("Komutlar: add, list, delete")
        return

    command = sys.argv[1].lower()

    if command == "add":
        if len(sys.argv) < 3:
            print("Kullanım: python todo_app.py add <görev_açıklaması>")
        else:
            description = " ".join(sys.argv[2:])
            add_todo(description)
    elif command == "list":
        list_todos()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Kullanım: python todo_app.py delete <görev_id>")
        else:
            try:
                todo_id = int(sys.argv[2])
                delete_todo(todo_id)
            except ValueError:
                print("Geçersiz görev ID. Lütfen bir sayı girin.")
    else:
        print(f"Bilinmeyen komut: {command}")
        print("Kullanılabilir komutlar: add, list, delete")

if __name__ == "__main__":
    main()
,