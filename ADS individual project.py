import pandas as pd
import heapq # For min-heap in Top N

# --- Custom Data Structure: EmissionNode Class ---
class EmissionNode:
    """
    Represents a single year's CO2 emission data for a country within a linked list.
    Attributes:
        year (int): The year of the emission data.
        emission (float): The total CO2 emission for that year.
        next (EmissionNode): Pointer to the next EmissionNode in the linked list.
    """
    def __init__(self, year: int, emission: float):
        self.year = year
        self.emission = emission
        self.next = None

# --- Custom Data Structure: EmissionLinkedList Class ---
class EmissionLinkedList:
    """
    A singly linked list designed to store EmissionNodes in chronological order by year.
    Each country in the EmissionAnalyzer system will have its own instance of this list.
    """
    def __init__(self):
        self.head = None

    def insert_chronologically(self, year: int, emission: float):
        """
        Inserts a new EmissionNode into the linked list while maintaining chronological order by year.
        Time Complexity: O(Y_c) in the worst case, where Y_c is the number of years for that specific country.
                         This involves traversing the list to find the correct insertion point.
        Space Complexity: O(1) for creating the new node.
        """
        new_node = EmissionNode(year, emission)
        
        # Case 1: List is empty or new node should be the new head
        if not self.head or year < self.head.year:
            new_node.next = self.head
            self.head = new_node
            return

        # Case 2: Traverse the list to find the correct insertion point
        current = self.head
        # Iterate until we find a node whose 'next' is None or whose 'next' year is greater than or equal to the new year
        while current.next and current.next.year < year:
            current = current.next
        
        # Insert the new node
        new_node.next = current.next # New node points to what current.next was pointing to
        current.next = new_node      # Current node now points to the new node

    def find_node(self, year: int, emission: float):
        """
        Helper method to find a specific node by year and emission.
        Used primarily for ensuring accuracy in `remove_node` for undo operations.
        Time Complexity: O(Y_c) in the worst case, where Y_c is the number of years for the country.
        Space Complexity: O(1).
        """
        current = self.head
        while current:
            if current.year == year and current.emission == emission:
                return current
            current = current.next
        return None

    def remove_node(self, year: int, emission: float):
        """
        Removes a specific EmissionNode from the linked list based on year and emission.
        Used for undo operations.
        Time Complexity: O(Y_c) in the worst case, where Y_c is the number of years for the country,
                         as it involves traversing the list to find the node and its predecessor.
        Space Complexity: O(1).
        """
        if not self.head:
            return False # List is empty, nothing to remove

        # If the head node is the one to be removed
        if self.head.year == year and self.head.emission == emission:
            self.head = self.head.next
            return True

        # Traverse the list to find the node and its predecessor
        current = self.head
        while current.next:
            if current.next.year == year and current.next.emission == emission:
                current.next = current.next.next # Skip the node to be removed
                return True
            current = current.next
        return False # Node not found

    def get_all_records(self):
        """
        Retrieves all records (year and emission) from the linked list as a list of dictionaries.
        The records are already sorted chronologically due to `insert_chronologically`.
        Time Complexity: O(Y_c) where Y_c is the number of years for the country, as it iterates through all nodes.
        Space Complexity: O(Y_c) for creating and returning the list of records.
        """
        records = []
        current = self.head
        while current:
            records.append({'year': current.year, 'emission': current.emission})
            current = current.next
        return records

    def find_max_emission_year(self):
        """
        Finds the year with the maximum emission within this specific country's linked list.
        Time Complexity: O(Y_c) where Y_c is the number of years for the country, as it traverses the entire list.
        Space Complexity: O(1).
        """
        if not self.head:
            return None, None # List is empty

        max_node = self.head
        current = self.head
        while current:
            if current.emission > max_node.emission:
                max_node = current
            current = current.next
        return max_node.year, max_node.emission

    def calculate_average_emission(self):
        """
        Calculates the average emission across all years in this specific country's linked list.
        Time Complexity: O(Y_c) where Y_c is the number of years for the country, as it traverses the entire list.
        Space Complexity: O(1).
        """
        total_emission = 0.0
        count = 0
        current = self.head
        while current:
            total_emission += current.emission
            count += 1
            current = current.next
        # Avoid division by zero for empty lists
        return total_emission / count if count else 0

    def display(self):
        """
        Prints the year and emission for each node in the linked list.
        Time Complexity: O(Y_c) where Y_c is the number of years for the country, as it traverses the entire list.
        Space Complexity: O(1).
        """
        current = self.head
        if not current:
            print("    (No data for this country)")
            return
        while current:
            print(f"    Year: {current.year}, Emission: {current.emission:.2f} Mt")
            current = current.next

