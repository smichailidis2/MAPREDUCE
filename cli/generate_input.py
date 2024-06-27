import random
import os

def generate_large_file(filename, target_size_mb, word_list):
    size = 0
    target_size = target_size_mb * 1024 * 1024  # Convert target size to bytes

    with open(filename, 'w') as file:
        while size < target_size:
            word = random.choice(word_list)
            file.write(word + " ")
            size += len(word) + 1  # Update current size (+1 for the space)

if __name__ == "__main__":
    words = ["alpha", "beta", "gamma", "delta", "dimitris", "stergios", "george", "vsam", "tuc"]

    generate_large_file('input_data.txt', 200, words)
