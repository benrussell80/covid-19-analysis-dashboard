# case reports
import datetime

from bokeh.models import DataTable, TableColumn, Panel, HTMLTemplateFormatter
from bokeh.layouts import row, column
from bokeh.plotting import figure

from sources import get_line_list_data


def create_case_details_tab():
    "Factory for creating 5th tab."

    ## Data Sources
    source_df, source_CDS = get_line_list_data()

    ## Data Table
    link_template = """<a href="<%= value %>">Link</a>"""
    overflow_paragraph_template = f"""<p style="overflow: auto; white-space: pre-wrap; padding: 0; margin: 0; height: 100%; width: inherit;"><%= value %></p>"""

    data_table_columns = [
        TableColumn(field="country", title="Country", width=150),
        TableColumn(field="location", title="Location", formatter=HTMLTemplateFormatter(template=overflow_paragraph_template), width=150),
        TableColumn(field="link", title="Link", formatter=HTMLTemplateFormatter(template=link_template), width=50),
        TableColumn(field="age", title="Age", width=50),
        TableColumn(field="gender", title="Gender", width=100),
        TableColumn(field="reporting_date", title="Reporting Date", width=200),
        TableColumn(field="summary", title="Summary", formatter=HTMLTemplateFormatter(template=overflow_paragraph_template), width=450),
        TableColumn(field="exposure_start", title="Exposure Start", width=200),
        TableColumn(field="exposure_end", title="Exposure End", width=200),
        TableColumn(field="symptoms", title="Symptoms", formatter=HTMLTemplateFormatter(template=overflow_paragraph_template), width=150),
        TableColumn(field="symptom_onset", title="Symptom Onset", width=250),
        TableColumn(field="from_wuhan", title="From Wuhan", width=150),
        TableColumn(field="visiting_wuhan", title="Visiting Wuhan", width=200),
        TableColumn(field="recovered", title="Recovered", width=150),
        TableColumn(field="recovered_date", title="Recovery Date", width=200),
        TableColumn(field="death", title="Death", width=100),
        TableColumn(field="death_date", title="Death Date", width=150),
    ]

    data_table = DataTable(
        columns=data_table_columns,
        source=source_CDS,
        row_height=100,
        sizing_mode='scale_both'
    )

    child = row([data_table])

    return Panel(child=child, title="Case Details")