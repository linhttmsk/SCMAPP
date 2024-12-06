import pandas
import xlwings
# Load the Excel files
file1 = "file1.xlsx"
file2 = "file2.xlsx"
config_file = "config.xlsx"
with xlwings.App() as App:
    _ = App.books.open('config.xlsx')
    rng = App.books['config.xlsx'].sheets['GroupCondition'].tables['tblConfig'].range
    group_combination_logic = App.books['config.xlsx'].sheets['GroupCondition'].range('C3').value
    config: pandas.DataFrame = rng.expand().options(pandas.DataFrame).value

#df1 = pandas.read_excel(file1)
#df2 = pandas.read_excel(file2)


# Group combination logic
#group_combination_logic = "lambda g1, g2, g3, g4: g1 or (g2 and (g3 or g4))"

# Initialize results
group_results = {}

# Step 1: Evaluate Each Group
for group, group_data in config.groupby("Group"):
    group_data = group_data.sort_values(by="Sequence")
    
    # Align data using the keys
    key_1 = group_data.iloc[0]["Key Column in Data 1"]
    key_2 = group_data.iloc[0]["Key Column in Data 2"]
    
    if key_1 not in df1.columns or key_2 not in df2.columns:
        group_results[group] = pd.Series(False, index=df1.index)  # Mark as False for missing keys
        continue
    
    aligned_df = pd.merge(df1, df2, left_on=key_1, right_on=key_2, how="left")
    
    # Evaluate each condition in the group
    group_condition = None
    for _, row in group_data.iterrows():
        col_1 = row["Column in Data 1"]
        col_2 = row["Column in Data 2"]
        operator = row["Operator"]
        logic = row["Logic"]

        # Build the condition
        if operator == "==":
            condition = aligned_df[col_1] == aligned_df[col_2]
        elif operator == "!=":
            condition = aligned_df[col_1] != aligned_df[col_2]
        elif operator == "<":
            condition = aligned_df[col_1] < aligned_df[col_2]
        elif operator == ">":
            condition = aligned_df[col_1] > aligned_df[col_2]
        else:
            condition = pd.Series(False, index=aligned_df.index)
        
        # Combine with previous conditions using logic
        if group_condition is None:
            group_condition = condition
        elif logic == "AND":
            group_condition = group_condition & condition
        elif logic == "OR":
            group_condition = group_condition | condition
    
    # Store the group result
    group_results[group] = group_condition

# Step 2: Combine Groups Using Group Logic
try:
    group_combination_func = eval(group_combination_logic)  # Convert to a function
    final_result = group_combination_func(
        group_results.get(1, pd.Series(False, index=df1.index)),
        group_results.get(2, pd.Series(False, index=df1.index)),
        group_results.get(3, pd.Series(False, index=df1.index)),
        group_results.get(4, pd.Series(False, index=df1.index)),
    )
except Exception as e:
    final_result = pd.Series(False, index=df1.index)  # Default to False if logic fails
    print(f"Error in group combination logic: {e}")

# Step 3: Identify and Report Mismatches
mismatched = ~final_result
if mismatched.any():
    mismatched_rows = df1.loc[mismatched].to_dict("records")
else:
    mismatched_rows = []

# Output Results
print("Mismatched Rows:", mismatched_rows)
