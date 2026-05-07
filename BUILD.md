# Building `Dashboard.xlsm`

This repo contains the source code (VBA, Power Query M, DAX) for an Excel
dashboard that combines `.xlsx` files from a user-selected folder, loads
them into the Power Pivot data model, and exposes KPIs, charts, and a
drillable PivotTable.

The `.xlsm` workbook itself is binary and must be assembled in Excel using
the steps below.

## Prerequisites

- Microsoft 365 / Excel 2021+ (Power Query and Power Pivot fully supported)
- All source files share an identical schema and the same sheet name
- A sample folder with 1-3 source `.xlsx` files for testing

## Repository layout

```
Test1/
├── BUILD.md                  # this file
├── CLAUDE.md
├── vba/
│   └── modDashboard.bas      # VBA module: refresh button + folder picker
├── power-query/
│   ├── Parameters.pq         # fxSettings + fxFolder/fxSheetName/fxDateColumn
│   ├── SourceData.pq         # combine-from-folder query
│   └── DateTable.pq          # generated date dimension
└── dax/
    └── measures.dax          # measures for the data model
```

---

## Step 1 - Create the workbook skeleton

1. Open Excel and save a new file as `Dashboard.xlsm` (Excel Macro-Enabled
   Workbook).
2. Create three sheets, in this order: `Dashboard`, `Detail`, `Settings`.
3. On `Settings`, build a two-column table starting at `A1`:

   | Key        | Value                       |
   |------------|-----------------------------|
   | SheetName  | (your data sheet name)      |
   | DateColumn | (your date column header)   |
   | LastFolder | (leave blank, VBA fills it) |

4. Select `A1:B4`, press **Ctrl + T**, confirm "My table has headers".
5. With the table selected, on the **Table Design** tab set the **Table
   Name** to `tblSettings`.
6. Define three named ranges (Formulas > Name Manager > New) pointing at
   the cells in column B:
   - `SheetName`   -> `=Settings!$B$2`
   - `DateColumn`  -> `=Settings!$B$3`
   - `LastFolder`  -> `=Settings!$B$4`

---

## Step 2 - Build the Power Query queries

Open **Data > Get Data > Launch Power Query Editor**.

### 2a. `fxSettings` (helper)

1. **Home > New Source > Blank Query**.
2. **Home > Advanced Editor**, paste the `fxSettings` block from
   `power-query/Parameters.pq` (the first `let ... in ...`).
3. Rename the query `fxSettings`.
4. Right-click `fxSettings` in the Queries pane > **uncheck Enable load**.

### 2b. `fxFolder`, `fxSheetName`, `fxDateColumn`

For each of the three commented-out blocks in `power-query/Parameters.pq`:

1. **Home > New Source > Blank Query**.
2. **Advanced Editor**, paste the body (uncomment the lines first).
3. Name the query exactly `fxFolder`, `fxSheetName`, or `fxDateColumn`.
4. Disable load on each (right-click > uncheck Enable load).

### 2c. Define the parameters used by `SourceData`

`SourceData.pq` references identifiers `pFolder`, `pSheetName`, and
`pDateColumn`. The simplest wiring is to make these *queries* (not formal
parameter objects):

1. **Home > New Source > Blank Query** -> name it `pFolder` -> Advanced
   Editor:
   ```
   let Source = fxFolder in Source
   ```
2. Repeat for `pSheetName` (referencing `fxSheetName`) and `pDateColumn`
   (referencing `fxDateColumn`).
3. Disable load on all three.

### 2d. `SourceData`

1. **New Source > Blank Query** -> name `SourceData`.
2. Advanced Editor: paste the contents of `power-query/SourceData.pq`.
3. **Close & Load To...** -> select **Only Create Connection** AND check
   **Add this data to the Data Model**.

### 2e. `DateTable`

1. **New Source > Blank Query** -> name `DateTable`.
2. Advanced Editor: paste the contents of `power-query/DateTable.pq`.
3. **Close & Load To...** -> **Only Create Connection** + **Add this data
   to the Data Model**.

---

## Step 3 - Set up the data model in Power Pivot

1. **Power Pivot > Manage**.
2. Switch to **Diagram View**. Drag `SourceData[<your date column>]` onto
   `DateTable[Date]` to create the relationship.
3. Click `DateTable`, then **Design > Mark as Date Table**, choose `Date`.
4. Switch back to **Data View**, select `SourceData`.
5. Open `dax/measures.dax`. For each measure block, paste it into the
   Calculation Area below the `SourceData` table. Replace `<Amount>` with
   your actual numeric column name before committing each measure.
6. Set the format of each measure (right-click measure > Format) per the
   hints at the bottom of `measures.dax`.

---

## Step 4 - Build the dashboard visuals

On the `Dashboard` sheet:

1. **Insert > PivotTable > From Data Model**. Place 4 small PivotTables
   for KPI cards (Total, Record Count, Average, YTD). Format each as a
   single big number with a label above.
2. **Insert > PivotChart > From Data Model**:
   - Trend chart (line): Axis = `DateTable[YearMonth]`, Values = `[Total]`
   - Category chart (bar): Axis = a dimension from `SourceData`,
     Values = `[Total]`
3. **Insert > Slicer**: connect at minimum
   - `DateTable[Year]`, `DateTable[Quarter]`, `DateTable[MonthName]`
   - One or two dimension slicers from `SourceData`
4. Connect every slicer to all PivotTables/PivotCharts on the sheet
   (Slicer tab > Report Connections).

On the `Detail` sheet:

1. Insert a single PivotTable from the data model with rows/columns/values
   wired up for ad-hoc exploration. Connect it to the same slicers if
   helpful.

---

## Step 5 - Add the VBA refresh button

1. **Developer > Visual Basic** (Alt+F11).
2. **File > Import File...** -> select `vba/modDashboard.bas`.
3. Save and return to Excel.
4. On `Dashboard`: **Developer > Insert > Button (Form Control)**.
5. Draw the button, assign macro `RefreshDashboard`, label it "Refresh".

---

## Step 6 - Test

1. Click **Refresh**. Pick the folder containing your sample `.xlsx`
   files.
2. Confirm the data model populates and the dashboard updates.
3. Drop another file into the folder and click **Refresh** again -
   the new rows should appear without any other action.
4. Save `Dashboard.xlsm`.

---

## Troubleshooting

- **"LastFolder not set"** - first run will write the folder path; if
  you're seeing this on a clean workbook, make sure `tblSettings` has
  the `LastFolder` row.
- **Dates show as text** - confirm the `DateColumn` value in `Settings`
  exactly matches the header in your source files (case-sensitive).
- **Sheet not found** - the Power Query filters strictly on
  `pSheetName`; check the value in `Settings` and ensure every source
  file has that sheet.
- **Workbook bloats** - confirm `SourceData` is **Connection Only +
  Data Model**, not also loaded to a worksheet.
