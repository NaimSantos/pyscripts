import re

def read_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: {file_name} not found!")
        return []
    except Exception as e:
        print(f"An error occurred while reading {file_name}: {e}")
        return []

def load_files():
    global tcg_current_list, ocg_current_list, traditional_current_list, worlds_current_list
    tcg_current_list = read_file("0TCG.lflist.conf")
    ocg_current_list = read_file("OCG.lflist.conf")
    traditional_current_list = read_file("Traditional.lflist.conf")
    worlds_current_list = read_file("World.lflist.conf")

    if tcg_current_list:
        print("TCG list loaded successfully.")
    if ocg_current_list:
        print("OCG list loaded successfully.")
    if traditional_current_list:
        print("Traditional list loaded successfully.")
    if worlds_current_list:
        print("Worlds list loaded successfully.")

def get_latest_identifier(files):
    """
    Get the most recent identifier and date from a list of files.
    """
    latest_date = None
    latest_identifier = ""

    # Regular expression to capture date and identifier
    pattern = re.compile(r"#\[(\d{4}\.\d{2})\s+([A-Za-z]+)\]")

    for file_content in files:
        first_line = file_content[0]  # Assuming file_content is a list of lines
        match = pattern.match(first_line.strip())
        if match:
            date = match.group(1)
            identifier = match.group(2)
            
            # Compare dates and update if this file is more recent
            if latest_date is None or date > latest_date:
                latest_date = date
                latest_identifier = identifier

    return latest_date, latest_identifier


def generate_worlds():
    print("Option 1: Generate Worlds is executed!")
    # Step 1: Merge the contents of tcg_current_list and ocg_current_list
    merged_list = tcg_current_list + ocg_current_list
    # Step 2: Remove lines that start with "#" or "!"
    merged_list = [line for line in merged_list if not line.strip().startswith(("#", "!"))]
    # Step 3: Sort the merged list
    merged_list.sort()
    # Step 4: Remove consecutive duplicates
    merged_list = remove_consecutive_duplicates(merged_list)
    # Step 5: Remove lines with the card pattern and apply count logic
    merged_list = remove_card_duplicates(merged_list)
    # Step 6: Sort the list again by count (ascending) and card name (alphabetical)
    merged_list = sort_by_count_and_name(merged_list)
    # Step 7: Get the latest identifier and date from the files
    files = [tcg_current_list, ocg_current_list]
    latest_date, latest_identifier = get_latest_identifier(files)

    # Prepare the first two lines
    first_line = f"#[{latest_date} Worlds]\n"
    second_line = f"!{latest_date} Worlds\n"
    # Step 8: Add the identifier lines at the beginning of the merged list
    with open("World.new.lflist.conf", "w") as file:
        file.write(first_line)
        file.write(second_line)
        file.writelines(merged_list)

    print("World.new.lflist.conf has been generated, sorted, and duplicates removed.\n\n")

def remove_consecutive_duplicates(merged_list):
    """
    Remove consecutive duplicated lines in the list.
    """
    unique_list = []
    previous_line = None

    for line in merged_list:
        if line != previous_line:
            unique_list.append(line)
        previous_line = line
    
    return unique_list

def remove_card_duplicates(merged_list):
    """
    Remove duplicate card entries based on the card ID and keep the one with the lowest count.
    """
    cleaned_list = []
    card_dict = {}

    # Pattern for the card line: ID, count (0-3), and card name after "--"
    card_pattern = re.compile(r"(\d+)\s+(\d+)\s+--\s*(.*)")

    for line in merged_list:
        match = card_pattern.match(line.strip())
        if match:
            card_id = int(match.group(1))
            count = int(match.group(2))
            card_name = match.group(3)

            # Check if we've seen this card ID before
            if card_id in card_dict:
                # If current count is lower, replace the previous line
                if card_dict[card_id][0] > count:
                    card_dict[card_id] = (count, line)
            else:
                # Store the first occurrence of the card ID
                card_dict[card_id] = (count, line)
        else:
            # If the line doesn't match the card pattern, add it as is
            cleaned_list.append(line)

    # Add only the lines with the lowest count for each card ID
    cleaned_list.extend([entry[1] for entry in sorted(card_dict.values(), key=lambda x: x[0])])

    return cleaned_list

