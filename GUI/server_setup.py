import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import random
import string

def generate_random_string(length=32, characters=None):
	if characters is None:
		characters = string.ascii_letters + string.digits + "!^&*_+-="
	return ''.join(random.choice(characters) for _ in range(length))

def setup_server(port, secret_key, mongo_user, mongo_password, mongo_database, debugging, email_sender, email_user, email_pass, email_smtp_host, email_smtp_port, site_url):
	repo_url = "https://github.com/ION-WorkoutApp/server.git"
	portal_url = "https://github.com/ION-WorkoutApp/admin-portal.git"
 
	try:
		subprocess.run(["git", "clone", repo_url], check=True)
		repo_name = repo_url.split("/")[-1].replace(".git", "")
	except subprocess.CalledProcessError:
		messagebox.showerror("Error", "Failed to clone base repository")
		return

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
   
			if debugging:
				env_file.write(f"DEBUGGING={str(debugging).lower()}\n")
    
			env_file.write(f"EMAIL_SENDER={email_sender}\n")
			env_file.write(f"EMAIL_USER={email_user}\n")
			env_file.write(f"EMAIL_PASS={email_pass}\n")
			env_file.write(f"EMAIL_SMTP_HOST={email_smtp_host}\n")
			env_file.write(f"EMAIL_SMTP_PORT={email_smtp_port}\n")
	except Exception as e:
		messagebox.showerror("Error", f"Error writing .env file: {e}")
		return

	try:
		subprocess.run(["git", "clone", portal_url], check=True)
		repo_name = repo_url.split("/")[-1].replace(".git", "")
	except subprocess.CalledProcessError:
		messagebox.showerror("Error", "Failed to set up admin portal")
		return

	env_path = os.path.join(repo_name, ".env")
	with open(env_path, "w") as env_file:
		env_file.write(f"API_BASE_URL={site_url}\n")

	try:
		subprocess.run(["docker", "compose", "pull"], cwd=repo_name, check=True)
	except subprocess.CalledProcessError:
		messagebox.showerror("Error", "Failed to pull Docker images")
		return

	messagebox.showinfo("Success", "Server setup completed successfully!")


class PlaceholderEntry(ttk.Entry):
	def __init__(self, master=None, placeholder="", show=None, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.placeholder = placeholder
		self.show_character = show  # For password masking
		self.default_show = self.cget("show")
		self.default_fg_color = self.cget("foreground")
		self.placeholder_fg_color_light = "gray"
		self.placeholder_fg_color_dark = "lightgray"
		self.has_placeholder = False
		self.insert_placeholder()
		self.bind("<FocusIn>", self.foc_in)
		self.bind("<FocusOut>", self.foc_out)
		self.bind("<Configure>", self.update_placeholder_color)

	def insert_placeholder(self):
		self.insert(0, self.placeholder)
		current_theme = ttk.Style().theme_use()
		if current_theme == "dark":
			self.config(foreground=self.placeholder_fg_color_dark, show="")
		else:
			self.config(foreground=self.placeholder_fg_color_light, show="")
		self.has_placeholder = True

	def remove_placeholder(self):
		if self.has_placeholder:
			self.delete(0, tk.END)
			self.config(foreground=self.default_fg_color)
			if self.show_character:
				self.config(show=self.show_character)
			else:
				self.config(show=self.default_show)
			self.has_placeholder = False

	def foc_in(self, *args):
		if self.has_placeholder:
			self.remove_placeholder()

	def foc_out(self, *args):
		if not self.get():
			self.insert_placeholder()

	def update_placeholder_color(self, event=None):
		if self.has_placeholder:
			current_theme = ttk.Style().theme_use()
			if current_theme == "dark":
				self.config(foreground=self.placeholder_fg_color_dark)
			else:
				self.config(foreground=self.placeholder_fg_color_light)

class ScrollableFrame(ttk.Frame):
	def __init__(self, container, *args, **kwargs):
		super().__init__(container, *args, **kwargs)

		# Create a canvas and vertical scrollbar
		self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.scrollable_frame = ttk.Frame(self.canvas)

		# Configure the canvas to use the scrollbar
		self.canvas.configure(yscrollcommand=self.scrollbar.set)

		# Create a window inside the canvas
		self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

		# Bind the <Configure> event of the scrollable_frame to update the scrollregion
		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: self.canvas.configure(
				scrollregion=self.canvas.bbox("all")
			)
		)

		# Bind the <Configure> event of the canvas to update the width of the scrollable_frame
		self.canvas.bind("<Configure>", self.on_canvas_configure)

		# Pack the canvas and scrollbar
		self.canvas.pack(side="left", fill="both", expand=True)
		self.scrollbar.pack(side="right", fill="y")

	def on_canvas_configure(self, event):
		"""Update the width of the scrollable_frame to match the canvas's width."""
		canvas_width = event.width
		self.canvas.itemconfig(self.window_id, width=canvas_width)

	def update_theme(self, dark_mode):
		"""Update the canvas background based on the theme."""
		if dark_mode:
			self.canvas.config(background="#2E2E2E")
		else:
			self.canvas.config(background="#f0f0f0")

