import pandas as pd
from taipy.gui import Gui, notify
import taipy.gui.builder as tgb

# Load the new dataset
# file from: https://github.com/metatron-app/metatron-doc-discovery/blob/master/_static/data/sales-data-sample.csv
data = pd.read_csv("sales-data-sample.csv")

# Get unique values of each filter
regions = list(data["Region"].unique())
categories = list(data["Category"].unique())
segments = list(data["Segment"].unique())

# Layout configuration for the charts
layout = {
    "xaxis": {"title": ""},
    "yaxis": {"title": ""},
    "margin": {"l": 150},
}

# Function to handle filtering when the user selects new filters
def on_filter(state):
    # Check if any of the filters is empty, if yes the user gets notified
    if (len(state.regions) == 0 or len(state.categories) == 0 or len(state.segments) == 0):
        notify(state, "Error", "No results found. Change the filters.")
        return
    # Update the state with the filtered data
    state.data_filtered, state.sales_by_sub_category, state.sales_by_region = filter_data(state.regions, state.categories, state.segments)

# Function to filter the data based on user selections
def filter_data(regions, categories, segments):
    # Filter the data based on the selected regions, categories, and segments
    data_filtered = data[
        data["Region"].isin(regions)
        & data["Category"].isin(categories)
        & data["Segment"].isin(segments)
    ]

    # Calculate sales by sub-category, summing up the "Sales" for each sub-category, and sorting the results
    sales_by_sub_category = (
        data_filtered[["Sub_Category", "Sales"]]
        .groupby(by="Sub_Category")
        .sum()
        .sort_values(by="Sales", ascending=True)
        .reset_index()
    )

    # Calculate sales by region, summing up the "Sales" for each region
    sales_by_region = (
        data_filtered[["Region", "Sales"]]
        .groupby(by="Region")
        .sum()
        .reset_index()
    )

    # Return the filtered dataset, sales by sub-category, and sales by region
    return data_filtered, sales_by_sub_category, sales_by_region

# Function to format numbers with commas
def to_text(value):
    return "{:,}".format(int(value))

# Create the page layout with Taipy GUI
with tgb.Page() as page:
    # Toggle for theme settings
    tgb.toggle(theme="False")
    # Dashboard title
    tgb.text("📊 Sales Dashboard", class_name="h1 text-center pb2")

# Layout for the top metrics
    with tgb.layout("1 1 1", class_name="p1"):
        # Card for Total Sales
        with tgb.part(class_name="card"):
            tgb.text("### 💸 Total Sales", mode="md", class_name="text-center")
            tgb.text("📈 {to_text(data_filtered['Sales'].sum())}$", class_name="h4 text-center")

        # Card for Average Sales
        with tgb.part(class_name="card"):
            tgb.text("### 💸 Average Sales", mode="md", class_name="text-center")
            tgb.text("📈 {to_text(data_filtered['Sales'].mean())}$", class_name="h4 text-center")
        
        # Card for Average Profit Ratio
        with tgb.part(class_name="card"):
            tgb.text("### 💸 Average Profit Ratio", mode="md", class_name="text-center")
            tgb.text("📈 {round(data_filtered['ProfitRatio'].mean(), 1)}" + "%", class_name="h4 text-center")

    # Layout for the filter selectors
    with tgb.layout("1 1 1", class_name="p1"):
        # Selector for regions
        tgb.selector(
            value="{regions}",
            lov=regions,
            dropdown=True,
            multiple=True,
            label="Select regions",
            class_name="fullwidth",
            on_change=on_filter,
        )
        # Selector for categories
        tgb.selector(
            value="{categories}",
            lov=categories,
            dropdown=True,
            multiple=True,
            label="Select categories",
            class_name="fullwidth",
            on_change=on_filter,
        )
        # Selector for segments
        tgb.selector(
            value="{segments}",
            lov=segments,
            dropdown=True,
            multiple=True,
            label="Select segments",
            class_name="fullwidth",
            on_change=on_filter,
        )

# Layout for the charts
    with tgb.layout("1 1"):
        # Chart for Sales by Region
        tgb.chart(
            "{sales_by_region}",
            x="Region",
            y="Sales",
            type="bar",
            title="Sales by Region",
            layout=layout,
        )
        # Chart for Sales by Sub-Category
        tgb.chart(
            "{sales_by_sub_category}",
            x="Sales",
            y="Sub_Category",
            type="bar",
            orientation="h",
            layout=layout,
            title="Sales by Sub-Category",
        )

if __name__ == "__main__":
    # Initialize the filtered data with default values
    data_filtered, sales_by_sub_category, sales_by_region = filter_data(regions, categories, segments)
    # Run the GUI with the defined page layout
    Gui(page).run(title="Sales Dashboard", use_reloader=True, debug=True, watermark="", margin="4em")