```python
# workspace/todo_app.py

import json
import os

TODO_FILE = 'todos.json'

def load_todos():
    \"\"\"JSON dosyasından görevleri yükler.\"\"\"
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_todos(todos):
    \"\"\"Görevleri JSON dosyasına kaydeder.\"\"\"
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)

def add_todo(task):
    \"\"\"Yeni bir görev ekler.\"\"\"
    todos = load_todos()
    todos.append({"id": len(todos) + 1, "task": task, "completed": False})
    save_todos(todos)
    print(f"Görev '{task}' eklendi.")

def list_todos():
    \"\"\"Tüm görevleri listeler.\"\"\"
    todos = load_todos()
    if not todos:
        print("Henüz hiç görev yok!")
        return
    print("Görevler:")
    for todo in todos:
        status = "[X]" if todo["completed"] else "[ ]"
        print(f"{todo['id']}. {status} {todo['task']}")

def delete_todo(todo_id):
    \"\"\"Belirtilen ID'ye sahip görevi siler.\"\"\"
    todos = load_todos()
    initial_length = len(todos)
    todos = [todo for todo in todos if todo['id'] != todo_id]
    if len(todos) < initial_length:
        save_todos(todos)
        print(f"Görev ID {todo_id} silindi.")
    else:
        print(f"Görev ID {todo_id} bulunamadı.")

def main():
    \"\"\"Uygulamanın ana giriş noktası.\"\"\"
    while True:
        command = input("Komut girin (ekle, listele, sil, çık): ").lower().split(maxsplit=1)
        action = command[0]

        if action == "ekle":
            if len(command) > 1:
                add_todo(command[1])
            else:
                print("Ekle komutu için bir görev metni belirtin.")
        elif action == "listele":
            list_todos()
        elif action == "sil":
            if len(command) > 1 and command[1].isdigit():
                delete_todo(int(command[1]))
            else:
                print("Sil komutu için geçerli bir görev ID'si belirtin.")
        elif action == "çık":
            print("Uygulamadan çıkılıyor.")
            break
        else:
            print("Geçersiz komut. Lütfen 'ekle', 'listele', 'sil' veya 'çık' komutlarından birini kullanın.")

if __name__ == "__main__":
    main()
```