# --- Main System Class: EmissionAnalyzer ---
class EmissionAnalyzer:
    """
    A system designed to analyze and interact with CO2 emission data from African countries.
    It integrates various custom and built-in data structures for efficient operations:
    - Hash Table (Python dict) for `country_emission_data`: Maps country names to their EmissionLinkedList.
    - Hash Table (Python dict) for `global_yearly_totals`: Stores total emissions for each year across all countries.
    - Linked Lists (EmissionLinkedList): Stores chronological emission records for individual countries.
    - Min-Heap (Python's `heapq` module): Used for efficiently finding the top N emitting countries.
    - Stack (Python list): Implemented as `undo_stack` to support rolling back the last insertion.
    """
    def __init__(self, file_path: str):
        self.country_emission_data = {}  # Hash table: country_name -> EmissionLinkedList
        self.global_yearly_totals = {}   # Hash table: year -> total_emission_across_all_countries
        self.undo_stack = []             # Stack (list) to store (operation_type, country, year, emission) for undo

        # The data loading is performed once during initialization
        self._load_data(file_path)
        self.file_path = file_path # Storing file path for potential re-reads (e.g., for 'sector' if needed)

    def _load_data(self, file_path: str):
        """
        Loads data from the specified CSV file into the custom data structures.
        This is an initialization step executed once when `EmissionAnalyzer` is created.
        Time Complexity: O(N), where N is the total number of records in the CSV file.
                         Each record involves:
                         - Reading a row from the Pandas DataFrame (O(1) average).
                         - Hash table lookup/insertion for country (O(1) average).
                         - Linked list insertion (`insert_chronologically`) into the country's list.
                           While a single insertion can be O(Y_c), summing over all insertions means each
                           node is effectively visited a constant number of times during its insertion path,
                           leading to an amortized O(N) for all linked list insertions combined.
                         - Hash table update for `global_yearly_totals` (O(1) average).
        Space Complexity: O(N) for storing all `EmissionNode`s across all `EmissionLinkedList` instances.
                          O(D_y) for `global_yearly_totals` (where D_y = number of distinct years).
        """
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return

        print("Loading data into custom data structures...")
        for index, row in df.iterrows():
            try:
                country = row["Country"]
                year = int(row["Year"])
                emission = float(row["Total CO2 Emission excluding LUCF (Mt)"])

                # Insert into country_emission_data (hash table of linked lists)
                if country not in self.country_emission_data:
                    self.country_emission_data[country] = EmissionLinkedList()
                self.country_emission_data[country].insert_chronologically(year, emission)

                # Update global_yearly_totals (hash table)
                self.global_yearly_totals[year] = self.global_yearly_totals.get(year, 0.0) + emission

            except (ValueError, KeyError) as e:
                print(f"  Skipping row {index} due to invalid data: {row.to_dict()} - Error: {e}")
                continue
        print("Data loading complete.")

    # --- 1. Search Emissions by Country ---
    def search_emissions_by_country(self, country_name: str):
        """
        Retrieves and displays all emissions records for a specific country.
        Time Complexity: O(1) average for hash table lookup (`self.country_emission_data.get(country_name)`).
                         Then, O(Y_c) to traverse the linked list and collect records,
                         where Y_c is the number of years for the given country.
        Space Complexity: O(Y_c) for storing the list of records before returning it.
        """
        print(f"\n--- Searching Emissions for {country_name} ---")
        emission_list = self.country_emission_data.get(country_name)
        if emission_list:
            emission_list.display() # Display directly from linked list
            return emission_list.get_all_records() # Return list of records for external use
        else:
            print(f"No emission data found for '{country_name}'.")
            return []

    # --- 2. Total Emissions Per Year ---
    def get_total_emissions_per_year(self, year: int):
        """
        Computes and displays the total CO₂ emissions by year across all countries.
        Time Complexity: O(1) average for hash table lookup (`self.global_yearly_totals.get(year)`).
        Space Complexity: O(1) for the returned value.
        """
        print(f"\n--- Total Emissions for Year {year} ---")
        total = self.global_yearly_totals.get(year)
        if total is not None:
            print(f"Total CO₂ emissions for {year}: {total:.2f} Mt")
            return total
        else:
            print(f"No global emission data found for year {year}.")
            return None

    # --- 3. Top N Emitting Countries ---
    def get_top_n_emitting_countries(self, year: int, n: int):
        """
        Returns and displays countries with the highest emissions for a selected year.
        Uses a min-heap to efficiently find the top N.
        Time Complexity: O(C) to gather all countries' emissions for the specified year (C = number of countries).
                         For each country, finding the year in its linked list takes O(Y_c) in worst case.
                         Then, O(C * log N) for heap operations (C insertions/replacements into a heap of size N).
                         Overall: O(C + C log N) = O(C log N) if fetching data for a specific year is optimized,
                         or O(N_total_records + C log N) if not optimized. The current implementation for fetching
                         year-specific data involves traversing each country's linked list to find the year, which sums
                         up to $O(N_{total\_records})$ in the worst case for that part. Then $O(C \log N)$.
                         More tightly, the iteration over `all_countries_for_year` is $O(C \times \text{AvgYearsPerCountry})$.
                         The dominant factor will be the heap operations for most realistic scenarios.
        Space Complexity: O(N) for the min-heap.
        """
        if n <= 0:
            print("N must be a positive integer.")
            return []

        print(f"\n--- Top {n} Emitting Countries in {year} ---")

        # Create a list to hold (emission, country) tuples for the specified year
        all_countries_for_year = []
        for country, emission_list in self.country_emission_data.items():
            current_node = emission_list.head
            while current_node:
                if current_node.year == year:
                    all_countries_for_year.append((current_node.emission, country))
                    break # Found the year for this country, move to the next country
                current_node = current_node.next

        if not all_countries_for_year:
            print(f"No emission data found for any country in year {year}.")
            return []

        # Use a min-heap to find the top N
        min_heap = [] # Stores (emission, country) tuples
        for emission, country in all_countries_for_year:
            if len(min_heap) < n:
                heapq.heappush(min_heap, (emission, country)) # Add to heap if less than N items
            elif emission > min_heap[0][0]: # If current emission is greater than the smallest in the heap
                heapq.heapreplace(min_heap, (emission, country)) # Remove smallest, add current

        # Extract elements from the heap and sort in descending order for display
        top_n = sorted([item for item in min_heap], key=lambda x: x[0], reverse=True)

        if not top_n:
            print("No data available to determine top emitters (after filtering for year).")
        for rank, (emission, country) in enumerate(top_n):
            print(f"  {rank+1}. {country}: {emission:.2f} Mt")
        return top_n

    # --- 4. Emissions by Sector (Conceptual due to data limitation) ---
    def aggregate_emissions_by_sector(self, sector_column_name: str = None):
        """
        Filters and aggregates emissions based on sectors.
        NOTE: The provided CSV ('co2 Emission Africa (3).csv') does NOT contain a 'sector' column.
        This function is conceptual given the dataset. It demonstrates how it *would* be implemented
        if such a column existed in the DataFrame before data loading.
        Time Complexity: O(N) if iterating through all N original records to aggregate by sector.
        Space Complexity: O(D_s) where D_s is the number of distinct sectors.
        """
        print("\n--- Emissions by Sector ---")
        # Check if the assumed sector column exists in the original CSV
        try:
            df_check = pd.read_csv(self.file_path, nrows=0) # Read only header
            if sector_column_name is None or sector_column_name not in df_check.columns:
                print("Error: The provided CSV does not contain a 'sector' column (or the specified column name is incorrect).")
                print("This function demonstrates a concept but cannot be fully executed with the current dataset.")
                print("To implement this, the input data would need a 'sector' column (e.g., 'Agriculture', 'Energy', 'Industry').")
                return {}
        except Exception as e:
            print(f"Error checking CSV columns: {e}. Ensure file path is correct.")
            return {}
        
        # If a sector column exists and is valid, proceed with aggregation (re-reading data)
        df_full = pd.read_csv(self.file_path)
        sector_emissions_sum = {}

        for _, row in df_full.iterrows():
            try:
                sector = row[sector_column_name]
                emission = float(row["Total CO2 Emission excluding LUCF (Mt)"])
                if sector: # Ensure sector is not empty/null
                    sector_emissions_sum[sector] = sector_emissions_sum.get(sector, 0.0) + emission
            except (KeyError, ValueError) as e:
                # Handle cases where sector column might be missing in some rows or emission is invalid
                continue
        
        if not sector_emissions_sum:
            print("No sector data aggregated.")
            return {}

        for sector, total in sector_emissions_sum.items():
            print(f"  {sector}: {total:.2f} Mt")
        return sector_emissions_sum


    # --- 5. Emissions Trend for a Country ---
    def get_emissions_trend_for_country(self, country_name: str):
        """
        Returns and displays the emissions trend (sorted by year) for a specific country.
        The data is already chronologically sorted within the EmissionLinkedList.
        Time Complexity: O(1) average for hash table lookup to find the country's linked list.
                         Then, O(Y_c) to traverse the linked list and collect records,
                         where Y_c is the number of years for the given country.
        Space Complexity: O(Y_c) for the list of records returned.
        """
        print(f"\n--- Emission Trend for {country_name} ---")
        emission_list = self.country_emission_data.get(country_name)
        if emission_list:
            trend_data = emission_list.get_all_records() # Already sorted by year
            if not trend_data:
                print(f"  No detailed trend data for {country_name}.")
                return []
            for record in trend_data:
                print(f"  Year: {record['year']}, Emission: {record['emission']:.2f} Mt")
            return trend_data
        else:
            print(f"No emission data found for '{country_name}'.")
            return []

    # --- 6. Insert New Emission Record ---
    def insert_new_emission_record(self, country: str, year: int, emission: float):
        """
        Adds a new data record (simulating real-time input) to the system.
        Updates both the country's linked list and the global yearly totals.
        Pushes the operation details to an undo stack to support rolling back this insertion.
        Time Complexity: O(Y_c) for linked list insertion (Y_c = years for country) in worst case.
                         O(1) average for hash table update (`global_yearly_totals`).
                         O(1) for pushing to stack.
        Space Complexity: O(1) for the new node and the stack entry.
        """
        print(f"\n--- Inserting New Record: Country='{country}', Year={year}, Emission={emission:.2f} Mt ---")
        
        # Get or create the EmissionLinkedList for the country
        if country not in self.country_emission_data:
            self.country_emission_data[country] = EmissionLinkedList()
            print(f"  New country '{country}' added to the system for insertion.")

        # Insert into the country's linked list
        self.country_emission_data[country].insert_chronologically(year, emission)

        # Update global_yearly_totals
        self.global_yearly_totals[year] = self.global_yearly_totals.get(year, 0.0) + emission

        # Push operation to undo stack
        # Storing (operation_type, country, year, emission)
        self.undo_stack.append(('insert', country, year, emission))
        print("  Record successfully inserted.")

    # --- 7. Undo Last Insertion ---
    def undo_last_insertion(self):
        """
        Rollbacks the last data insertion operation.
        Pops the last operation from the undo stack and reverses its effects on the data structures.
        Time Complexity: O(Y_c) for linked list removal (Y_c = years for country) in worst case.
                         O(1) average for hash table update (`global_yearly_totals`).
                         O(1) for popping from stack.
        Space Complexity: O(1) for popping from stack.
        """
        print("\n--- Attempting to Undo Last Insertion ---")
        if not self.undo_stack:
            print("  No operations to undo. Undo stack is empty.")
            return

        operation, country, year, emission = self.undo_stack.pop()

        if operation == 'insert':
            emission_list = self.country_emission_data.get(country)
            if emission_list:
                # Attempt to remove the node from the linked list
                if emission_list.remove_node(year, emission):
                    # If removal successful, update global totals
                    self.global_yearly_totals[year] = self.global_yearly_totals.get(year, 0.0) - emission
                    print(f"  Undone last insertion: Country='{country}', Year={year}, Emission={emission:.2f} Mt.")
                    
                    # Optional: If after removing, the country's list becomes empty, you could remove the country entry
                    # from the main hash table (self.country_emission_data) to save space.
                    # For simplicity, we keep the empty list here.
                else:
                    print(f"  Failed to undo insertion: Record (Year={year}, Emission={emission:.2f} Mt) not found in '{country}'s list. Undo stack might be out of sync.")
            else:
                print(f"  Failed to undo insertion: Country '{country}' not found in data structure. This indicates a data consistency issue.")
        else:
            print(f"  Unsupported undo operation type: '{operation}'. Only 'insert' undo is currently supported.")

