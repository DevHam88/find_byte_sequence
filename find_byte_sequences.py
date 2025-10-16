import os
import itertools
import time
import sys

# === Configuration ===
sequences = [
    bytes.fromhex("4500"),
    bytes.fromhex("8200"),
    bytes.fromhex("E803"),
]

# Folder to search, relative to this script
# By default, looks for a folder named "target" alongside the script.
directory_to_search = "./target"

# Require sequences to appear in the order defined above
ENFORCE_SEQUENCE_ORDER = False

# Maximum number of bytes allowed between each adjacent sequence
MAX_INTER_SEQUENCE_GAP = 12

# Derived fixed window size
FIXED_WINDOW = sum(len(s) for s in sequences) + (MAX_INTER_SEQUENCE_GAP * (len(sequences) - 1))

# Cap on how many sequence combinations per file to evaluate
MAX_COMBOS = 10_000_000  # adjust as needed

# Progress display control
SHOW_PROGRESS = False      # Set to True for progress messages
PROGRESS_INTERVAL = 500    # Show progress every N files (only if SHOW_PROGRESS is True)

# Log file control
WRITE_LOG = False            # Enable or disable writing all output to a log file
LOG_DIRECTORY = "./logs"    # Where logs will be stored (auto-created if missing)

# === Validate target directory ===
if not os.path.exists(directory_to_search):
    print(f"⚠️  Directory not found: {directory_to_search}")
    print("Please create it or update 'directory_to_search' in the script.\n")
    sys.exit(1)

# === Logging setup ===
if WRITE_LOG:
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"find_byte_sequences_{timestamp}.txt"
    log_path = os.path.join(LOG_DIRECTORY, log_filename)
    sys.stdout = open(log_path, "w", encoding="utf-8")
    sys.stderr = sys.stdout
    print(f"[Logging Enabled] Output redirected to: {log_path}\n")

# === Search setup ===
total_files = 0
files_with_matches = 0
total_matches = 0
all_window_sizes = []
skipped_files = []

start_time = time.time()

print(f"\nSearching directory: {directory_to_search}")
print(f"Number of sequences: {len(sequences)}")
print(f"Fixed window size:   {FIXED_WINDOW} bytes")
print(f"Order enforced:      {ENFORCE_SEQUENCE_ORDER}")
print(f"Max combos per file: {MAX_COMBOS:,}")
print(f"Show progress:       {SHOW_PROGRESS} (every {PROGRESS_INTERVAL} files)")
print(f"Write log:           {WRITE_LOG}")
print("-" * 60)
print("[Status] Script initialized successfully. Configuration loaded.\n")

# === Main search ===
first_file_started = False
first_file_done = False

for root, _, files in os.walk(directory_to_search):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        total_files += 1

        if not first_file_started:
            print(f"[Status] First file scanning started: {file_name}")
            first_file_started = True

        # --- Optional progress feedback ---
        if SHOW_PROGRESS and total_files % PROGRESS_INTERVAL == 0:
            elapsed = time.time() - start_time
            print(f"[Progress] Processed {total_files} files... ({elapsed:.1f}s elapsed)")

        try:
            with open(file_path, "rb") as f:
                data = f.read()

            # Find all occurrences of each sequence
            positions = {}
            for seq in sequences:
                seq_hex = seq.hex().upper()
                pos_list, start = [], 0
                while (pos := data.find(seq, start)) != -1:
                    pos_list.append(pos)
                    start = pos + 1
                positions[seq_hex] = pos_list

            # Skip files missing any sequence
            if any(len(v) == 0 for v in positions.values()):
                continue

            # Estimate total combinations for this file
            combo_count = 1
            for pos_list in positions.values():
                combo_count *= len(pos_list)

            # Skip files with too many combinations
            if combo_count > MAX_COMBOS:
                relative_path = os.path.relpath(file_path, directory_to_search)
                print(f"[Skip] {relative_path} — {combo_count:,} combinations (skipped for performance)")
                skipped_files.append((relative_path, combo_count))
                continue

            matches = []
            for combo in itertools.product(*positions.values()):
                # Check order (if required)
                if ENFORCE_SEQUENCE_ORDER and combo != tuple(sorted(combo)):
                    continue

                window = max(combo) - min(combo)
                if window <= FIXED_WINDOW:
                    matches.append((combo, window))
                    all_window_sizes.append(window)

            # Output file results
            if matches:
                files_with_matches += 1
                total_matches += len(matches)
                matches.sort(key=lambda m: m[1])
                relative_path = os.path.relpath(file_path, directory_to_search)
                print(f"\n{relative_path} — {len(matches)} match(es)")
                for i, (combo, window) in enumerate(matches, start=1):
                    is_ordered = combo == tuple(sorted(combo))
                    order_status = "YES" if is_ordered else "NO"
                    offs = ", ".join(f"0x{x:X}" for x in combo)
                    print(f"  [#{i:>2}]  Window={window:>5} | Ordered={order_status:<3} | Offsets: [{offs}]")

            # First file completed successfully
            if first_file_started and not first_file_done:
                print("[Status] First file scanning complete.\n")
                first_file_done = True

        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")

# --- Completion and summary ---
elapsed_total = time.time() - start_time
print(f"\nAll files processed in {elapsed_total:.2f} seconds.\n")

print("=" * 60)
print("Search Summary")
print("=" * 60)
print(f"Total files searched:    {total_files}")
print(f"Files with matches:      {files_with_matches}")
print(f"Files skipped:           {len(skipped_files)}")
print(f"Total matches found:     {total_matches}")
if all_window_sizes:
    avg_window = sum(all_window_sizes) / len(all_window_sizes)
    min_window = min(all_window_sizes)
    max_window = max(all_window_sizes)
    print(f"Average window size:     {avg_window:.2f} bytes")
    print(f"Smallest window found:   {min_window} bytes")
    print(f"Largest window found:    {max_window} bytes")
else:
    print("No matches found.")
print("-" * 60)
print("Configuration Used")
print("-" * 60)
print(f"Directory searched:      {directory_to_search}")
print(f"Number of sequences:     {len(sequences)}")
print(f"Fixed window size:       {FIXED_WINDOW} bytes")
print(f"Order enforced:          {ENFORCE_SEQUENCE_ORDER}")
print(f"Max inter-sequence gap:  {MAX_INTER_SEQUENCE_GAP} bytes")
print(f"Max combos per file:     {MAX_COMBOS:,}")
print(f"Show progress:           {SHOW_PROGRESS} (every {PROGRESS_INTERVAL} files)")
print(f"Write log:               {WRITE_LOG}")
print("=" * 60)

# --- Skipped file summary ---
if skipped_files:
    print("\nSkipped Files (due to excessive combination counts)")
    print("-" * 60)
    print(f"Total skipped: {len(skipped_files)} file(s)")
    for path, count in skipped_files:
        print(f"  {path} — {count:,} combinations")
    print("=" * 60)

# --- Close log file if used ---
if WRITE_LOG:
    sys.stdout.close()
