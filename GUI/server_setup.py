import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import os
import random
import string


def generate_random_string(length=32, characters=None):
    """Generate a random string with the given length and character set."""
    if characters is None:
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(random.choice(characters) for _ in range(length))


def setup_server(port, secret_key, mongo_user, mongo_password, mongo_database, debugging):
    # Clone the repository
    repo_url = "https://github.com/ION-WorkoutApp/server.git"
    try:
        subprocess.run(["git", "clone", repo_url], check=True)
        repo_name = repo_url.split("/")[-1].replace(".git", "")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to clone the repository.")
        return

    # Write the .env file
    env_path = os.path.join(repo_name, ".env")
    try:
        with open(env_path, "w") as env_file:
            env_file.write(f"PORT={port}\n")
            env_file.write(f"SECRET_KEY={secret_key}\n")
            env_file.write(
                f"MONGO_URI=mongodb://{mongo_user}:{mongo_password}@mongodb:27017/{mongo_database}?authSource=admin\n"
            )
            env_file.write(f"MONGO_INITDB_ROOT_USERNAME={mongo_user}\n")
            env_file.write(f"MONGO_INITDB_ROOT_PASSWORD={mongo_password}\n")
            env_file.write(f"MONGO_DATABASE={mongo_database}\n")
            env_file.write(f"DEBUGGING={str(debugging).lower()}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Error writing .env file: {e}")
        return

    # Pull Docker images
    try:
        subprocess.run(["docker", "compose", "pull"], cwd=repo_name, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to pull Docker images.")
        return

    messagebox.showinfo("Success", "Server setup completed successfully!")


def open_gui():
    def on_submit():
        port = port_var.get().strip()
        secret_key = secret_key_var.get().strip()
        mongo_user = mongo_user_var.get().strip()
        mongo_password = mongo_password_var.get().strip()
        mongo_database = mongo_database_var.get().strip()
        debugging = debugging_var.get()  # Boolean (1 for checked, 0 for unchecked)

        if not all([port, secret_key, mongo_user, mongo_password, mongo_database]):
            return messagebox.showerror("Error!", "All fields must be filled out!")

        setup_server(port, secret_key, mongo_user, mongo_password, mongo_database, debugging)

    def add_placeholder(entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.bind("<FocusIn>", lambda e: clear_placeholder(entry, placeholder_text))
        entry.bind("<FocusOut>", lambda e: restore_placeholder(entry, placeholder_text))

    def clear_placeholder(entry, placeholder_text):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(foreground="#ffffff")

    def restore_placeholder(entry, placeholder_text):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="#808080")

    def generate_random_values():
        """Generate random values and populate the relevant fields."""
        random_secret = generate_random_string()
        random_password = generate_random_string()

        secret_key_entry.delete(0, tk.END)
        secret_key_entry.insert(0, random_secret)
        secret_key_entry.config(foreground="#4ee44e")  # Highlight auto-generated value

        mongo_password_entry.delete(0, tk.END)
        mongo_password_entry.insert(0, random_password)
        mongo_password_entry.config(foreground="#4ee44e")  # Highlight auto-generated value

        # messagebox.showinfo("Generated", "Random values have been generated and filled in the form.")

    # Root window
    root = tk.Tk()
    root.title("Server Setup")
    root.geometry("600x550")
    root.configure(bg="#2c2f33")  # Dark background

    # Main container
    container = ttk.Frame(root, padding=20, style="DarkCard.TFrame")
    container.pack(expand=True, fill="both", padx=20, pady=20)

    # Header
    ttk.Label(container, text="Server Setup", style="DarkHeader.TLabel").pack(pady=10)

    # Form groups
    def add_form_field(container, label_text, variable, placeholder):
        frame = ttk.Frame(container, style="DarkCard.TFrame")
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label_text, style="DarkForm.TLabel").pack(anchor="w", padx=5)
        entry = ttk.Entry(frame, textvariable=variable, style="DarkEntry.TEntry")
        entry.pack(fill="x", padx=5, pady=5)
        add_placeholder(entry, placeholder)
        return entry  # Return the entry widget for customization

    # Form variables
    port_var = tk.StringVar()
    secret_key_var = tk.StringVar()
    mongo_user_var = tk.StringVar()
    mongo_password_var = tk.StringVar()
    mongo_database_var = tk.StringVar()
    debugging_var = tk.IntVar(value=1)  # Checkbox for debugging (1 = checked, 0 = unchecked)

    # Add form fields with placeholders
    add_form_field(container, "Port", port_var, placeholder="1221")
    secret_key_entry = add_form_field(container, "Secret Key", secret_key_var, placeholder="yourSecret")
    add_form_field(container, "MongoDB User", mongo_user_var, placeholder="workoutadmin")
    mongo_password_entry = add_form_field(container, "MongoDB Password", mongo_password_var, placeholder="yourPassword")
    add_form_field(container, "MongoDB Database", mongo_database_var, placeholder="maindb")

    # Random value generation button
    ttk.Button(container, text="Generate Random Values", command=generate_random_values, style="DarkButton.TButton").pack(fill="x", pady=10)

    # Debugging checkbox with custom styling
    debug_frame = ttk.Frame(container, style="DarkCard.TFrame")
    debug_frame.pack(fill="x", pady=10)
    debug_label = ttk.Label(debug_frame, text="Debugging", style="DarkForm.TLabel")
    debug_label.pack(side="left", padx=5)

    debug_checkbox = ttk.Checkbutton(debug_frame, variable=debugging_var, style="CustomCheck.TCheckbutton")
    debug_checkbox.pack(side="left")

    # Submit button
    ttk.Button(container, text="Setup Server", command=on_submit, style="DarkButton.TButton").pack(fill="x", pady=20)

    # Styles
    style = ttk.Style()
    style.configure("DarkCard.TFrame", background="#23272a")
    style.configure("DarkHeader.TLabel", font=("Arial", 18, "bold"), background="#23272a", foreground="#ffffff")
    style.configure("DarkForm.TLabel", font=("Arial", 12), background="#23272a", foreground="#b9bbbe")
    style.configure("DarkEntry.TEntry", font=("Arial", 12), fieldbackground="#2c2f33", foreground="#808080", insertcolor="#ffffff", borderwidth=1, highlightthickness=0)
    style.configure("DarkButton.TButton", font=("Arial", 14), background="#7289da", foreground="#ffffff", padding=10)
    style.map("DarkButton.TButton", background=[("active", "#5b6eae")])

    root.mainloop()


if __name__ == "__main__":
    open_gui()