# --- Main Execution for Demonstration ---
# Make sure the CSV file 'co2 Emission Africa (3).csv' is in the same directory as this Python script
# or provide the full path to the file.
file_path = r"co2 Emission Africa (3).csv" 

# 1. Initialize the EmissionAnalyzer system with the dataset
print("Initializing EmissionAnalyzer system...")
analyzer = EmissionAnalyzer(file_path)

# --- Demonstrating Required Operations and Complexities ---

# --- 1. Search Emissions by Country ---
print("\n" + "#"*5 + " 1. Demonstrating Search Emissions by Country " + "#"*5)
# Time Complexity: O(1) average (hash table lookup) + O(Y_c) (linked list traversal)
# Space Complexity: O(Y_c) for returned data
analyzer.search_emissions_by_country("Kenya")
analyzer.search_emissions_by_country("South Africa")
analyzer.search_emissions_by_country("Madagascar")
analyzer.search_emissions_by_country("NonExistentCountry") # Test for non-existent country

# --- 2. Total Emissions Per Year ---
print("\n" + "#"*5 + " 2. Demonstrating Total Emissions Per Year " + "#"*5)
# Time Complexity: O(1) average (hash table lookup)
# Space Complexity: O(1)
analyzer.get_total_emissions_per_year(2000)
analyzer.get_total_emissions_per_year(2020)
analyzer.get_total_emissions_per_year(1995) # Test for year with no data
analyzer.get_total_emissions_per_year(1900) # Test for year with no data

