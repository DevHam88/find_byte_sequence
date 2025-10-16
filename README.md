# 🔍 find_byte_sequence

A standalone Python tool for scanning binary files for multiple byte sequences that appear close together.  
Supports order-enforced or unordered matching, configurable proximity, and optional logging.

---

## ⚙️ Features
- Search all files in a directory (recursively).
- Detect proximity of multiple byte sequences within a fixed window.
- Enforce or ignore sequence order.
- Auto-skip massive combination counts for performance.
- Optional logging and progress updates.

---

## 🧩 Setup
1. **Install Python 3.8+** (no extra packages required).  
2. **Clone or download** this repository.
3. **Create a folder named `target/`** beside the script and place files to scan inside it.  
   > You can change this location by editing `directory_to_search` in the script.

---

## ⚙️ Configuring

Edit the configuration section at the top of `find_byte_sequences.py` to define your byte sequences and settings.

Example:
```python
sequences = [
    bytes.fromhex("4500"),
    bytes.fromhex("8200"),
    bytes.fromhex("E803"),
]
```

Add or remove sequences by adding or removing rows inside this list — any number of sequences can be used.

### Key Settings

| Setting | Default | Description |
|----------|----------|-------------|
| `sequences` | `[bytes.fromhex("4500"), bytes.fromhex("8200"), bytes.fromhex("E803")]` | Byte sequences to search for. |
| `directory_to_search` | `"./target"` | Folder to scan (relative or absolute). |
| `ENFORCE_SEQUENCE_ORDER` | `False` | Require sequences in defined order. |
| `MAX_INTER_SEQUENCE_GAP` | `12` | Max bytes allowed between sequences. |
| `MAX_COMBOS` | `10_000_000` | Skip files exceeding this combo count. |
| `SHOW_PROGRESS` | `False` | Show periodic progress messages. |
| `WRITE_LOG` | `False` | Save output logs to `/logs/`. |

---

## 🚀 Usage
Run the script:
```bash
python find_byte_sequences.py
```

Example output:
```
[Status] Script initialized successfully. Configuration loaded.
[Status] First file scanning started: arm9.bin
[Status] First file scanning complete.

arm9.bin — 2 match(es)
  [#1]  Window=12 | Ordered=YES | Offsets: [0x13C4, 0x13C8, 0x13D7]
```

If logging is enabled, results are saved to `/logs/find_byte_sequences_YYYYMMDD_HHMMSS.txt`.

---

## 🧾 Output Summary
After scanning, the script prints totals such as:
```
Total files searched:    37
Files with matches:      5
Files skipped:           2
Total matches found:     14
Average window size:     18.6 bytes
```

---

## 🛠 Notes
- All byte sequences are matched exactly as entered (little-endian if written that way) with no space characters between them.
- Works on any binary file type.
- If `./target` is missing, you’ll get a friendly warning and the script will exit safely.

---

## 📜 License
Released under the MIT License — free to use and modify with attribution.
