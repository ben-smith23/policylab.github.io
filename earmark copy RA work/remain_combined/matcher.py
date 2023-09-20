import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import numpy as np

# Load the CSV files
remain_df = pd.read_csv('remain_23_3', encoding='ISO-8859-1')
senate_coded_23_df = pd.read_csv('senate_coded_23', encoding='ISO-8859-1')

# Function to calculate the number of similar words between two strings
def similar_words_count(str1, str2):
    return len(set(str1.split()) & set(str2.split()))

# File paths
remain_23_3_copy_path = 'remain_23_3_copy.csv'
combined_23_4_path = 'combined_23_4.csv'

# If remain_23_3_copy doesn't exist, create it as a copy of remain_23_3
if not os.path.exists(remain_23_3_copy_path):
    remain_df.to_csv(remain_23_3_copy_path, index=False)

# Load remain_23_3_copy into a dataframe for use in the GUI
remain_23_3_copy_df = pd.read_csv(remain_23_3_copy_path, encoding='ISO-8859-1')

# Function to handle the combination and saving process
def handle_match():
    # Get the selected row from senate_coded_23
    selected_index = listbox.curselection()
    if selected_index:
        selected_match = matched_rows.iloc[selected_index[0]]
        
        # Identify columns that are present in both dataframes
        common_cols = test_row.index.intersection(selected_match.index).to_list()
        
        # For common columns, add .x and .y suffixes, for unique columns, retain them as-is
        combined_series = pd.concat([
            test_row[common_cols].add_suffix('.x'),
            selected_match[common_cols].add_suffix('.y'),
            test_row.drop(common_cols),
            selected_match.drop(common_cols)
        ])
        
        # Remove duplicate columns (st, subcommittee, and last) with .y suffix
        for col in ['st.y', 'subcommittee.y', 'last.y']:
            if col in combined_series:
                combined_series = combined_series.drop(col)
        
        # Append the combined row to combined_23_4
        with open(combined_23_4_path, 'a', encoding='ISO-8859-1', newline='') as f:
            # Check if file is empty and write header if necessary
            if f.tell() == 0:
                combined_series.to_frame().T.to_csv(f, header=True, index=False)
            else:
                combined_series.to_frame().T.to_csv(f, header=False, index=False)
        
        # Remove the matched row from remain_23_3_copy and save
        global remain_23_3_copy_df
        remain_23_3_copy_df = remain_23_3_copy_df.drop(test_row.name)
        remain_23_3_copy_df.to_csv(remain_23_3_copy_path, index=False, encoding='ISO-8859-1')
        
        # Update the GUI to show the next row
        update_gui()

# Function to skip the current row
def skip_row():
    global remain_23_3_copy_df
    # Append the skipped row to the end of the DataFrame
    skipped_row = remain_23_3_copy_df.iloc[0]
    remain_23_3_copy_df = pd.concat([remain_23_3_copy_df.iloc[1:], skipped_row.to_frame().T])
    # Save the updated DataFrame
    remain_23_3_copy_df.to_csv(remain_23_3_copy_path, index=False, encoding='ISO-8859-1')
    # Update the GUI to show the next row
    update_gui()

# Function to compute Jaccard similarity between two strings
def jaccard_similarity(s1, s2):
    # If any string is NaN or None, return 0
    if pd.isna(s1) or pd.isna(s2):
        return 0
    words_1 = set(s1.split())
    words_2 = set(s2.split())
    intersection = len(words_1.intersection(words_2))
    union = len(words_1.union(words_2))
    return intersection / union if union != 0 else 0

# Function to compute combined similarity for recipient and project
def combined_similarity(row, ref_recipient, ref_project):
    combined_ref_string = str(ref_recipient) + " " + str(ref_project)
    combined_row_string = str(row['recipient']) + " " + str(row['project'])
    return jaccard_similarity(combined_row_string, combined_ref_string)

# Function to update the GUI content
def update_gui():
    global test_row
    global matched_rows
    
    # Load the next row
    if not remain_23_3_copy_df.empty:
        test_row = remain_23_3_copy_df.iloc[0]
        
        matched_rows = senate_coded_23_df[
            (senate_coded_23_df["last"] == test_row["last"]) &
            (senate_coded_23_df["st"] == test_row["st"]) &
            (senate_coded_23_df["subcommittee"] == test_row["subcommittee"])
        ]
        matched_rows["similarity"] = matched_rows.apply(lambda x: combined_similarity(x, test_row['recipient'], test_row['project']), axis=1)
        matched_rows = matched_rows.sort_values(by="similarity", ascending=False).drop(columns="similarity")
        
        # Update the displayed data
        remain_label["text"] = f"Recipient: {test_row['recipient']} | Project: {test_row['project']}"
        listbox.delete(0, tk.END)
        for _, row in matched_rows.iterrows():
            listbox.insert(tk.END, f"Recipient: {row['recipient']} | Project: {row['project']}")
        
        # Update the counter
        counter_label["text"] = f"Rows Remaining: {len(remain_23_3_copy_df)}"
    else:
        remain_label["text"] = "All rows have been matched!"
        listbox.delete(0, tk.END)
        counter_label["text"] = "Rows Remaining: 0"


# Create the main window
root = tk.Tk()
root.title("Match Selection")

# Frame for remain_23_3 data
frame_remain = ttk.LabelFrame(root, text="remain_23_3 Data", padding=(10, 5))
frame_remain.pack(padx=10, pady=5, fill="x", expand=True)
remain_label = ttk.Label(frame_remain)
remain_label.pack(padx=5, pady=5, anchor="w")

# Frame for potential matches from senate_coded_23
frame_matches = ttk.LabelFrame(root, text="Potential Matches from senate_coded_23", padding=(10, 5))
frame_matches.pack(padx=10, pady=5, fill="x", expand=True)
listbox = tk.Listbox(frame_matches, height=30, selectmode=tk.SINGLE)
listbox.pack(fill="both", expand=True)

# Counter label
counter_label = ttk.Label(root, padding=(10, 5))
counter_label.pack(pady=5, anchor="center")

# Buttons
btn_next = ttk.Button(root, text="Next", command=handle_match)
btn_next.pack(pady=5, side=tk.LEFT, padx=5)
btn_skip = ttk.Button(root, text="Skip", command=skip_row)
btn_skip.pack(pady=5, side=tk.RIGHT, padx=5)

# Initialize the GUI content
update_gui()

# Run the GUI
root.mainloop()