// SourceData
// ---------------------------------------------------------------------------
// Combines all .xlsx files in the user-selected folder, keeping only the
// sheet whose name matches the pSheetName parameter. Promotes headers and
// loads the result to the Data Model.
//
// Parameters required (set up via Home > Manage Parameters in Power Query):
//   pFolder      (Text) - reads from Settings!LastFolder
//   pSheetName   (Text) - reads from Settings!SheetName
//   pDateColumn  (Text) - reads from Settings!DateColumn
//
// The "reads from Settings" wiring is done with three small queries
// (fxFolder, fxSheetName, fxDateColumn) that pull from the Settings table.
// See Parameters.pq.
//
// Load destination: Data Model only (uncheck "Load to worksheet").
// ---------------------------------------------------------------------------
let
    Source = Folder.Files(pFolder),

    OnlyXlsx = Table.SelectRows(
        Source,
        each [Extension] = ".xlsx"
            and not Text.StartsWith([Name], "~$")
            and not Text.StartsWith([Name], ".")
    ),

    AddWorkbook = Table.AddColumn(
        OnlyXlsx,
        "Workbook",
        each Excel.Workbook([Content], true),
        type table
    ),

    KeepWorkbookCols = Table.SelectColumns(AddWorkbook, {"Name", "Workbook"}),

    ExpandSheets = Table.ExpandTableColumn(
        KeepWorkbookCols,
        "Workbook",
        {"Name", "Data", "Kind"},
        {"SheetName", "Data", "Kind"}
    ),

    OnlyTargetSheet = Table.SelectRows(
        ExpandSheets,
        each [Kind] = "Sheet" and [SheetName] = pSheetName
    ),

    CombinedRaw = Table.Combine(OnlyTargetSheet[Data]),

    Promoted = Table.PromoteHeaders(CombinedRaw, [PromoteAllScalars = true]),

    // Coerce the configured date column to type date.
    // Other columns stay as-is (auto-detect happens in subsequent steps if needed).
    Typed = Table.TransformColumnTypes(
        Promoted,
        {{pDateColumn, type date}}
    ),

    RemoveBlankRows = Table.SelectRows(
        Typed,
        each not List.IsEmpty(
            List.RemoveMatchingItems(Record.FieldValues(_), {"", null})
        )
    )
in
    RemoveBlankRows
