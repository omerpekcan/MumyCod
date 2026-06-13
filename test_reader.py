from tools.file_reader import FileReader

reader = FileReader()

content = reader.read(
    "core/agent.py"
)

print(content[:1000])