def sort_by_count_and_name(merged_list):
    """
    Sort the list first by count (0, 1, 2, 3), then by card name alphabetically,
    and add group headers for 0, 1, and 2 counts.
    """
    sorted_list = []

    # Pattern for the card line: ID, count (0-3), and card name after "--"
    card_pattern = re.compile(r"(\d+)\s+(\d+)\s+--\s*(.*)")

    # Sorting using a custom key: first by count, then by card name
    for line in merged_list:
        match = card_pattern.match(line.strip())
        if match:
            count = int(match.group(2))
            card_name = match.group(3)
            sorted_list.append((count, card_name, line))
        else:
            sorted_list.append((float('inf'), line.strip(), line))  # For non-card lines, place at the end
    
    # Sorting first by count, then by card name
    sorted_list.sort(key=lambda x: (x[0], x[1]))

    # Prepare to insert group headers
    final_list = []
    added_forbidden = added_limited = added_semi_limited = False

    for entry in sorted_list:
        count, card_name, line = entry

        if count == 0 and not added_forbidden:
            final_list.append("#Forbidden\n")
            added_forbidden = True
        elif count == 1 and not added_limited:
            final_list.append("#Limited\n")
            added_limited = True
        elif count == 2 and not added_semi_limited:
            final_list.append("#Semi-Limited\n")
            added_semi_limited = True

        final_list.append(line)

    return final_list

import re

def generate_tcg_traditional_list():
    print("Option 2: Generate TCG Traditional List is executed!")

    # Step 1: Read the tcg_current_list file and process its contents
    traditional_list = tcg_current_list.copy()

    # Step 2: Change count 0 to count 1
    traditional_list = [line if not line.strip() or not re.match(r"^\d+\s+0\s+--", line.strip()) else re.sub(r"(\d+\s+)0", r"\1 1", line) for line in traditional_list]

    # Step 3: Sort the lines, first by count, then by card name
    card_pattern = re.compile(r"(\d+)\s+(\d+)\s+--\s*(.*)")
    sorted_list = []

    for line in traditional_list:
        match = card_pattern.match(line.strip())
        if match:
            count = int(match.group(2))
            card_name = match.group(3)
            sorted_list.append((count, card_name, line))
        else:
            sorted_list.append((float('inf'), line.strip(), line))  # Non-card lines placed at the end

    # Sorting by count and then by card name
    sorted_list.sort(key=lambda x: (x[0], x[1]))

    # Step 4: Remove lines that start with "#" or "!"
    sorted_list = [line for _, _, line in sorted_list if not line.strip().startswith(("#", "!"))]

    # Step 5: Get the identifier from tcg_current_list (the first 2 lines)
    first_line = tcg_current_list[0].strip()
    second_line = tcg_current_list[1].strip()

    # Step 6: Prepare to write the output file with the identifier lines
    first_line = re.sub(r"(TCG|OCG)", "Traditional", first_line)  # Change identifier to "Worlds"
    second_line = re.sub(r"(TCG|OCG)", "Traditional", second_line)  # Same for the second line

    # Prepare the first two lines with the identifier changed to "Worlds"
    with open("Traditional.new.lflist.conf", "w") as file:
        file.write(f"{first_line}\n")
        file.write(f"{second_line}\n")

        # Step 7: Add a line before the first count 1 with "#Limited" and the count 2 with "#Semi-Limited"
        added_limited = False
        added_semi_limited = False
        for line in sorted_list:
            if re.match(r"^\d+\s+1\s+--", line.strip()) and not added_limited:
                file.write("#Limited\n")
                added_limited = True
            if re.match(r"^\d+\s+2\s+--", line.strip()) and not added_semi_limited:
                file.write("#Semi-Limited\n")
                added_semi_limited = True
            file.write(f"{line}\n")
    # Step 8: Remove any extra empty lines from the output file
    with open("Traditional.new.lflist.conf", "r") as file:
        lines = file.readlines()

    # Remove empty lines (lines that contain only whitespace)
    lines = [line for line in lines if line.strip()]

    # Write the cleaned lines back to the file
    with open("Traditional.new.lflist.conf", "w") as file:
        file.writelines(lines)
    print("Traditional.new.lflist.conf has been generated, count adjusted, sorted, and commented.\n\n")



def main():
    load_files()  # Load the files before the user selects an option

    while True:
        print("\nSelect an option:")
        print("1. Generate Worlds Forbidden/Limited list")
        print("2. Generate TCG Traditional list")
        print("3. feature to be implemented (not in use for now)")
        print("4. Exit")

        try:
            choice = int(input("Enter your choice (1/2/3/4): "))

            if choice == 1:
                generate_worlds()
            if choice == 2:
                generate_tcg_traditional_list()
            elif choice == 3:
                print("This option is not in use currently.")
            elif choice == 4:
                print("Exiting the script.")
                break
            else:
                print("Invalid choice. Please choose a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()