def open_gui():
	def on_submit():
		# Validate required fields
		required_fields = [
			("Port", port_var.get().strip()),
			("Secret Key", secret_key_var.get().strip()),
			("MongoDB User", mongo_user_var.get().strip()),
			("MongoDB Password", mongo_password_var.get().strip()),
			("MongoDB Database", mongo_database_var.get().strip()),
			("Email User", email_user_var.get().strip()),
			("Email Sender", email_user_var.get().strip()),
			("Email Password", email_pass_var.get().strip()),
			("SMTP Host", email_smtp_host_var.get().strip()),
			("SMTP Port", email_smtp_port_var.get().strip())
		]

		for field_name, value in required_fields:
			if not value:
				messagebox.showerror("Error", f"{field_name} cannot be empty.")
				return

		# Optionally generate secrets if empty
		if not secret_key_var.get().strip():
			secret_key_var.set(generate_random_string())

		if not mongo_password_var.get().strip():
			mongo_password_var.set(generate_random_string())

		setup_server(
			port_var.get().strip(),
			secret_key_var.get().strip(),
			mongo_user_var.get().strip(),
			mongo_password_var.get().strip(),
			mongo_database_var.get().strip(),
			debugging_var.get() != 0,
			email_sender_var.get().strip(),
			email_user_var.get().strip(),
			email_pass_var.get().strip(),
			email_smtp_host_var.get().strip(),
			email_smtp_port_var.get().strip(),
			site_url.get().strip()
		)

	def toggle_theme():
		if dark_theme_var.get():
			style.theme_use("dark")
			container.update_theme(dark_mode=True)
		else:
			style.theme_use("light")
			container.update_theme(dark_mode=False)

	root = tk.Tk()
	root.title("Server Setup")
	root.geometry("600x800")
	root.resizable(True, True)  # Allow resizing to enable scrollbar

	# Initialize styles
	style = ttk.Style()
	root.style = style  # Make style accessible if needed elsewhere

	# Define Light Theme
	style.theme_create("light", parent="default", settings={
		"TFrame": {
			"configure": {"background": "#f0f0f0"}
		},
		"TLabel": {
			"configure": {"background": "#f0f0f0", "foreground": "#000000"}
		},
		"TLabelframe": {
			"configure": {"background": "#f0f0f0", "foreground": "#000000"}
		},
		"TLabelframe.Label": {
			"configure": {
				"background": "#f0f0f0",
				"foreground": "#FF8C00",
				"font": ("Arial", 12, "bold"),
				"anchor": "center"
			}
		},
		"TEntry": {
			"configure": {"fieldbackground": "#ffffff", "foreground": "#000000", "insertcolor": "#000000"}
		},
		"TButton": {
			"configure": {"background": "#e0e0e0", "foreground": "#000000"}
		},
		"TCheckbutton": {
			"configure": {"background": "#f0f0f0", "foreground": "#000000"}
		},
		"Orange.TLabel": {
			"configure": {"background": "#f0f0f0", "foreground": "#FF8C00"}
		},
	})

	# Define Dark Theme with Improved Colors
	style.theme_create("dark", parent="clam", settings={
		"TFrame": {
			"configure": {"background": "#2E2E2E"}
		},
		"TLabel": {
			"configure": {"background": "#2E2E2E", "foreground": "#E0E0E0"}
		},
		"TLabelframe": {
			"configure": {"background": "#2E2E2E", "foreground": "#E0E0E0"}
		},
		"TLabelframe.Label": {
			"configure": {
				"background": "#2E2E2E",
				"foreground": "#FFA500",
				"font": ("Arial", 14, "bold"),
				"anchor": "center"
			}
		},
		"TEntry": {
			"configure": {"fieldbackground": "#3C3F41", "foreground": "#E0E0E0", "insertcolor": "#E0E0E0"}
		},
		"TButton": {
			"configure": {"background": "#5A5A5A", "foreground": "#FFFFFF"}
		},
		"TCheckbutton": {
			"configure": {"background": "#2E2E2E", "foreground": "#E0E0E0"}
		},
		"Orange.TLabel": {
			"configure": {"background": "#2E2E2E", "foreground": "#FFA500"}  # Orange color
		},
	})

	# Use Dark Theme by default
	style.theme_use("dark")

	# Create Scrollable Frame
	container = ScrollableFrame(root)
	container.pack(expand=True, fill="both", padx=10, pady=10)

	# Update the ScrollableFrame's background according to the current theme
	container.update_theme(dark_mode=True)

	# Header Label
	header_label = ttk.Label(container.scrollable_frame, text="Server Setup", font=("Arial", 18, "bold"))
	header_label.pack(pady=10, padx=10)

	# Variables
	port_var = tk.StringVar(value="1221")
	secret_key_var = tk.StringVar(value="yourSecret")
	mongo_user_var = tk.StringVar(value="yourUser")
	mongo_password_var = tk.StringVar(value="yourPassword")
	mongo_database_var = tk.StringVar(value="maindb")
	debugging_var = tk.IntVar(value=0)
	email_sender_var = tk.StringVar(value="donotreply@ion606.com")
	email_user_var = tk.StringVar(value="main@ion606.com")
	email_pass_var = tk.StringVar(value="emailpassword")
	email_smtp_host_var = tk.StringVar(value="smtp.fastmail.com")
	email_smtp_port_var = tk.StringVar(value="465")
	site_url = tk.StringVar(value="https://workoutapp.ion606.com")

	# Theme Toggle Checkbox
	dark_theme_var = tk.BooleanVar(value=True)
	dark_theme_cb = ttk.Checkbutton(container.scrollable_frame, text="Dark Theme", variable=dark_theme_var, command=toggle_theme)
	dark_theme_cb.pack(pady=5, padx=10)

	# Main Fields
	fields = [
		("Site URL", site_url, site_url.get().strip()),
		("Port", port_var, "1221"),
		("Secret Key", secret_key_var, "yourSecret"),
		("MongoDB User", mongo_user_var, "yourUser"),
		("MongoDB Password", mongo_password_var, "yourPassword"),
		("MongoDB Database", mongo_database_var, "maindb"),
	]

	for label_text, var, placeholder in fields:
		frame = ttk.Frame(container.scrollable_frame)
		frame.pack(fill="x", pady=5, padx=10)
		label = ttk.Label(frame, text=label_text)
		label.pack(anchor="w", padx=5)
		if "Password" in label_text:
			entry = PlaceholderEntry(frame, placeholder=placeholder, textvariable=var, show='*')
		else:
			entry = PlaceholderEntry(frame, placeholder=placeholder, textvariable=var)
		entry.pack(fill="x", padx=5, pady=2)

	# Create Email Settings Label
	email_title = ttk.Label(container.scrollable_frame, text="Email Settings", font=("Arial", 14, "bold"))
	email_title.pack(pady=(50, 0))  # Add spacing to separate from previous section

	# Email Settings Frame (Without Title)
	email_frame = ttk.LabelFrame(container.scrollable_frame, padding=(0, 0))
	email_frame.pack(fill="x", pady=0, padx=10)

	# Email Disclaimer
	email_disclaimer = ttk.Label(
		email_frame,
		text="DISCLAIMER: You must configure email settings to use email services.",
		font=("Arial", 9, "bold"),
		style="Orange.TLabel",  # Using the Orange.TLabel style
		wraplength=560,
		justify="center"
	)
	email_disclaimer.pack(pady=0, padx=10)

	# Email Fields
	email_fields = [
		("Email Sender", email_sender_var, "donotreply@ion606.com"),
		("Email User", email_user_var, "main@ion606.com"),
		("Email Password", email_pass_var, "????????"),
		("SMTP Host", email_smtp_host_var, "smtp.fastmail.com"),
		("SMTP Port", email_smtp_port_var, "465"),
	]

	for label_text, var, placeholder in email_fields:
		frame = ttk.Frame(email_frame)
		frame.pack(fill="x", pady=5, padx=10)
		label = ttk.Label(frame, text=label_text, style="Orange.TLabel")
		label.pack(anchor="w", padx=5)
		if "Password" in label_text:
			entry = PlaceholderEntry(frame, placeholder=placeholder, textvariable=var, show='*')
		else:
			entry = PlaceholderEntry(frame, placeholder=placeholder, textvariable=var)
		entry.pack(fill="x", padx=5, pady=2)

	# Debugging Checkbutton
	debugging_cb = ttk.Checkbutton(container.scrollable_frame, text="Enable Debugging", variable=debugging_var)
	debugging_cb.pack(pady=10, padx=10)

	# Setup Button
	setup_button = ttk.Button(container.scrollable_frame, text="Setup Server", command=on_submit)
	setup_button.pack(pady=20, padx=10)

	root.mainloop()

if __name__ == "__main__":
	open_gui()
