import sqlite3
import os

def get_database_card_names(database_path):
    """Reads the card names from the database and returns a dictionary of {id: name}."""
    card_names = {}
    try:
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM texts")
            for card_id, card_name in cursor.fetchall():
                card_names[card_id] = card_name
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
    return card_names

def update_script_files(scripts_path, card_names):
    """Updates the Lua script files with the correct card names and fixes comment formatting."""
    updated_count = 0  # Counter for changed scripts

    for file_name in os.listdir(scripts_path):
        if file_name.startswith("c") and file_name.endswith(".lua"):
            card_id_str = file_name[1:-4]  # Extract the card ID from the file name
            try:
                card_id = int(card_id_str)
                if card_id in card_names:
                    script_path = os.path.join(scripts_path, file_name)
                    with open(script_path, 'r', encoding='utf-8') as script_file:
                        lines = script_file.readlines()
                    
                    changed = False  # Track if the script needs to be updated
                    
                    # Check and fix card name in the second line
                    if len(lines) >= 2 and lines[1].startswith("--"):
                        current_name = lines[1][2:].strip()
                        correct_name = card_names[card_id]
                        if current_name != correct_name:
                            lines[1] = f"--{correct_name}\n"
                            changed = True
                    
                    # Remove spaces after "--" in all comment lines
                    for i, line in enumerate(lines):
                        if line.strip().startswith("-- "):  # Check for space after "--"
                            lines[i] = line.replace("-- ", "--", 1)
                            changed = True

                    # Write changes if any were made
                    if changed:
                        with open(script_path, 'w', encoding='utf-8') as script_file:
                            script_file.writelines(lines)
                        updated_count += 1
                        print(f"Updated {file_name}.")
                else:
                    print(f"Card ID {card_id} not found in the database. Skipping file.")
            except ValueError:
                print(f"Invalid card ID in file name {file_name}. Skipping file.")

    print(f"\nTotal scripts updated: {updated_count}")

def main():
    database_path = input("Enter the path to the directory containing 'cards.delta.cdb': ").strip()
    database_path = os.path.join(database_path, "cards.delta.cdb")

    if not os.path.isfile(database_path):
        print(f"Database file not found: {database_path}")
        return

    scripts_path = input("Enter the path to the directory containing the Lua script files: ").strip()

    if not os.path.isdir(scripts_path):
        print(f"Scripts directory not found: {scripts_path}")
        return

    print("Reading card names from the database...")
    card_names = get_database_card_names(database_path)

    if not card_names:
        print("No card names were retrieved from the database. Exiting.")
        return

    print("Updating script files...")
    update_script_files(scripts_path, card_names)
    print("Finished updating scripts.")

if __name__ == "__main__":
    main()
