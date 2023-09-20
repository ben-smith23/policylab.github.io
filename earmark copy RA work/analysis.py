import pandas as pd
import chardet
import io

# Detect encoding for "enacted FY23 FINAL FINAL.csv"
with open("enacted FY23 FINAL FINAL.csv", 'rb') as f:
    result_enacted = chardet.detect(f.read())
encoding_enacted = result_enacted['encoding']

# Detect encoding for "senate coded request 22-24 addresses.csv"
with open("senate coded request 22-24 addresses.csv", 'rb') as f:
    result_coded = chardet.detect(f.read())
encoding_coded = result_coded['encoding']

# Read the file as binary, then decode with error replacement
with open("senate coded request 22-24 addresses.csv", 'rb') as f:
    content = f.read().decode(encoding_coded, errors='replace')

# Use StringIO to convert the decoded string content to a file-like object so it can be read into a DataFrame
senate_coded_23 = pd.read_csv(io.StringIO(content))

# Read the senate_enacted_23 dataframe with detected encoding
senate_enacted_23 = pd.read_csv("enacted FY23 FINAL FINAL.csv", encoding=encoding_enacted)

# Filter dataframes
senate_enacted_23 = senate_enacted_23[senate_enacted_23['chamber'].str.contains('S') & 
                                      (senate_enacted_23['origination'].str.contains('S') | 
                                       senate_enacted_23['origination'].str.contains('B'))]
senate_coded_23 = senate_coded_23[senate_coded_23['FY'].str.contains('FY2023')]

# Rename columns
senate_enacted_23 = senate_enacted_23.rename(columns={'total': 'amount', 'state': 'st'})

# Mapping dictionary
mapping_dict = {
    "Agriculture, Rural Development, Food and Drug Administration, and Related Agencies": "AG",
    "Commerce, Justice, Science, and Related Agencies": "CJS",
    "Energy and Water Development": "EW",
    "Financial Services and General Government": "FSGG",
    "Homeland Security": "HS",
    "Interior, Environment, and Related Agencies": "Interior",
    "Labor, Health and Human Services, Education, and Related Agencies": "LHHS",
    "Military Construction, Veterans Affairs, and Related Agencies": "MilCon VA",
    "Transportation, Housing and Urban Development, and Related Agencies": "THUD"
}

# Apply mapping
senate_coded_23['subcommittee'] = senate_coded_23['subcommittee'].map(mapping_dict).fillna(senate_coded_23['subcommittee'])

# Merge dataframes
combined_23 = pd.merge(senate_enacted_23, senate_coded_23, on=["last", "st", "subcommittee", "recipient", "amount"], how='inner')
combined_23 = combined_23.drop_duplicates(subset=['id', 'last'])

remain_23 = senate_enacted_23.merge(combined_23[['id']], on='id', how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

combined_23_1 = pd.merge(remain_23, senate_coded_23, on=["last", "st", "subcommittee", "recipient", "location"], how='inner')
combined_23_1 = combined_23_1.drop_duplicates(subset=['id', 'last'])

remain_23_1 = remain_23.merge(combined_23_1[['id']], on='id', how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

combined_23_2 = pd.merge(remain_23_1, senate_coded_23, on=["last", "st", "subcommittee", "recipient"], how='inner')
combined_23_2 = combined_23_2.drop_duplicates(subset=['id', 'last'])

remain_23_2 = remain_23_1.merge(combined_23_2[['id']], on='id', how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

# Print number of observations in each dataframe
print(f"Number of observations in senate_enacted_23: {senate_enacted_23.shape[0]}")
print(f"Number of observations in senate_coded_23: {senate_coded_23.shape[0]}")
print(f"Number of observations in combined_23: {combined_23.shape[0]}")
print(f"Number of observations in remain_23: {remain_23.shape[0]}")
print(f"Number of observations in combined_23_1: {combined_23_1.shape[0]}")
print(f"Number of observations in remain_23_1: {remain_23_1.shape[0]}")
print(f"Number of observations in combined_23_2: {combined_23_2.shape[0]}")
print(f"Number of observations in remain_23_2: {remain_23_2.shape[0]}")