# --- 3. Top N Emitting Countries ---
print("\n" + "#"*5 + " 3. Demonstrating Top N Emitting Countries " + "#"*5)
# Time Complexity: O(C log N) (C = number of countries, N = top count)
# Space Complexity: O(N)
analyzer.get_top_n_emitting_countries(year=2020, n=5)
analyzer.get_top_n_emitting_countries(year=2010, n=3)
analyzer.get_top_n_emitting_countries(year=1990, n=2) # Test for year with no data
analyzer.get_top_n_emitting_countries(year=2020, n=100) # Test N larger than total countries
analyzer.get_top_n_emitting_countries(year=1800, n=5) # Test for year with no data

# --- 4. Emissions by Sector (Conceptual due to data limitation) ---
print("\n" + "#"*5 + " 4. Demonstrating Emissions by Sector (Conceptual) " + "#"*5)
# Time Complexity: O(N) (iterates through all N original records)
# Space Complexity: O(D_s) (number of distinct sectors)
analyzer.aggregate_emissions_by_sector() # This will show the error as no 'sector' column
# If a 'Sector' column existed in 'co2 Emission Africa (3).csv', you would call:
# analyzer.aggregate_emissions_by_sector(sector_column_name="Sector")

# --- 5. Emissions Trend for a Country ---
print("\n" + "#"*5 + " 5. Demonstrating Emissions Trend for a Country " + "#"*5)
# Time Complexity: O(1) average (hash table lookup) + O(Y_c) (linked list traversal)
# Space Complexity: O(Y_c)
analyzer.get_emissions_trend_for_country("Algeria")
analyzer.get_emissions_trend_for_country("Nigeria")
analyzer.get_emissions_trend_for_country("Somalia") # Test for countries with fewer records

