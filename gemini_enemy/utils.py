def create_file_if_not_exists(file_name):
    try:
        with open(file_name, "x") as file:
            pass
    except:
        pass

def read_file_lines(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
        return lines

def write_memory(memory_file, memory):
    with open(memory_file, "w") as file:
        for line in memory:
            file.write(line + "\n")
    
def load_memory(memory_file, memory):
    create_file_if_not_exists(memory_file)

    lines = read_file_lines(memory_file)

    for line in lines:
        memory.append(line)