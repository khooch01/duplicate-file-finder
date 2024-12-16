# Duplicate File Finder

Duplicate File Finder is a Python application that helps you identify and remove duplicate files from your system. It provides an easy-to-use graphical interface for selecting folders and scanning them for duplicates.

## Features
- Add multiple folders to scan for duplicate files.
- Detect duplicate files by comparing file content using hashing (MD5).
- Display a list of duplicate files with details such as file path and size.
- Allow users to delete selected duplicate files directly from the application.

## Technologies Used
- **Python**: Programming language.
- **Tkinter**: For creating the graphical user interface.
- **Hashlib**: For generating hash values of files to identify duplicates.

## Prerequisites
- Python 3.8 or higher.
- Required Python packages:
  - `tkinter`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/khooch/duplicate-file-finder.git
   ```
2. Install any missing dependencies if necessary.

## Usage
1. Run the application:
   ```bash
   py main.py
   ```
2. Use the interface to add folders to the list of folders to scan.
3. Click the **Scan** button to search for duplicate files.
4. Review the list of duplicates and delete selected files if necessary.

## Screenshots
![image](https://github.com/user-attachments/assets/0f6a9ad6-e24b-4b09-a88f-aebabf00261c)


## How It Works
1. **File Hashing**: The app calculates the MD5 hash of each file in the selected folders.
2. **Comparison**: Files with matching hash values are identified as duplicates.
3. **Interface**: Users can view duplicates, select files to delete, and clear folders for a new scan.

## Future Enhancements
- Add support for advanced filters (e.g., file type, size).
- Improve performance for large directories.
- Save scan reports to a file.

## Contributing
Contributions are welcome! Feel free to fork this repository and submit pull requests.


## Contact
For issues or suggestions, contact:
- Email: khooch695@gmail.com