# --- 6. Insert New Emission Record ---
print("\n" + "#"*5 + " 6. Demonstrating Insert New Emission Record " + "#"*5)
# Time Complexity: O(Y_c) (linked list insertion) + O(1) average (hash table updates)
# Space Complexity: O(1)
analyzer.insert_new_emission_record("Kenya", 2023, 55.75)
analyzer.insert_new_emission_record("New Test Country", 2015, 10.0) # Inserting a new country
analyzer.insert_new_emission_record("Kenya", 2024, 60.0) # Inserting another for Kenya to show chronological order

# Verify insertions (using search and total emission functions)
analyzer.search_emissions_by_country("Kenya")
analyzer.search_emissions_by_country("New Test Country")
analyzer.get_total_emissions_per_year(2023)
analyzer.get_total_emissions_per_year(2015)
analyzer.get_total_emissions_per_year(2024)

# --- 7. Undo Last Insertion ---
print("\n" + "#"*5 + " 7. Demonstrating Undo Last Insertion " + "#"*5)
# Time Complexity: O(Y_c) (linked list removal) + O(1) average (hash table updates)
# Space Complexity: O(1)
analyzer.undo_last_insertion() # Undoes Kenya 2024
analyzer.search_emissions_by_country("Kenya") # Check if 2024 is gone
analyzer.get_total_emissions_per_year(2024) # Check if total is updated (should be 0 or original value)

analyzer.undo_last_insertion() # Undoes New Test Country 2015
analyzer.search_emissions_by_country("New Test Country") # Check if New Test Country is gone
analyzer.get_total_emissions_per_year(2015) # Check if total is updated

analyzer.undo_last_insertion() # Undoes Kenya 2023
analyzer.search_emissions_by_country("Kenya") # Check if 2023 is gone
analyzer.get_total_emissions_per_year(2023) # Check if total is updated

analyzer.undo_last_insertion() # Should indicate no operations to undo
analyzer.undo_last_insertion() # Another attempt, still no operations to undo