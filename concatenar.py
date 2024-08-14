# Retry concatenating the files and saving as a new Excel file

# Load the four Excel files provided by the user
file1_path = '/mnt/data/aro00.xlsx'
file2_path = '/mnt/data/aro01.xlsx'
file3_path = '/mnt/data/aro02.xlsx'
file4_path = '/mnt/data/aro03.xlsx'

# Read all four Excel files into DataFrames
df1 = pd.read_excel(file1_path)
df2 = pd.read_excel(file2_path)
df3 = pd.read_excel(file3_path)
df4 = pd.read_excel(file4_path)

# Concatenate the DataFrames
combined_df = pd.concat([df1, df2, df3, df4], ignore_index=True)

# Save the concatenated DataFrame to a new Excel file
output_filename = '/mnt/data/aro10.xlsx'
combined_df.to_excel(output_filename, index=False)

output_filename
