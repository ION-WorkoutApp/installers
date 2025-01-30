# ION Workout App Installers

Welcome to the **ION Workout App** installers repository! This project provides two convenient ways to set up the ION Workout App server:

- **CLI Installer** 🔄: A command-line interface script for advanced users.
- **GUI Installer** 🔧: A graphical interface with a friendly setup wizard.

---

## Features 🌐

- **Environment Setup**: Automatically configures environment variables in a `.env` file.
- **MongoDB Integration**: Supports username, password, and database setup.
- **Docker Image Management**: Pulls necessary Docker images.
- **Custom Credentials**: Optionally auto-generate secure passwords and keys.

---

## Prerequisites ⚙️

Ensure the following software is installed:

- **Git**
- **Docker & Docker Compose**
- **Python 3.x**
- **Cloudflared (optional)**

For the GUI installer, the Python dependencies will be installed automatically.

---

## CLI Installer 🔄

The CLI installer is a Bash script that guides you through the setup process via terminal prompts.

### One-Line Command to Install and Run

Run this single command to execute the CLI installer:

```bash
bash <(curl -s https://raw.githubusercontent.com/ION-WorkoutApp/installers/main/setup.sh)
```

### What It Does
1. Fetches the installer script from the repository.
2. Executes it directly in your terminal.

---

## GUI Installer 🔧

The GUI installer provides a user-friendly interface for setting up the ION Workout App server.

Simply download and run [the setup file](GUI/dist/server_setup)

---

## Development ⚖️

### Building the GUI Installer

The GUI installer can be packaged into a standalone executable using **PyInstaller**:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ION-WorkoutApp/installers.git
   cd installers
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r GUI/requirements.txt
   ```

4. **Build the executable**:
   ```bash
   pyinstaller --onefile --noconsole server_setup.py
   ```
   The executable will be created in the `dist` folder

5. **Deactivate the virtual environment** (optional):
   ```bash
   deactivate
   ```

---

## Troubleshooting 🚫

- **Docker Not Found**:
  - Ensure Docker is installed and running.
  - Verify Docker Compose compatibility.

- **Python Errors**:
  - Ensure Python 3.x is installed.

---

## Contributing ✨

Contributions are welcome! Feel free to submit issues or pull requests.

---

## License 🔒

This project is licensed under the MIT License.
