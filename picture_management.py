import os
from PIL import Image

def option_one():
    print("Option 1 selected: Remove duplicated pics (keeping PNG).")
    # Directory containing images
    subdirectory = "pics"

    if not os.path.exists(subdirectory):
        print(f"The directory '{subdirectory}' does not exist. Please ensure it is present in the current working directory.")
        return

    # Scan for image files
    files = os.listdir(subdirectory)
    png_files = set(f[:-4] for f in files if f.lower().endswith('.png'))
    jpg_files = set(f[:-4] for f in files if f.lower().endswith('.jpg'))

    # Find duplicates and remove jpg
    duplicates = png_files & jpg_files

    for duplicate in duplicates:
        jpg_path = os.path.join(subdirectory, duplicate + ".jpg")
        try:
            os.remove(jpg_path)
            print(f"Removed duplicate: {jpg_path}")
        except OSError as e:
            print(f"Error deleting file {jpg_path}: {e}")

    print("Duplicate removal process completed.")

def option_two():
    print("Option 2 selected: Dimension checker.")
    # Directory containing images
    subdirectory = "pics"
    output_file = "pics_to_generate.ydk"

    if not os.path.exists(subdirectory):
        print(f"The directory '{subdirectory}' does not exist. Please ensure it is present in the current working directory.")
        return

    target_dimensions = [(177, 254), (254, 177)]

    valid_files = []

    for file_name in os.listdir(subdirectory):
        if not file_name.lower().endswith(('.png', '.jpg')):
            continue

        stem, _ = os.path.splitext(file_name)
        if not stem.isdigit() or int(stem) >= 120120120:
            continue

        file_path = os.path.join(subdirectory, file_name)
        try:
            with Image.open(file_path) as img:
                dimensions = img.size
                if dimensions in target_dimensions:
                    valid_files.append(stem)
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")

    with open(output_file, "w") as f:
        for stem in sorted(valid_files):
            f.write(f"{stem}\n")

    print(f"Dimension check completed. Results written to '{output_file}'.")

def option_three():
    print("Option 3 selected: Performing task for Option 3.")
    # Example functionality for Option 3
    print("Task for Option 3 completed successfully.")

def main():
    while True:
        print("\nPlease select an option:")
        print("1. Remove duplicated pics (keeping PNG)")
        print("2. Dimension checker")
        print("3. Execute Option 3")
        print("4. Exit")

        try:
            choice = int(input("Enter your choice (1-4): "))

            if choice == 1:
                option_one()
            elif choice == 2:
                option_two()
            elif choice == 3:
                option_three()
            elif choice == 4:
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
